# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-16 11:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0012_mailing_notification_redirect'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailingstatus',
            name='redirect_url',
            field=models.TextField(blank=True, default='', null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u0434\u043b\u044f \u0440\u0435\u0434\u0438\u0440\u0435\u043a\u0442\u0430'),
        ),
    ]
