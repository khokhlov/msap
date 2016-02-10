#coding: utf-8

from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse

import datetime

from staff.models import SiteUser
from contingent.models import Student

class CourseProgramm(models.Model):
    name = models.TextField(blank = False, verbose_name = u'Название')
    
    def __unicode__(self):
        return u'%s' % self.name

class Course(models.Model):
    name     = models.TextField(blank = False, verbose_name = u'Название')
    programm = models.ForeignKey(CourseProgramm, blank = False, verbose_name = u'Программа курса')
    students = models.ManyToManyField(Student, related_name = 'courses', verbose_name = u'Студенты')
    teachers = models.ManyToManyField(SiteUser, related_name = 'courses_teacher', verbose_name = u'Учителя')
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_students(self):
        s = []
        for i in self.students.all():
            i.course_attendances = Attendance.get_or_create_cource(i, self)
            s.append(i)
        return s
    
    def add_group(self, g):
        self.students.add(*list(g.students.all()))
    
    def get_absolute_url(self):
        return reverse('training:course', args=[self.pk])
    
    def get_html_url(self):
        return '<a href="%s">%s</a>' % (self.get_absolute_url(), self.name)
    get_html_url.allow_tags = True
    get_html_url.short_description = u'Смотреть на сайте'
  

class Couple(models.Model):
    name       = models.TextField(blank = False, verbose_name = u'Название')
    short_name = models.TextField(blank = True, verbose_name = u'Сокращенное название')
    time_from  = models.TimeField(blank = False, verbose_name = u'Время начала')
    time_to    = models.TimeField(blank = False, verbose_name = u'Время окончания')
    
    def __unicode__(self):
        return u'%s' % self.name

class Class(models.Model):
    CLASS_OK     = 0
    CLASS_BAD    = 1
    CLASS_CANCEL = 2
    CLASS_NO     = 3
    CLASS_STATUS_CHOICES = (
        (CLASS_OK,     u'Состоялось'),
        (CLASS_BAD,    u'Не состоялось'),
        (CLASS_CANCEL, u'Отменено'),
        (CLASS_NO,     u'Не отмечено'),
    )
    
    class Meta:
        ordering = ['date', 'couple__time_from']
    
    course    = models.ForeignKey(Course, blank = False, related_name = 'classes', verbose_name = u'Курс')
    date      = models.DateField(blank = False, verbose_name = u'Дата')
    couple    = models.ForeignKey(Couple, blank = False, verbose_name = u'Пара')
    status    = models.IntegerField(choices = CLASS_STATUS_CHOICES, default = CLASS_NO, verbose_name = u'Статус')
    
    @staticmethod
    def gen_classes(course, date_from, date_to, couple):
        dt = datetime.timedelta(days = 7)
        t0 = date_from
        cnt = 0
        while t0 <= date_to:
            c = Class()
            c.course = course
            c.date = t0
            c.couple = couple
            c.save()
            t0 += dt
            cnt += 1
        return cnt
    
    def is_today(self):
        return datetime.date.today() == self.date
    
class Attendance(models.Model):
    class Meta:
        ordering = ['clazz__date', 'clazz__couple__time_from']
    
    ATTENDANCE_YES          = 0
    ATTENDANCE_NO           = 1
    ATTENDANCE_NO_BY_REASON = 2
    ATTENDANCE_UNDEFINED    = 3
    
    ATTENDANCE_STATUS_CHOICES = (
        (ATTENDANCE_YES,          u'Присутствовал'),
        (ATTENDANCE_NO,           u'Отсутствовал'),
        (ATTENDANCE_NO_BY_REASON, u'Уважительная причина'),
        (ATTENDANCE_UNDEFINED,    u'Не отмечено'),
    )
    
    clazz   = models.ForeignKey(Class, blank = False, related_name = 'attendances', verbose_name = u'Занятие')
    student = models.ForeignKey(Student, blank = False, related_name = 'attendances', verbose_name = u'Студент')
    status  = models.IntegerField(choices = ATTENDANCE_STATUS_CHOICES, default = ATTENDANCE_UNDEFINED, verbose_name = u'Статус')
    
    @staticmethod
    def get_or_create_class(student, clazz):
        q = Attendance.objects.filter(student = student).filter(clazz = clazz)
        if q.count() > 0:
            return q[0]
        a = Attendance()
        a.clazz = clazz
        a.student = student
        a.save()
        return a
    
    @staticmethod
    def get_or_create_cource(student, course):
        q = Attendance.objects.filter(student = student).filter(clazz__course = course)
        if q.count() != course.classes.count():
            for c in course.classes.all():
                Attendance.get_or_create_class(student, c)
        q = Attendance.objects.filter(student = student).filter(clazz__course = course)
        return q.all()
    
    @staticmethod
    def attendance_all_set_status(course, clazz, status):
        q = Attendance.objects.filter(clazz = clazz).filter(clazz__course = course)
        q.update(status = status)
    
    def rotate(self):
        if self.status == Attendance.ATTENDANCE_YES:
            self.status = Attendance.ATTENDANCE_NO
        else:
            self.status = Attendance.ATTENDANCE_YES
        self.save()
