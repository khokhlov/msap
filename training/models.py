#coding: utf-8

from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.db import transaction

import datetime
from decimal import Decimal
import md5

from reversion import revisions as reversion

from staff.models import SiteUser, Mailing
from contingent.models import Student, Teacher
from tasks.models import BaseTask, BaseSolution

@reversion.register()
class CourseProgramm(models.Model):
    name = models.TextField(blank = False, verbose_name = u'Название')
    creatos = models.ManyToManyField(Teacher, blank = True, verbose_name = u'Составители', related_name = 'course_programms')
    
    def __unicode__(self):
        return u'%s' % self.name

@reversion.register()
class Course(models.Model):
    name     = models.TextField(blank = False, verbose_name = u'Название')
    programm = models.ForeignKey(CourseProgramm, blank = False, verbose_name = u'Программа курса')
    auto_check_code = models.TextField(blank = True, null = True, verbose_name = u'Код для автоматической проверки')
    auto_check_flag = models.BooleanField(default = False, verbose_name = u'Автоматическая проверка')
    students = models.ManyToManyField(Student, related_name = 'courses', verbose_name = u'Студенты')
    teachers = models.ManyToManyField(Teacher, related_name = 'courses_teacher', verbose_name = u'Учителя')
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_students(self):
        s = []
        for i in self.students.all():
            i = self.fill_student(i)
            s.append(i)
        return s
    
    def fill_student(self, s):
        s.course_attendances = Attendance.get_or_create_cource(s, self)
        s.course_solutions = CourseTaskSolution.get_or_create_solution_course(s, self)
        s.course_score = CourseScore.get_or_create(s, self)
        return s
    
    def is_auto_check(self):
        return self.auto_check_flag
    
    def add_group(self, g):
        self.students.add(*list(g.students.all()))
    
    def get_absolute_url(self):
        return reverse('training:course', args=[self.pk])
    
    def get_html_url(self):
        return '<a href="%s">%s</a>' % (self.get_absolute_url(), self.name)
    get_html_url.allow_tags = True
    get_html_url.short_description = u'Смотреть на сайте'
    
    def add_students_to_mailing(self, m):
        for s in self.students.all():
            m.to.add(s.user)
            
@reversion.register()    
class CourseScore(models.Model):
    course  = models.ForeignKey(Course, verbose_name = u'Курс')
    student = models.ForeignKey(Student, verbose_name = u'Студент')
    
    score_min   = models.DecimalField(max_digits = 5, decimal_places = 2, default = Decimal('0.00'), verbose_name = u'Минимум')
    score_max   = models.DecimalField(max_digits = 5, decimal_places = 2, default = Decimal('0.00'), verbose_name = u'Максимум')
    score_auto  = models.DecimalField(max_digits = 5, decimal_places = 2, default = Decimal('0.00'), verbose_name = u'Авто-оценка')
    score_final = models.DecimalField(max_digits = 5, decimal_places = 2, default = Decimal('0.00'), verbose_name = u'Финальная отметка')
    
    @staticmethod
    def get_or_create(student, course):
        q = CourseScore.objects.filter(course = course).filter(student = student)
        if q.count() > 0:
            return q[0]
        s = CourseScore()
        s.student = student
        s.course = course
        s.save()
        return s
    
    @transaction.atomic()
    @reversion.create_revision()
    def update(self):
        if self.course.is_auto_check():
            code = self.course.auto_check_code
            #TODO: implement
            self.score_max = Decimal("10")
            self.score_min = Decimal("0")
            self.save()
            

class Couple(models.Model):
    name       = models.TextField(blank = False, verbose_name = u'Название')
    short_name = models.TextField(blank = True, verbose_name = u'Сокращенное название')
    time_from  = models.TimeField(blank = False, verbose_name = u'Время начала')
    time_to    = models.TimeField(blank = False, verbose_name = u'Время окончания')
    
    def __unicode__(self):
        return u'%s' % self.name

@reversion.register()
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

@reversion.register()    
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

