from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from staff.models import *

class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = SiteUser
        fields = ("email",)

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = SiteUser
        widgets = {
            'name': forms.TextInput(),
            'patronymic': forms.TextInput(),
            'surname': forms.TextInput(),
        }


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

    fieldsets = (
        (None,              {'fields': ('email', 'password',)}),
        ('Personal data',   {'fields': ('name', 'patronymic', 'surname', 'email2')}),  
        ('Permissions',     {'fields': ('is_student', 'is_teacher', 'is_active', 'is_staff', 'is_superuser',)}),  
        ('Groups',          {'fields': ('groups', 'user_permissions',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

    list_display = ('surname', 'name', 'patronymic', 'email',  'is_student', 'is_teacher')       
    list_filter = ('is_active', 'students_group')    
    search_fields = ('email',)       
    ordering = ('email',)


admin.site.register(SiteUser, MyUserAdmin)
admin.site.register(StudentsGroup)