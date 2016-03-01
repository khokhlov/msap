from django.contrib import admin
from django import forms

from .models import *

class StudentsGroupAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentsGroupAdminForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
             self.fields['monitor'].queryset = initial.studentsgroup.students

    class Meta:
        model = StudentsGroup
        #fields = '__all__'
        fields = ['name', 'year', 'monitor']
        widgets = {
            'name': forms.TextInput(),
        }

class StudentsGroupAdmin(admin.ModelAdmin):
    form = StudentsGroupAdminForm


admin.site.register(StudentsGroup, StudentsGroupAdmin)
admin.site.register(Student)
admin.site.register(Teacher)
