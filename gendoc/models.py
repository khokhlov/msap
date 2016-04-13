#coding: utf-8

from __future__ import unicode_literals

import sys

from django.db import models
from django.conf import settings
from django.utils.encoding import smart_text

import md5
import datetime
import json
import importlib

from reversion import revisions as reversion

UserModel = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

def class_for_name(module_name, class_name):
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    print m
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c

def gdt_upload(instance, filename):
    h = md5.md5('%s_%s' % (datetime.datetime.now(), filename)).hexdigest()
    return 'generated_documents/templates/%s_%s' % (h, filename)

class GeneratedDocumentProcessor(models.Model):
    name = models.CharField(max_length=1024, verbose_name = u'Название')
    clazz = models.CharField(max_length=1024, verbose_name = u'Класс')
    
    def __unicode__(self):
        return self.name

@reversion.register()
class GeneratedDocumentTemplate(models.Model):
    name = models.CharField(max_length=1024, verbose_name = u'Название')
    active = models.BooleanField(default = True, verbose_name = u'Активный')
    created = models.DateTimeField(auto_now_add = True, verbose_name = u'Время создания')
    modified = models.DateTimeField(auto_now=True, verbose_name = u'Время модификации')
    template_file = models.FileField(upload_to = gdt_upload, verbose_name = u'Файл')
    processor = models.ForeignKey(GeneratedDocumentProcessor, blank = True, null = True, verbose_name = u'Генератор документа')
    template_info = models.TextField(null = True, blank = True, verbose_name = u'Информация о документе')
    
    def __unicode__(self):
        return self.name
    
    def get_processor(self):
        cn = self.processor.clazz
        cn1 = cn[:cn.rfind('.')]
        cn2 = cn[cn.rfind('.')+1:]
        p = class_for_name(cn1, cn2)()
        p.load_template(self.template_file.path)
        return p
    
    def clean(self):
        p = self.get_processor()
        self.template_info = smart_text(json.dumps(p.get_vars(), indent = 4))
    



def gd_upload(instance, filename):
    return 'generated_documents/templates/%s_%s' % (instance.user.pk, filename)

class GeneratedDocument(models.Model):
    template = models.ForeignKey(GeneratedDocumentTemplate, verbose_name = u'Шаблон')
    user     = models.ForeignKey(UserModel, verbose_name = u'Пользователь')
    creator  = models.ForeignKey(UserModel, verbose_name = u'Создатель', related_name = 'creator_generated_documents')
    created = models.DateTimeField(auto_now_add = True, verbose_name = u'Время создания')
    doc_file = models.FileField(upload_to = gd_upload, verbose_name = u'Файл')
    
    def __unicode__(self):
        return u'%s (%s)' % (self.template.name, self.user)
