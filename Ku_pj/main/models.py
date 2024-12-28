# models.py
from django.db import models

class Expert(models.Model):
    name = models.CharField(max_length=100)
    weight = models.FloatField(default=0.1)

    def __str__(self):
        return self.name

class Criterion(models.Model):
    name = models.CharField(max_length=100)
    max_value = models.FloatField(null=True, blank=True)
    min_value = models.FloatField(null=True, blank=True)
    importance = models.FloatField(null=True, blank=True)
    preference_type = models.CharField(max_length=10,
                                       choices=[('max', 'Лучше наибольший'), ('min', 'Лучше наименьший')],
                                       default='max')
    def __str__(self):
        return self.name


class Alternative(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Score(models.Model):
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)
    alternative = models.ForeignKey(Alternative, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    value = models.FloatField()

    def __str__(self):
        return f"{self.alternative} - {self.criterion}: {self.value} (Expert: {self.expert})"
