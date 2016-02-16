#coding: utf-8
from __future__ import unicode_literals

from django.db import models

from staff.models import *

class StudentsGroup(models.Model):
    class Meta:
        ordering = ['year', 'name']
            
    name = models.TextField(blank=False, verbose_name=u'Название')
    year = models.IntegerField(blank=False, verbose_name=u'Год')
    monitor = models.ForeignKey('contingent.Student', blank = True, null = True, related_name = 'monitor_group', verbose_name = u'Староста')
    
    def __unicode__(self):
        return '%s, %s' % (self.name, self.year)
    
    @staticmethod
    def get_or_create(name, year):
        q = StudentsGroup.objects.filter(year = year).filter(name = name)
        if q.count() > 0:
            return q[0]
        g = StudentsGroup()
        g.name = name
        g.year = year
        g.save()
        return g

class Student(models.Model):
    user = models.OneToOneField(SiteUser, related_name='student')
    group = models.ForeignKey(StudentsGroup, blank = True, null = True, related_name = 'students', verbose_name = u'Группа')

    def __unicode__(self):
        return self.user.__unicode__()
    
    def is_monitor(self):
        return self.group.monitor == self
    
    @staticmethod
    def create(name, patronymic, surname, email, password):
        u = None
        if SiteUser.has(email):
            u = SiteUser.get_by_email(email)
        else:
            u = SiteUser.create(name, patronymic, surname, email, password)
        s = Student()
        s.user = u
        s.save()
        return s
    
    @staticmethod
    def has_by_email(email):
        return Student.objects.filter(user__email = email).count() > 0

    @staticmethod
    def get_by_email(email):
        return Student.objects.filter(user__email = email)[0]
    