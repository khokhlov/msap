# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-16 11:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0010_auto_20160216_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailingstatus',
            name='slug',
            field=models.SlugField(default='q', verbose_name='\u041a\u043e\u0434'),
            preserve_default=False,
        ),
    ]
