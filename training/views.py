
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.http import HttpResponse
from django.views.generic import View

from .models import *


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'training/course.html'

class AttendanceAllCheck(View):
    def get(self, request, course_id, clazz_id, attendance_status):
        c1 = get_object_or_404(Course, pk=course_id)
        c2 = get_object_or_404(Class,  pk=clazz_id)
        Attendance.attendance_all_set_status(c1, c2, attendance_status)
        return HttpResponseRedirect(reverse('training:course', args=[course_id]))

class AttendanceCheck(View):
    def get(self, request, attendance_id):
        a = get_object_or_404(Attendance,  pk=attendance_id)
        a.rotate()
        return HttpResponseRedirect(reverse('training:course', args=[a.clazz.course.id]))