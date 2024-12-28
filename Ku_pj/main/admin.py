from django.contrib import admin
from .models import Alternative, Criterion, Score, Expert

class ExpertAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')  # Укажите поля для отображения в списке

class AlternativeAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Укажите поля для отображения в списке

class CriterionAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_value', 'min_value', "preference_type", 'importance')

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('alternative', 'criterion', 'value', 'expert')  # Указываем существующие поля

admin.site.register(Alternative, AlternativeAdmin)
admin.site.register(Criterion, CriterionAdmin)
admin.site.register(Score, ScoreAdmin)
admin.site.register(Expert, ExpertAdmin)

