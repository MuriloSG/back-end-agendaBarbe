# Generated by Django 4.2.19 on 2025-03-22 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_timeslot_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workday',
            name='day_of_week',
            field=models.CharField(blank=True, choices=[('monday', 'Segunda-feira'), ('tuesday', 'Terça-feira'), ('wednesday', 'Quarta-feira'), ('thursday', 'Quinta-feira'), ('friday', 'Sexta-feira'), ('saturday', 'Sábado'), ('sunday', 'Domingo')], max_length=10, null=True),
        ),
    ]
