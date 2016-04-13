# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-17 15:13
from __future__ import unicode_literals

from django.db import migrations, models
import gendoc.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeneratedDocumentTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024, verbose_name='\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435')),
                ('active', models.BooleanField(default=True, verbose_name='\u0410\u043a\u0442\u0438\u0432\u043d\u044b\u0439')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='\u0412\u0440\u0435\u043c\u044f \u043c\u043e\u0434\u0438\u0444\u0438\u043a\u0430\u0446\u0438\u0438')),
                ('template_file', models.FileField(upload_to=gendoc.models.gdt_upload, verbose_name='\u0424\u0430\u0439\u043b')),
            ],
        ),
    ]
