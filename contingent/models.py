#coding: utf-8
from __future__ import unicode_literals

from django.db import models

from reversion import revisions as reversion

from decimal import Decimal

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

@reversion.register()
class Subdivision(models.Model):
    name = models.TextField(verbose_name = u'Название')
    chief = models.ForeignKey('contingent.Position', null = True, blank = True, related_name = u'chief_subdivisions', verbose_name = u'Заведующий')
    
    def __unicode__(self):
        return self.name

class PositionType(models.Model):
    name = models.TextField(verbose_name = u'Название')
    short_name = models.CharField(max_length=256, null = True, blank = True, verbose_name = u'Кратное название')
    
    def __unicode__(self):
        return self.name

class EmploymentType(models.Model):
    name = models.TextField(verbose_name = u'Название')
    short_name = models.CharField(max_length=256, null = True, blank = True, verbose_name = u'Кратное название')
    
    def __unicode__(self):
        return self.name

class AbstractTimedObject(models.Model):
    class Meta:
        abstract = True
    
    active    = models.BooleanField(default = True, verbose_name = u'Активный')
    date_from = models.DateTimeField(verbose_name = u'Дата от')
    date_to   = models.DateTimeField(null = True, blank = True, verbose_name = u'Дата до')
    
@reversion.register()
class Position(AbstractTimedObject):
    user = models.ForeignKey(SiteUser, related_name='positions', verbose_name = u'Сотрудник')
    subdivision = models.ForeignKey(Subdivision, related_name = 'employees', verbose_name = u'Подразделение')
    employment_type = models.ForeignKey(EmploymentType, verbose_name = u'Вид занятости')
    position_type = models.ForeignKey(PositionType, verbose_name = u'Должность')
    rate = models.DecimalField(max_digits = 3, decimal_places = 2, default = Decimal('0.00'), verbose_name = u'Ставка')
    
    def __unicode__(self):
        return '%s (%s)' % (self.user, self.position_type.short_name)
    