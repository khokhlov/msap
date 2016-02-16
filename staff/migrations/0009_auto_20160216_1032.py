# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-16 10:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_auto_20160215_1321'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailingStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('received', models.BooleanField(default=False, verbose_name='\u041f\u043e\u043b\u0443\u0447\u0435\u043d\u043e')),
            ],
        ),
        migrations.AddField(
            model_name='mailing',
            name='with_notification',
            field=models.BooleanField(default=False, verbose_name='\u0421 \u0443\u0432\u0435\u0434\u043e\u043c\u043b\u0435\u043d\u0438\u044f\u043c\u0438'),
        ),
        migrations.AddField(
            model_name='mailingstatus',
            name='mailing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statuses', to='staff.Mailing', verbose_name='\u0420\u0430\u0441\u0441\u044b\u043b\u043a\u0430'),
        ),
        migrations.AddField(
            model_name='mailingstatus',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mailing_statuses', to='staff.Mailing', verbose_name='\u041f\u043e\u043b\u0443\u0447\u0430\u0442\u0435\u043b\u044c'),
        ),
    ]
