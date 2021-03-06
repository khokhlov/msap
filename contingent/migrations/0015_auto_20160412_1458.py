# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-04-12 14:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contingent', '0014_scientificmanagement'),
    ]

    operations = [
        migrations.RenameField(
            model_name='scientificmanagement',
            old_name='superviser',
            new_name='supervisor',
        ),
        migrations.AlterField(
            model_name='scientificmanagement',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervisors', to='contingent.Student', verbose_name='\u0421\u0442\u0443\u0434\u0435\u043d\u0442'),
        ),
    ]
