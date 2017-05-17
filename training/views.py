
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.http import HttpResponse
from django.views.generic import View
from django.db import transaction

from reversion import revisions as reversion

from decimal import Decimal

from .models import *


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'training/course.html'

class AttendanceAllCheck(View):
    def get(self, request, course_id, clazz_id, attendance_status):
        c1 = get_object_or_404(Course, pk=course_id)
        c2 = get_object_or_404(Class,  pk=clazz_id)
        with transaction.atomic(), reversion.create_revision():
            Attendance.attendance_all_set_status(c1, c2, attendance_status)
            reversion.set_user(request.user)
            reversion.set_comment("Setting to %s by %s" % (attendance_status, request.user))
        return HttpResponseRedirect(reverse('training:course', args=[course_id]))

class AttendanceCheck(View):
    def get(self, request, attendance_id):
        a = get_object_or_404(Attendance,  pk=attendance_id)
        with transaction.atomic(), reversion.create_revision():
            a.rotate()
            reversion.set_user(request.user)
            reversion.set_comment("Rotating by %s" % request.user)
        return HttpResponseRedirect(reverse('training:course', args=[a.clazz.course.id]))

class CourseTaskSolutionHandSet(View):
    def get(self, request, solution_id, val):
        a = get_object_or_404(CourseTaskSolution,  pk=solution_id)
        with transaction.atomic(), reversion.create_revision():
            a.hand_flag = True
            a.hand_score = Decimal(val)
            a.save()
            reversion.set_user(request.user)
            reversion.set_comment("Setting max score to task %s by user %s" % (a, request.user))
        return HttpResponseRedirect(reverse('training:course', args=[a.task.course.id]))