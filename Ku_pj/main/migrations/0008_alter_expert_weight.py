# Generated by Django 5.0.6 on 2024-12-18 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_expert_weight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expert',
            name='weight',
            field=models.FloatField(default=0.1),
        ),
    ]
