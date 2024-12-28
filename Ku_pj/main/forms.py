# forms.py
from django import forms
from .models import Criterion, Alternative, Score, Expert

class CriterionForm(forms.ModelForm):
    max_value = forms.FloatField(required=False, label='Максимальное значение')
    min_value = forms.FloatField(required=False, label='Минимальное значение')

    class Meta:
        model = Criterion
        fields = ['name', 'preference_type', 'importance', 'max_value', 'min_value']


class AlternativeForm(forms.ModelForm):
    class Meta:
        model = Alternative
        fields = ['name']


class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        fields = ['value']


class ExpertForm(forms.ModelForm):
    class Meta:
        model = Expert
        fields = ['name', 'weight']  # Поля для имени и веса эксперта
