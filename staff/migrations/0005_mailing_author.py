# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-15 12:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_mailing_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailing',
            name='author',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u041e\u0442\u043f\u0440\u0430\u0432\u0438\u0442\u0435\u043b\u044c'),
            preserve_default=False,
        ),
    ]
