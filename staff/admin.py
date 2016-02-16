#coding: utf-8

from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.http import HttpResponseRedirect

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
        ('Personal data',   {'fields': ('name', 'patronymic', 'surname', )}),  
        ('Permissions',     {'fields': ('is_active', 'is_staff', 'is_superuser',)}),  
        ('Groups',          {'fields': ('groups', 'user_permissions',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

    list_display = ('surname', 'name', 'patronymic', 'email', 'is_student' )       
    list_filter = ('is_active', )    
    search_fields = ('email', 'surname', 'name')       
    ordering = ('email',)



class MailingChangeForm(forms.ModelForm):
    class Meta:
        model = Mailing
        widgets = {
            'subject': forms.TextInput(),
        }
        exclude = ('to', 'author', 'is_delivered', 'date_delivery')


class MailingToInline(admin.TabularInline):
    model = Mailing.to.through
    extra = 1
    verbose_name = u'получатель'
    verbose_name_plural = u'Добавить получателей "кому"'



def send_mailing(modeladmin, request, queryset):
    ret = True
    for o in queryset.all():
        ret = ret and o.send()
    if ret:
        modeladmin.message_user(request, u'Рассылка отправлена')
    else:
        modeladmin.message_user(request, u'Ошибка отправки!')
send_mailing.short_description = u'Отправить рассылку'


class ActionInChangeFormMixin(object):
    def response_action(self, request, queryset):
        """
        Prefer http referer for redirect
        """
        response = super(ActionInChangeFormMixin, self).response_action(request, queryset)
        if isinstance(response, HttpResponseRedirect):
            response['Location'] = request.META.get('HTTP_REFERER', response.url)
        return response

    def change_view(self, request, object_id, extra_context=None):
        actions = self.get_actions(request)
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
        else: 
            action_form = None
        extra_context=extra_context or {}
        extra_context['action_form'] = action_form
        return super(ActionInChangeFormMixin, self).change_view(request, object_id, extra_context=extra_context)

class MailingAdmin(ActionInChangeFormMixin, admin.ModelAdmin):
    inlines = [MailingToInline]
    form = MailingChangeForm
    list_display = ('subject', 'date', 'author', 'is_delivered')
    list_filter = ('is_delivered', )
    
    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()
    
    def get_readonly_fields(self, request, obj=None):
        fields = self.readonly_fields
        if obj:
            if obj.is_delivered:
                fields += ('subject', 'message',)
            fields += ('author', 'date', 'is_delivered', 'date_delivery')
        
        return fields
    
    """
    def change_view(self, request, object_id, extra_context=None):
        o = Mailing.objects.get(pk=object_id)
        if o.is_delivered:
            extra_context = extra_context or {}
            extra_context['show_save_and_add_another'] = False
            extra_context['show_save_and_continue'] = False
            extra_context['show_save'] = False
            extra_context['save_as'] = False
            extra_context['has_add_permission'] = False
        return super(MailingAdmin, self).change_view(request, object_id, extra_context=extra_context)
    """
    actions = [send_mailing, ]



admin.site.register(SiteUser, MyUserAdmin)
admin.site.register(Mailing, MailingAdmin)
