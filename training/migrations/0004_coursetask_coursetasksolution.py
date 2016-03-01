# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-01 10:26
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contingent', '0007_teacher'),
        ('tasks', '0002_basetask_author'),
        ('training', '0003_courseprogramm_creatos'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deadline_start', models.DateTimeField(blank=True, null=True, verbose_name='\u041d\u0430\u0447\u0430\u043b\u043e \u0441\u0434\u0430\u0447\u0438')),
                ('deadline_end', models.DateTimeField(blank=True, null=True, verbose_name='\u041e\u043a\u043e\u043d\u0447\u0430\u043d\u0438\u0435 \u0441\u0434\u0430\u0447\u0438')),
                ('score_min', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='\u041c\u0438\u043d\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u043e\u0442\u043c\u0435\u0442\u043a\u0430 \u0437\u0430 \u0437\u0430\u0434\u0430\u0447\u0443')),
                ('score_max', models.DecimalField(decimal_places=2, default=Decimal('1.00'), max_digits=5, verbose_name='\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u043e\u0442\u043c\u0435\u0442\u043a\u0430 \u0437\u0430 \u0437\u0430\u0434\u0430\u0447\u0443')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.BaseTask', verbose_name='\u041e\u043f\u0438\u0441\u0430\u043d\u0438\u0435')),
            ],
        ),
        migrations.CreateModel(
            name='CourseTaskSolution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('solutions', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.BaseSolution', verbose_name='\u0420\u0435\u0448\u0435\u043d\u0438\u0435')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contingent.Student', verbose_name='\u0421\u0442\u0443\u0434\u0435\u043d\u0442')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='training.CourseTask', verbose_name='\u0417\u0430\u0434\u0430\u0447\u0430')),
            ],
        ),
    ]
