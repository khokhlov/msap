#coding: utf-8

from django.contrib import admin
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django import forms
from django.core.urlresolvers import reverse

from reversion_compare.helpers import patch_admin

from .models import *
from .forms import *
from contingent.models import Student


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

def create_mailing(modeladmin, request, queryset):
    t = u''
    if queryset.count() > 0:
        t = queryset.all()[0].__unicode__()
    m = Mailing.create_mailing(t, u'', [])
    m.author = request.user
    m.save()
    for c in queryset.all():
        c.add_students_to_mailing(m)
    return HttpResponseRedirect(reverse('admin:staff_mailing_change', args=[m.id]))
create_mailing.short_description = u'Создать рассылку'

class ClassInline(admin.TabularInline):
    model = Class
    extra = 1


class StudentInline(admin.TabularInline):
    model = Course.students.through
    extra = 1
    verbose_name = u'студент'
    verbose_name_plural = u'Добавить сутдентов'

class CourseTaskInline(admin.TabularInline):
    model = CourseTask
    extra = 1

class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        #fields = '__all__'
        fields = ['name', 'programm', 'auto_check_flag', 'auto_check_code']
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
    inlines = [CourseTaskInline, ClassInline, StudentInline]
    actions = [create_classes, add_groups, create_mailing]
    view_on_site = True
    list_display = ['name', 'get_html_url']



class CourseTaskSolutionFileInline(admin.TabularInline):
    model = CourseTaskSolutionFile
    extra = 1
    fields = ['name', 'attachment_file', 'created']
    readonly_fields = ['created',]


class CourseTaskSolutionAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        fields = self.readonly_fields
        fields += ('task', 'student')
        return fields
    
    fieldsets = (
        (None,              {'fields': ('solutions', )}),
        (u'Ручная отметка', {'fields': ('hand_flag', 'hand_score', )}),  
        (u'Инфо',           {'fields': ('task', 'student', )}),  
    )
    
    inlines = (CourseTaskSolutionFileInline, )

def update_course_scores(modeladmin, request, queryset):
    for i in queryset.all():
        i.update()
update_course_scores.short_description = u'Обновить авто значения'

class CourseScoreAdmin(admin.ModelAdmin):
    list_display = ['course', 'student']
    actions = [update_course_scores, ]
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('score_min', 'score_max', 'score_auto', 'student', 'course')

admin.site.register(CourseProgramm)
admin.site.register(Couple)
admin.site.register(CourseTaskSolution, CourseTaskSolutionAdmin)
admin.site.register(CourseScore, CourseScoreAdmin)
admin.site.register(Attendance)
admin.site.register(Course, CourseAdmin)

patch_admin(CourseProgramm)
patch_admin(CourseTaskSolution)
patch_admin(Course)
patch_admin(Attendance)
patch_admin(CourseScore)
