# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-17 10:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contingent', '0010_auto_20160317_1025'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmploymentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('short_name', models.CharField(blank=True, max_length=256, null=True, verbose_name='\u041a\u0440\u0430\u0442\u043d\u043e\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
            ],
        ),
    ]
