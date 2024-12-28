from django.shortcuts import render, redirect
from .models import Criterion, Alternative, Score, Expert
from .forms import CriterionForm, AlternativeForm, ScoreForm, ExpertForm

def home(request):
    # Очистка базы данных
    Score.objects.all().delete()
    Criterion.objects.all().delete()
    Alternative.objects.all().delete()
    Expert.objects.all().delete()  # Очищаем таблицу экспертов

    return render(request, 'home.html')


def set_counts(request):
    if request.method == 'POST':
        num_alternatives = int(request.POST['num_alternatives'])
        num_criteria = int(request.POST['num_criteria'])
        num_experts = int(request.POST['num_experts'])  # Получаем количество экспертов

        request.session['num_alternatives'] = num_alternatives
        request.session['num_criteria'] = num_criteria
        request.session['num_experts'] = num_experts  # Сохраняем количество экспертов в сессии

        return redirect('add_experts')

    return render(request, 'set_counts.html')


def add_experts(request):
    num_experts = request.session.get('num_experts', 0)

    if request.method == 'POST':
        forms = []
        total_weight = 0.0  # Переменная для хранения суммы весов

        # Сбор форм и вычисление общей суммы весов
        for i in range(num_experts):
            form = ExpertForm(request.POST, prefix=f'expert_{i}')
            if form.is_valid():
                expert_instance = form.save(commit=False)  # Не сохраняем пока
                total_weight += expert_instance.weight  # Добавляем вес к общей сумме
                forms.append(expert_instance)  # Сохраняем экземпляр эксперта для последующего сохранения
            else:
                forms.append(form)  # Если форма не валидна, добавляем ее в список

        # Проверка на сумму весов
        if total_weight != 1:
            return render(request, 'error.html', {
                'message': f'Сумма весов всех экспертов должна быть равна 1. Текущая сумма: {total_weight:.2f}.'
            })

        # Если все формы валидны и сумма весов равна 1, сохраняем всех экспертов
        for expert in forms:
            expert.save()

        return redirect('add_criterion')

    forms = [ExpertForm(prefix=f'expert_{i}') for i in range(num_experts)]

    return render(request, 'add_expert.html', {'forms': forms})

def add_criterion(request):
    num_criteria = request.session.get('num_criteria', 0)
    range_criteria = list(range(num_criteria))

    if request.method == 'POST':
        forms = []
        valid = True

        # Список для хранения созданных критериев
        criteria_instances = []

        for i in range(num_criteria):
            form = CriterionForm(request.POST, prefix=f'criterion_{i}')
            forms.append(form)

            if form.is_valid():
                importance = form.cleaned_data['importance']
                if importance < 0 or importance > 10:
                    return render(request, 'error.html', {
                        'message': f'Важность {importance} для критерия выходит за пределы допустимых значений (0 - 10).'
                    })

                # Создаем экземпляр критерия без сохранения в БД
                criterion_instance = form.save(commit=False)
                criterion_instance.importance = importance

                # Получаем max и min значения из POST-запроса
                max_value = request.POST.get(f'max_{i}')
                min_value = request.POST.get(f'min_{i}')

                # Сохраняем max и min значения, если они указаны
                if max_value:
                    criterion_instance.max_value = float(max_value)
                if min_value:
                    criterion_instance.min_value = float(min_value)

                # Сохраняем экземпляр критерия в БД
                criterion_instance.save()
                criteria_instances.append(criterion_instance)  # Добавляем созданный экземпляр в список

            else:
                valid = False

        if valid:
            return redirect('add_alternative')

    else:
        forms = [CriterionForm(prefix=f'criterion_{i}') for i in range(num_criteria)]

    return render(request, 'add_criterion.html', {'forms': forms})



def add_alternatives(request):
    num_alternatives = request.session.get('num_alternatives', 0)

    if request.method == 'POST':
        for i in range(num_alternatives):
            form = AlternativeForm(request.POST, prefix=f'alternative_{i}')
            if form.is_valid():
                form.save()

        return redirect('input_scores')

    forms = [AlternativeForm(prefix=f'alternative_{i}') for i in range(num_alternatives)]

    return render(request, 'add_alternative.html', {'forms': forms})


