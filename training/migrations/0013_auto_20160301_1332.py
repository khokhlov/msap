# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-01 13:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0012_course_auto_check_flag'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coursetask',
            options={'ordering': ['num']},
        ),
        migrations.AddField(
            model_name='coursetask',
            name='num',
            field=models.IntegerField(default=0, verbose_name='\u041d\u043e\u043c\u0435\u0440 \u0437\u0430\u0434\u0430\u0447\u0438 \u0432 \u043a\u0443\u0440\u0441\u0435 (\u0434\u043b\u044f \u0441\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u043a\u0438 \u0438 \u0430\u0432\u0442\u043e \u043e\u0442\u043c\u0435\u0442\u043a\u0438)'),
        ),
    ]
