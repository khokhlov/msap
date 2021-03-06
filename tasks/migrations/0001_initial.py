# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-01 10:08
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseSolution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('date_modification', models.DateTimeField(auto_now=True, null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043c\u043e\u0434\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438')),
                ('score', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='\u041e\u0442\u043c\u0435\u0442\u043a\u0430')),
                ('status', models.IntegerField(default=-1, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441')),
            ],
            options={
                'ordering': ['date_creation'],
            },
        ),
        migrations.CreateModel(
            name='BaseTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('text', models.TextField(blank=True, verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
                ('ans', models.TextField(blank=True, verbose_name='\u041e\u0442\u0432\u0435\u0442')),
                ('score_min', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u043e\u0442\u043c\u0435\u0442\u043a\u0430 \u0437\u0430 \u0437\u0430\u0434\u0430\u0447\u0443')),
                ('score_max', models.DecimalField(decimal_places=2, default=Decimal('10.00'), max_digits=5, verbose_name='\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u043e\u0442\u043c\u0435\u0442\u043a\u0430 \u0437\u0430 \u0437\u0430\u0434\u0430\u0447\u0443')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('date_modification', models.DateTimeField(auto_now=True, null=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043c\u043e\u0434\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TextSolution',
            fields=[
                ('basesolution_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tasks.BaseSolution')),
                ('text', models.TextField(verbose_name='\u041e\u0442\u0432\u0435\u0442')),
            ],
            options={
                'verbose_name': '\u0422\u0435\u043a\u0442\u043e\u0432\u044b\u0439 \u043e\u0442\u0432\u0435\u0442',
            },
            bases=('tasks.basesolution',),
        ),
        migrations.CreateModel(
            name='TextTask',
            fields=[
                ('basetask_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tasks.BaseTask')),
            ],
            options={
                'verbose_name': '\u0422\u0435\u043a\u0442\u043e\u0432\u0430\u044f \u0437\u0430\u0434\u0430\u0447\u0430',
            },
            bases=('tasks.basetask',),
        ),
        migrations.AddField(
            model_name='basesolution',
            name='checker',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='checker_solutions', to=settings.AUTH_USER_MODEL, verbose_name='\u041a\u0442\u043e \u043f\u0440\u043e\u0432\u0435\u0440\u0438\u043b'),
        ),
        migrations.AddField(
            model_name='basesolution',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to='tasks.BaseTask', verbose_name='\u0417\u0430\u0434\u0430\u0447\u0430'),
        ),
        migrations.AddField(
            model_name='basesolution',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to=settings.AUTH_USER_MODEL, verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c'),
        ),
    ]
