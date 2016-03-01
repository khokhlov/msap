# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-01 11:13
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0008_coursetask_short_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursetasksolution',
            name='hand_flag',
            field=models.BooleanField(default=False, verbose_name='\u0412\u044b\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u043e\u0442\u043c\u0435\u0442\u043a\u0443 \u0432\u0440\u0443\u0447\u043d\u0443\u044e'),
        ),
        migrations.AddField(
            model_name='coursetasksolution',
            name='hand_score',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='\u0420\u0443\u0447\u043d\u0430\u044f \u043e\u0442\u043c\u0435\u0442\u043a\u0430'),
        ),
    ]