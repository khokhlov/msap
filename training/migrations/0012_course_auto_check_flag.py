# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-01 13:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0011_coursescore'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='auto_check_flag',
            field=models.BooleanField(default=False, verbose_name='\u0410\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0430\u044f \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0430'),
        ),
    ]
