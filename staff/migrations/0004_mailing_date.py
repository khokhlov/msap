# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-15 12:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_auto_20160215_1214'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailing',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 2, 15, 12, 16, 56, 387673, tzinfo=utc), verbose_name='\u0414\u0430\u0442\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f'),
            preserve_default=False,
        ),
    ]