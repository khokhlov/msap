#coding: utf-8

from __future__ import unicode_literals

from decimal import Decimal

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

class InheritanceCastModel(models.Model):
    """
    An abstract base class that provides a ``real_type`` FK to ContentType.

    For use in trees of inherited models, to be able to downcast
    parent instances to their child types.

    """
    real_type = models.ForeignKey(ContentType, null = True, editable=False)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            self.real_type = self._get_real_type()
        super(InheritanceCastModel, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def cast(self):
        return self.real_type.get_object_for_this_type(pk=self.pk)

    class Meta:
        abstract = True
        
class BaseTask(InheritanceCastModel):
    class Meta:
        ordering = ['name', ]
    name = models.TextField(blank = True, verbose_name = u'Название')
    text = models.TextField(blank = True, verbose_name = u'Описание')
    ans  = models.TextField(blank = True, verbose_name = u'Ответ')
    
    score_min = models.DecimalField(max_digits = 5, decimal_places = 2, default = Decimal('0.00'), verbose_name = u'Минимальная отметка за задачу')
    score_max = models.DecimalField(max_digits = 5, decimal_places = 2, default = Decimal('10.00'),verbose_name = u'Максимальная отметка за задачу')
    
    date_creation = models.DateTimeField(auto_now_add = True, verbose_name = u'Время создания')
    date_modification = models.DateTimeField(blank = True, null = True, auto_now = True, verbose_name = u'Время модификации')
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, verbose_name = u'Автор', related_name = 'author_tasks')

    def __unicode__(self):
        return u'%s' % self.name
    
class TextTask(BaseTask):
    class Meta:
        verbose_name = u'Тектовая задача'
        
        
class BaseSolution(InheritanceCastModel):
    class Meta:
        ordering = ['date_creation', ]
    
    STATUS_ACCEPTED = 0

    task = models.ForeignKey(BaseTask, verbose_name = u'Задача', related_name = 'solutions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name = u'Пользователь', related_name = 'solutions')
    checker = models.ForeignKey(settings.AUTH_USER_MODEL, blank = True, null = True, verbose_name = u'Кто проверил', related_name = 'checker_solutions')
    date_creation = models.DateTimeField(auto_now_add = True, verbose_name = u'Время создания')
    date_modification = models.DateTimeField(blank = True, null = True, auto_now = True, verbose_name = u'Время модификации')
    score = models.DecimalField(max_digits = 5, decimal_places = 2, default = Decimal('0.00'), verbose_name = u'Отметка')
    status = models.IntegerField(default = -1, verbose_name = u'Статус')

    def is_accepted(self):
        return self.status == BaseSolution.STATUS_ACCEPTED
    
    def set_status(self, status, checker = None):
        self.status = status
        self.checker = checker
        self.save()
    
    def assept(self, checker = None):
        self.set_status(BaseSolution.STATUS_ACCEPTED, checker)

class TextSolution(BaseSolution):
    class Meta:
        verbose_name = u'Тектовый ответ'
    
    text = models.TextField(verbose_name = u'Ответ')
