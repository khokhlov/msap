#coding: utf-8

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin


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

    is_active = models.BooleanField(default=True)
    is_admin  = models.BooleanField(default=False)
    is_staff  = models.BooleanField(default=False)
    
    name       = models.TextField(blank=True, verbose_name=u'Имя')
    patronymic = models.TextField(blank=True, verbose_name=u'Отчество')
    surname    = models.TextField(blank=True, verbose_name=u'Фамилия')
    
    USERNAME_FIELD = 'email'

    objects = SiteUserManager()

    def get_full_name(self):
        return '%s %s %s' % (self.surname, self.name, self.patronymic)

    def get_short_name(self):
        return self.name
    
    def is_student(self):
        return self.student is not None
    
    @staticmethod
    def has(email):
        return SiteUser.objects.filter(email = email).count() > 0
    
    @staticmethod
    def create(name, patronymic, surname, email, password):
        u = SiteUser()
        u.name = name
        u.patronymic = patronymic
        u.surname = surname
        u.email = email
        u.set_password(password)
        u.save()
        return u
    
    @staticmethod
    def get_by_email(email):
        return SiteUser.objects.filter(email = email)[0]
    
    def get_attendances(self, course):
        return self.attendances.filter(clazz__course = course).all()


