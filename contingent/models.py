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

class AbstractStaff(models.Model):
    class Meta:
        ordering = ['user__surname',]
        abstract = True
    
    user = models.OneToOneField(SiteUser, related_name='%(class)s')
    
    def __unicode__(self):
        return self.user.__unicode__()
    
    @staticmethod
    def create(clazz, name, patronymic, surname, email, password):
        u = None
        if SiteUser.has(email):
            u = SiteUser.get_by_email(email)
        else:
            u = SiteUser.create(name, patronymic, surname, email, password)
        s = clazz()
        print u, email
        s.user = u
        s.save()
        return s
    
    @staticmethod
    def has_by_email(clazz, email):
        return clazz.objects.filter(user__email = email).count() > 0
    
    @staticmethod
    def has_by_fio(clazz, surname, n1, n2):
        return clazz.objects.filter(user__name__iexact = n1).filter(user__surname__iexact = surname).filter(user__patronymic__iexact = n2).count() > 0
    
    @staticmethod
    def get_by_fio(clazz, surname, n1, n2):
        return clazz.objects.filter(user__name__iexact = n1).filter(user__surname__iexact = surname).filter(user__patronymic__iexact = n2)[0]

    @staticmethod
    def get_by_email(clazz, email):
        return clazz.objects.filter(user__email = email)[0]


class Student(AbstractStaff):
    group = models.ForeignKey(StudentsGroup, blank = True, null = True, related_name = 'students', verbose_name = u'Группа')

    def __unicode__(self):
        return '%s %s' % (self.user.__unicode__(), self.group)
    
    def is_monitor(self):
        if self.group is None:
            return False
        return self.group.monitor == self
    
    @staticmethod
    def create(name, patronymic, surname, email, password):
        return AbstractStaff.create(Student, name, patronymic, surname, email, password)
    
    @staticmethod
    def has_by_email(email):
        return AbstractStaff.has_by_email(Student, email)
    
    @staticmethod
    def has_by_fio(surname, n1, n2):
        return AbstractStaff.has_by_fio(Student, surname, n1, n2)
    
    @staticmethod
    def get_by_fio(surname, n1, n2):
        return AbstractStaff.get_by_fio(Student, surname, n1, n2)

    @staticmethod
    def get_by_email(email):
        return AbstractStaff.has_by_email(Student, email)

class Teacher(AbstractStaff):
    pass
