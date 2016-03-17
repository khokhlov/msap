#coding: utf-8

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.conf import settings
from django.core.mail import send_mass_mail
from django.core.urlresolvers import reverse
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template import Context, Template

import md5
import datetime

from html2text import html2text
from reversion import revisions as reversion


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

@reversion.register()
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
    subject     = models.TextField(verbose_name = u'Тема')
    message     = models.TextField(verbose_name = u'Сообщение html')
    message_txt = models.TextField(blank = True, null = True, verbose_name = u'Сообщение txt')
    to = models.ManyToManyField(SiteUser, related_name = 'mailings', verbose_name = u'Кому')
    is_delivered = models.BooleanField(default = False, verbose_name = u'Отправлено')
    date = models.DateTimeField(auto_now_add = True, verbose_name = u'Дата создания')
    author = models.ForeignKey(SiteUser, null = True, verbose_name = u'Отправитель')
    date_delivery = models.DateTimeField(default = None, null = True, verbose_name = u'Дата отправки')
    with_notification = models.BooleanField(default = False, verbose_name = u'С уведомлениями')
    notification_redirect = models.TextField(blank = True, null = True, verbose_name = u'Ссылка для уведомления')
    
    def send(self):
        msgs = self.create_messages()
        ret = self.send_mass_html_mail(msgs, fail_silently=False)
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
        if self.with_notification:
            MailingStatus.get_or_create(self, to)
        #m = self.process_message(self.message, to)
        ctx = self.get_context(to)
        ts = Template(self.subject)
        tmh = Template(self.message)
        tmt = Template(self.message_txt)
        txt = ''
        if self.message_txt is not None and self.message_txt != '':
            txt = tmt.render(ctx)
        else:
            txt = html2text(tmh.render(ctx))
        return (ts.render(ctx), txt, tmh.render(ctx), settings.DEFAULT_FROM_EMAIL, [to.email,])
    
    def create_messages(self):
        msgs = []
        for to in self.to.all():
            msgs.append(self.create_single_message(to))
        return msgs
    
    def get_context(self, to):
        ctx = {
            'user': to,
            'mailing': self,
            'mailing_status': None,
            }
        if self.with_notification:
            ctx['mailing_status'] = MailingStatus.get_or_create(self, to)
        return Context(ctx)
    
    def process_message(self, m, to):
        m = m.replace('%NAME%', to.name)
        m = m.replace('%SURNAME%', to.surname)
        m = m.replace('%PATRONYMIC%', to.patronymic)
        if self.with_notification:
            s = MailingStatus.get_or_create(self, to)
            m = m.replace('%NOTIFY_URL%', s.get_url())
        return m
    
    def send_mass_html_mail(self, datatuple, fail_silently=False, user=None, password=None, connection=None):
        """
        Given a datatuple of (subject, text_content, html_content, from_email,
        recipient_list), sends each message to each recipient list. Returns the
        number of emails sent.

        If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
        If auth_user and auth_password are set, they're used to log in.
        If auth_user is None, the EMAIL_HOST_USER setting is used.
        If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

        """
        connection = connection or get_connection(
            username=user, password=password, fail_silently=fail_silently)
        messages = []
        for subject, text, html, from_email, recipient in datatuple:
            message = EmailMultiAlternatives(subject, text, from_email, recipient)
            message.attach_alternative(html, 'text/html')
            messages.append(message)
        return connection.send_messages(messages)

class MailingStatus(models.Model):
    mailing = models.ForeignKey(Mailing, verbose_name = u'Рассылка', related_name = 'statuses')
    recipient = models.ForeignKey(SiteUser, verbose_name = u'Получатель', related_name = 'mailing_statuses')
    received = models.BooleanField(default = False, verbose_name = u'Получено')
    slug = models.SlugField(verbose_name = u'Код')
    redirect_url = models.TextField(blank = True, null = True, default = '', verbose_name = u'Ссылка для редиректа')
    modified = models.DateTimeField(blank = True, null = True, auto_now = True, verbose_name = u'Время модификации')
    
    @staticmethod
    def get_or_create(mailing, user):
        q = MailingStatus.objects.filter(recipient = user).filter(mailing = mailing)
        if q.count() > 0:
            return q[0]
        ms = MailingStatus()
        ms.recipient = user
        ms.mailing = mailing
        if mailing.notification_redirect is not None and mailing.notification_redirect != '':
            ms.redirect_url = mailing.notification_redirect
        ms.save()
        return ms

    def get_url(self):
        return reverse('staff:mailing_status_read', args=[self.slug])
    
    def save(self, *args, **kwargs):
        super(MailingStatus, self).save(*args, **kwargs)
        self.slug = md5.md5('%s' % self.id).hexdigest()
        super(MailingStatus, self).save(*args, **kwargs)
