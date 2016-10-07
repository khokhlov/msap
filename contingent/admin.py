#coding: utf-8

from django.contrib import admin
from django import forms
from django.http import HttpResponseRedirect

from reversion_compare.helpers import patch_admin
from reversion_compare.admin import CompareVersionAdmin


from .models import *


def create_mailing(modeladmin, request, queryset):
    t = u''
    if queryset.count() > 0:
        t = queryset.all()[0].__unicode__()
    m = Mailing.create_mailing(t, u'', [])
    m.author = request.user
    m.save()
    for c in queryset.all():
        for s in c.students.all():
            m.to.add(s.user)
    return HttpResponseRedirect(reverse('admin:staff_mailing_change', args=[m.id]))
create_mailing.short_description = u'Создать рассылку'

def create_mailing_contingent(modeladmin, request, queryset):
    t = u''
    if queryset.count() > 0:
        t = queryset.all()[0].__unicode__()
    m = Mailing.create_mailing(t, u'', [])
    m.author = request.user
    m.save()
    for c in queryset.all():
        m.to.add(c.user)
    return HttpResponseRedirect(reverse('admin:staff_mailing_change', args=[m.id]))
create_mailing_contingent.short_description = u'Создать рассылку'

def create_mailing_sm_t(modeladmin, request, queryset):
    t = u''
    if queryset.count() > 0:
        t = queryset.all()[0].__unicode__()
    m = Mailing.create_mailing(t, u'', [])
    m.author = request.user
    m.save()
    for c in queryset.all():
        m.to.add(c.supervisor.user)
    return HttpResponseRedirect(reverse('admin:staff_mailing_change', args=[m.id]))
create_mailing_sm_t.short_description = u'Создать рассылку по научрукам'

def create_mailing_sm_s(modeladmin, request, queryset):
    t = u''
    if queryset.count() > 0:
        t = queryset.all()[0].__unicode__()
    m = Mailing.create_mailing(t, u'', [])
    m.author = request.user
    m.save()
    for c in queryset.all():
        m.to.add(c.student.user)
    return HttpResponseRedirect(reverse('admin:staff_mailing_change', args=[m.id]))
create_mailing_sm_s.short_description = u'Создать рассылку по студентам'




class StudentsGroupAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentsGroupAdminForm, self).__init__(*args, **kwargs)
        print kwargs
        if 'instance' in kwargs:
             self.fields['monitor'].queryset = kwargs['instance'].students

    class Meta:
        model = StudentsGroup
        #fields = '__all__'
        fields = ['name', 'year', 'monitor']
        widgets = {
            'name': forms.TextInput(),
        }

class StudentsGroupAdmin(admin.ModelAdmin):
    form = StudentsGroupAdminForm
    
    actions = [create_mailing, ]

class PositionAdmin(admin.ModelAdmin):
    list_display = ['user', 'employment_type', 'position_type', 'date_from', 'date_to', 'rate', 'subdivision', 'active']
    list_filter = ('active', 'employment_type', 'position_type', 'subdivision')
    
class ScientificManagementAdmin(admin.ModelAdmin):
    list_display = ['supervisor', 'student', 'active_flag', 'created', 'modified', ]
    list_filter = ('active_flag',)
    
    actions = [create_mailing_sm_t, create_mailing_sm_s, ]

class TeacherAdmin(admin.ModelAdmin):
    actions = [create_mailing_contingent, ]
    

admin.site.register(StudentsGroup, StudentsGroupAdmin)
admin.site.register(Student)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Subdivision)
admin.site.register(PositionType)
admin.site.register(EmploymentType)
admin.site.register(ScientificManagement, ScientificManagementAdmin)
admin.site.register(Position, PositionAdmin)

patch_admin(Subdivision)
