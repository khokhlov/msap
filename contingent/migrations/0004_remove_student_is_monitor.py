# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-12 14:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contingent', '0003_student_is_monitor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='is_monitor',
        ),
    ]
