#coding: utf-8

from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms

from .models import *
from .forms import *


def create_classes(modeladmin, request, queryset):
    form = None

    if 'apply' in request.POST:
        form = CreateClassesForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_start']
            date_to = form.cleaned_data['date_end']
            couple = form.cleaned_data['couples']
            c = 0
            for course in queryset.all():
                c = Class.gen_classes(course, date_from, date_to, couple)
            modeladmin.message_user(request, "Добавлено %s семинаров к %s курсам." % (c, queryset.count()))
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = CreateClassesForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    return render(request, 'training/create_classes_action.html', {'items': queryset, 'form': form, 'title': u'Создать расписание'})

create_classes.short_description = u'Создать расписание'

def add_groups(modeladmin, request, queryset):
    form = None

    if 'apply' in request.POST:
        form = AddGroupForm(request.POST)
        if form.is_valid():
            g = form.cleaned_data['group']
            c = 0
            for course in queryset.all():
                course.add_group(g)
            modeladmin.message_user(request, "Добавлено %s студентов." % (g.students.count()))
            return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = AddGroupForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    return render(request, 'training/add_groups_action.html', {'items': queryset, 'form': form, 'title': u'Добавить студентов из групп'})
add_groups.short_description = u'Добавить студентов'

class ClassInline(admin.TabularInline):
    model = Class
    extra = 1

class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        #fields = '__all__'
        fields = ['name', 'programm']
        widgets = {
            'name': forms.TextInput(),
        }

class CourseAdmin(admin.ModelAdmin):
    def get_queryset(self, request): 
        qs = super(CourseAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(teachers = request.user)
    form = CourseAdminForm
    inlines = [ClassInline]
    actions = [create_classes, add_groups]
    view_on_site = True
    list_display = ['name', 'get_html_url']


admin.site.register(CourseProgramm)
admin.site.register(Couple)
admin.site.register(Attendance)
admin.site.register(Course, CourseAdmin)

