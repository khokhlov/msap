
from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.http import HttpResponse
from django.views.generic import View
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseForbidden

from reversion import revisions as reversion

from decimal import Decimal

from .models import *


class CourseDetailView(UserPassesTestMixin, generic.DetailView):
    model = Course
    template_name = 'training/course.html'
    raise_exception = True
    
    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        u = self.request.user
        context['is_student'] = self.object.is_student(u)
        context['is_teacher'] = self.object.is_teacher(u)
        return context
    
    def test_func(self):
        u = self.request.user
        o = self.get_object()
        return o.is_student(u) or o.is_teacher(u)
    
    
    @method_decorator(login_required())
    def dispatch(self, request, *args, **kwargs):
        return super(CourseDetailView, self).dispatch(request, *args, **kwargs)


class AttendanceAllCheck(View):
    def get(self, request, course_id, clazz_id, attendance_status):
        c1 = get_object_or_404(Course, pk=course_id)
        if not c1.is_teacher(request.user):
            return HttpResponseRedirect(reverse('training:course', args=[course_id]))
        c2 = get_object_or_404(Class,  pk=clazz_id)
        with transaction.atomic(), reversion.create_revision():
            Attendance.attendance_all_set_status(c1, c2, attendance_status)
            reversion.set_user(request.user)
            reversion.set_comment("Setting to %s by %s" % (attendance_status, request.user))
        return HttpResponseRedirect(reverse('training:course', args=[course_id]))

class AttendanceCheck(View):
    def get(self, request, attendance_id):
        a = get_object_or_404(Attendance,  pk=attendance_id)
        if not a.clazz.course.is_teacher(request.user):
            return HttpResponseRedirect(reverse('training:course', args=[a.clazz.course.id]))
        with transaction.atomic(), reversion.create_revision():
            a.rotate()
            reversion.set_user(request.user)
            reversion.set_comment("Rotating by %s" % request.user)
        return HttpResponseRedirect(reverse('training:course', args=[a.clazz.course.id]))

class CourseTaskSolutionHandSet(View):
    def get(self, request, solution_id, val):
        a = get_object_or_404(CourseTaskSolution,  pk=solution_id)
        if not a.task.course.is_teacher(request.user):
            return HttpResponseRedirect(reverse('training:course', args=[a.task.course.id]))
        with transaction.atomic(), reversion.create_revision():
            a.hand_flag = True
            a.hand_score = Decimal(val)
            a.save()
            reversion.set_user(request.user)
            reversion.set_comment("Setting max score to task %s by user %s" % (a, request.user))
        return HttpResponseRedirect(reverse('training:course', args=[a.task.course.id]))