def input_scores(request):
    num_alternatives = request.session.get('num_alternatives', 0)
    num_criteria = request.session.get('num_criteria', 0)

    alternatives_list = list(Alternative.objects.values_list('name', flat=True))
    alternatives = Alternative.objects.all()
    criteria = list(Criterion.objects.all())

    min_values = {criterion.id: criterion.min_value for criterion in criteria}
    max_values = {criterion.id: criterion.max_value for criterion in criteria}

    indices = list(range(1, len(alternatives_list) + 1))
    range_criteria = list(range(num_criteria))

    # Получаем текущего эксперта из сессии
    current_expert_index = request.session.get('current_expert_index', 0)
    experts = Expert.objects.all()  # Получаем всех экспертов

    if request.method == 'POST':
        # Сохраняем оценки для текущего эксперта
        for i in indices:
            for j in range_criteria:


                score_value = request.POST.get(f'score_{i}_{j}')

                if score_value:
                    score_value_float = float(score_value)
                    alternative_instance = alternatives[i - 1]
                    criterion_instance = criteria[j]

                    min_value_float = criterion_instance.min_value
                    max_value_float = criterion_instance.max_value

                    # Проверяем, находятся ли score_value в допустимом диапазоне
                    if score_value_float < min_value_float or score_value_float > max_value_float:
                        return render(request, 'error.html', {
                            'message': f'Оценка {score_value_float} для альтернативы {alternative_instance.name} по критерию {criterion_instance.name} выходит за пределы допустимых значений ({min_value_float} - {max_value_float}).'
                        })



                    # Создаем или обновляем оценку
                    Score.objects.update_or_create(
                        alternative=alternative_instance,
                        criterion=criterion_instance,
                        expert=experts[current_expert_index],
                        defaults={'value': score_value_float}
                    )

        # Переходим к следующему эксперту
        current_expert_index += 1

        if current_expert_index < len(experts):
            request.session['current_expert_index'] = current_expert_index
            return redirect('input_scores')  # Перезагружаем страницу для следующего эксперта
        else:
            del request.session['current_expert_index']  # Удаляем сессию, если все эксперты оценили

            # Сохраняем нормированные значения важности
            total_importance = sum(criterion.importance for criterion in criteria if criterion.importance is not None)
            if total_importance > 0:
                for criterion in criteria:
                    normalized_importance = round(criterion.importance / total_importance, 2) if criterion.importance else 0
                    criterion.importance = normalized_importance
                    criterion.save()

            return redirect('calculate_distances')  # Переход к следующему шагу

    return render(request, 'input_scores.html', {
        'alternatives': alternatives_list,
        'criteria': criteria,
        'num_alternatives': num_alternatives,
        'num_criteria': num_criteria,
        'indices': indices,
        'range_criteria': range_criteria,
        'current_expert': experts[current_expert_index] if experts else None,  # Текущий эксперт
    })


def calculate_distances(request):
    scores = Score.objects.all()
    criteria = Criterion.objects.all()
    experts = Expert.objects.all()

    min_values = {criterion.id: criterion.min_value for criterion in criteria}
    max_values = {criterion.id: criterion.max_value for criterion in criteria}

    importance_values = [criterion.importance for criterion in criteria]
    indices_scores = list(range(len(criteria)))  # Индексы критериев

    # Словарь для хранения обобщенных оценок
    aggregated_scores = {
        alternative.id: {criterion.id: 0 for criterion in criteria}
        for alternative in Alternative.objects.all()
    }

    # Словарь для хранения значений согласованности
    consistency_scores = {
        alternative.id: {criterion.id: 0 for criterion in criteria}
        for alternative in Alternative.objects.all()
    }

    # Вычисляем обобщенные оценки по каждому критерию для каждой альтернативы
    for score in scores:
        alternative_id = score.alternative.id
        criterion_id = score.criterion.id
        expert_weight = score.expert.weight
        score_value = score.value

        # Обновляем обобщенные оценки
        aggregated_scores[alternative_id][criterion_id] += score_value * expert_weight

    # Расчет согласованности экспертов и коэффициента вариации
    for criterion in criteria:
        for alternative_id in aggregated_scores.keys():
            aggregated_score = aggregated_scores[alternative_id][criterion.id]

            if aggregated_score > 0:  # Избегаем деления на ноль
                cv_sum = 0  # Инициализация суммы для CV

                # Сбор всех оценок для текущей альтернативы и критерия
                expert_values = scores.filter(criterion=criterion, alternative__id=alternative_id)

                for expert_score in expert_values:
                    expert_value = expert_score.value
                    expert_weight = expert_score.expert.weight

                    # Расчет согласованности
                    cv_sum += expert_weight * ((expert_value - aggregated_score) ** 2)

                # Коэффициент вариации
                cv = (cv_sum ** 0.5 / aggregated_score) * 100
                consistency_scores[alternative_id][criterion.id] = round(cv, 2)


    distances = []
    aggregated_scores_list = []
    winning_alternative = None
    max_distance = float('inf')

    for alternative_id, scores_dict in aggregated_scores.items():
        alternative_instance = Alternative.objects.get(id=alternative_id)
        norm_scores = []
        cv_scores = []  # Список для хранения коэффициентов вариации

        for criterion in criteria:
            if criterion.id in scores_dict:
                score_value = scores_dict[criterion.id]

                # Нормализация
                if max_values[criterion.id] is not None and min_values[criterion.id] is not None:
                    if criterion.preference_type == 'max':
                        norm_score = (score_value - min_values[criterion.id]) / (max_values[criterion.id] - min_values[criterion.id])
                    else:
                        norm_score = (max_values[criterion.id] - score_value) / (max_values[criterion.id] - min_values[criterion.id])

                    norm_scores.append(round(norm_score, 2))


        # Расчет расстояния до идеальной точки
        distance = (sum(importance_values[i] * (1 - norm_scores[i]) ** 2 for i in range(len(norm_scores))) ** 0.5)

        if distance < max_distance:
            max_distance = distance
            winning_alternative = alternative_instance.name

        distances.append({
            'alternative': alternative_instance,
            'distance': round(distance, 2),
            'normalized_scores': norm_scores,
            'consistency_scores': [round(consistency_scores[alternative_id][criterion.id], 2) for criterion in criteria]
        })

        # Добавляем данные для таблицы обобщенных оценок
        aggregated_scores_list.append({
            'alternative': alternative_instance,
            'scores': [round(score, 2) for score in scores_dict.values()],
        })

    return render(request, 'calculate_distances.html', {
        'distances': distances,
        'aggregated_scores_list': aggregated_scores_list,
        'criteria': criteria,
        'winning_alternative': winning_alternative,
        'max_distance': round(max_distance, 2),
        'indices_scores': list(range(len(criteria))),
    })





