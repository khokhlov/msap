# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-05-18 10:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0016_auto_20161007_0755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mailing',
            name='test_email',
            field=models.CharField(blank=True, max_length=2014, null=True, verbose_name='\u0422\u0435\u0441\u0442\u043e\u0432\u044b\u0439 e-mail'),
        ),
    ]
