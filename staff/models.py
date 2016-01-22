#coding: utf-8

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin

class StudentsGroup(models.Model):
    class Meta:
        ordering = ['year', 'name']
            
    name = models.TextField(blank=False, verbose_name=u'Название')
    year = models.IntegerField(blank=False, verbose_name=u'Год')
    
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

class SiteUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email address must be set')

        email = SiteUserManager.normalize_email(email)
        user  = self.model(email=email,
                          is_staff=False, is_active=True, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        u = self.create_user(email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u

class SiteUser(AbstractBaseUser, PermissionsMixin):
    class Meta:
        ordering = ['surname', 'name']
    
    email  = models.EmailField(unique=True, blank=False, verbose_name=u'Основной адрес электронной почты (логин)')
    email2 = models.EmailField(unique=False, blank=True, verbose_name=u'Дополнительный адрес электронной почты (не обязателен)')

    is_active = models.BooleanField(default=True)
    is_admin  = models.BooleanField(default=False)
    is_staff  = models.BooleanField(default=False)
    
    is_student = models.BooleanField(default=False, verbose_name = u'Студент')
    is_teacher = models.BooleanField(default=False, verbose_name = u'Учитель')
    
    name       = models.TextField(blank=True, verbose_name=u'Имя')
    patronymic = models.TextField(blank=True, verbose_name=u'Отчество')
    surname    = models.TextField(blank=True, verbose_name=u'Фамилия')
    
    students_group = models.ForeignKey(StudentsGroup, blank = True, null = True, related_name = 'students', verbose_name = u'Группа')

    USERNAME_FIELD = 'email'

    objects = SiteUserManager()

    def get_full_name(self):
        return '%s %s %s' % (self.surname, self.name, self.patronymic)

    def get_short_name(self):
        return self.name
    
    @staticmethod
    def has(email):
        return SiteUser.objects.filter(email = email).count() > 0
    
    @staticmethod
    def create(name, patronymic, surname, is_student, is_teacher, email, password):
        u = SiteUser()
        u.name = name
        u.patronymic = patronymic
        u.surname = surname
        u.is_student = is_student
        u.is_teacher = is_teacher
        u.email = email
        u.set_password(password)
        u.save()
        return u
    
    @staticmethod
    def get_by_email(email):
        return SiteUser.objects.filter(email = email)[0]
    
    def get_attendances(self, course):
        return self.attendances.filter(clazz__course = course).all()


