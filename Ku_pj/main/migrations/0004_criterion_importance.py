# Generated by Django 5.0.6 on 2024-12-13 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_criterion_max_value_criterion_min_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='criterion',
            name='importance',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
