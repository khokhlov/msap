#coding: utf-8

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.core.mail import send_mass_mail

import datetime


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
        ordering = ['surname',]
    
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
    
    def __unicode__(self):
        return u'%s %s %s' % (self.surname, self.name, self.patronymic)

class Mailing(models.Model):
    subject = models.TextField(verbose_name = u'Тема')
    message = models.TextField(verbose_name = u'Сообщение')
    to = models.ManyToManyField(SiteUser, related_name = 'mailings', verbose_name = u'Кому')
    is_delivered = models.BooleanField(default = False, verbose_name = u'Отправлено')
    date = models.DateTimeField(auto_now_add = True, verbose_name = u'Дата создания')
    author = models.ForeignKey(SiteUser, null = True, verbose_name = u'Отправитель')
    date_delivery = models.DateTimeField(default = None, null = True, verbose_name = u'Дата отправки')
    
    def send(self):
        msgs = self.create_messages()
        ret = send_mass_mail(msgs, fail_silently=False)
        if ret:
            self.date_delivery = datetime.datetime.now()
            self.is_delivered = True
            self.save()
        return ret
    
    @staticmethod
    def create_mailing(subj, msg, to):
        m = Mailing()
        m.subject = subj
        m.message = msg
        m.save()
        for i in to:
            m.to.add(i)
        return m
    
    def create_single_message(self, to):
        return (self.subject, self.message, settings.DEFAULT_FROM_EMAIL, [to.email,])
    
    def create_messages(self):
        msgs = []
        for to in self.to.all():
            msgs.append(self.create_single_message(to))
        return msgs

    
