from django.contrib import admin
from django import forms

from .models import *

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

class PositionAdmin(admin.ModelAdmin):
    list_display = ['user', 'employment_type', 'position_type', 'date_from', 'date_to', 'rate', 'subdivision', 'active']
    list_filter = ('active', 'employment_type', 'position_type', 'subdivision')

admin.site.register(StudentsGroup, StudentsGroupAdmin)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Subdivision)
admin.site.register(PositionType)
admin.site.register(EmploymentType)
admin.site.register(Position, PositionAdmin)
