# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-01 13:02
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contingent', '0007_teacher'),
        ('training', '0010_course_auto_check_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score_min', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='\u041c\u0438\u043d\u0438\u043c\u0443\u043c')),
                ('score_max', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='\u041c\u0430\u043a\u0441\u0438\u043c\u0443\u043c')),
                ('score_auto', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='\u0410\u0432\u0442\u043e-\u043e\u0446\u0435\u043d\u043a\u0430')),
                ('score_final', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='\u0424\u0438\u043d\u0430\u043b\u044c\u043d\u0430\u044f \u043e\u0442\u043c\u0435\u0442\u043a\u0430')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='training.Course', verbose_name='\u041a\u0443\u0440\u0441')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contingent.Student', verbose_name='\u0421\u0442\u0443\u0434\u0435\u043d\u0442')),
            ],
        ),
    ]