class CourseTask(models.Model):
    class Meta:
        ordering = ['num', ]

    short_name = models.CharField(max_length = 256, null = True, blank = True, verbose_name = u'Короткое название')
    task = models.ForeignKey(BaseTask, verbose_name = u'Описание')
    course = models.ForeignKey(Course, null = True, verbose_name = u'Курс', related_name = 'coursetasks')
    deadline_start = models.DateTimeField(blank = True, null = True, verbose_name = u'Начало сдачи')
    deadline_end = models.DateTimeField(blank = True, null = True, verbose_name = u'Окончание сдачи')
    
    num = models.IntegerField(default = 0, verbose_name = u'Номер задачи в курсе (для сортировки и авто отметки)')
    
    score_min = models.DecimalField(max_digits = 5, decimal_places = 2, default = Decimal('0.00'), verbose_name = u'Минимальная отметка за задачу')
    score_max = models.DecimalField(max_digits = 5, decimal_places = 2, default = Decimal('1.00'), verbose_name = u'Максимальная отметка за задачу')
    
    def __unicode__(self):
        return u'%s' % self.short_name

@reversion.register()
class CourseTaskSolution(models.Model):
    
    SOLUTION_BAD     = 0
    SOLUTION_GOOD    = 1
    SOLUTION_PARTIAL = 2
    
    class Meta:
        ordering = ['task__num', ]
    task = models.ForeignKey(CourseTask, verbose_name = u'Задача')
    student = models.ForeignKey(Student, verbose_name = u'Студент')
    solutions = models.ForeignKey(BaseSolution, null = True, blank = True, verbose_name = u'Решение')
    
    hand_flag = models.BooleanField(default = False, verbose_name = u'Выставить отметку вручную')
    hand_score = models.DecimalField(max_digits = 5, decimal_places = 2, default = Decimal('0.00'), verbose_name = u'Ручная отметка')
    
    def __unicode__(self):
        return u'%s, %s, %s' % (self.task, self.task.course, self.student)
    
    def get_score(self):
        if self.hand_flag:
            return self.hand_score
        if self.solutions:
            return 10000
        else:
            return self.task.score_min
    
    def get_status(self):
        if self.get_score() == self.task.score_min:
            return CourseTaskSolution.SOLUTION_BAD
        if self.get_score() == self.task.score_max:
            return CourseTaskSolution.SOLUTION_GOOD
        return CourseTaskSolution.SOLUTION_PARTIAL
    
    def get_status_class_css(self):
        classes = ['solution_bad', 'solution_good', 'solution_partial']
        return classes[self.get_status()]
    
    @staticmethod
    def get_or_create_solution(student, task):
        q = CourseTaskSolution.objects.filter(student = student).filter(task = task)
        if q.count() > 0:
            return q[0]
        s = CourseTaskSolution()
        s.student = student
        s.task = task
        s.solutions = None
        s.save()
        return s
    
    @staticmethod
    def get_or_create_solution_course(student, course):
        q = CourseTaskSolution.objects.filter(student = student).filter(task__course = course)
        if q.count() != course.coursetasks.count():
            for c in course.coursetasks.all():
                CourseTaskSolution.get_or_create_solution(student, c)
        q = CourseTaskSolution.objects.filter(student = student).filter(task__course = course)
        return q.all()
    
    def get_url(self):
        return reverse('admin:training_coursetasksolution_change', args=[self.pk])
    

def cts_upload(instance, filename):
    h = md5.md5('%s_%s' % (instance.cts.student.pk, filename)).hexdigest()
    return 'course_task_solutions_files/%s/%s/%s_%s' % (instance.cts.task.pk, instance.cts.student.pk, h, filename)

class CourseTaskSolutionFile(models.Model):
    class Meta:
        ordering = ['-created']

    cts = models.ForeignKey(CourseTaskSolution, verbose_name = u'Решение задачи')
    name = models.CharField(max_length = 1024, verbose_name = u'Название')
    attachment_file = models.FileField(upload_to = cts_upload, verbose_name = u'Файл')
    created = models.DateTimeField(auto_now_add = True, verbose_name = u'Время создания')
    modified = models.DateTimeField(auto_now=True, verbose_name = u'Время модификации')
    