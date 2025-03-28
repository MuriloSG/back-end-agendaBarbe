# Generated by Django 4.2.19 on 2025-03-02 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workday',
            name='end_time',
            field=models.TimeField(blank=True, help_text='Hora de fim do expediente', null=True),
        ),
        migrations.AddField(
            model_name='workday',
            name='lunch_end_time',
            field=models.TimeField(blank=True, help_text='Hora de fim do almoço', null=True),
        ),
        migrations.AddField(
            model_name='workday',
            name='lunch_start_time',
            field=models.TimeField(blank=True, help_text='Hora de início do almoço', null=True),
        ),
        migrations.AddField(
            model_name='workday',
            name='start_time',
            field=models.TimeField(blank=True, help_text='Hora de início do expediente', null=True),
        ),
    ]
