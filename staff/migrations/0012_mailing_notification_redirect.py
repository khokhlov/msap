# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-16 11:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0011_mailingstatus_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailing',
            name='notification_redirect',
            field=models.TextField(blank=True, null=True, verbose_name='\u0421\u0441\u044b\u043b\u043a\u0430 \u0434\u043b\u044f \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f'),
        ),
    ]
