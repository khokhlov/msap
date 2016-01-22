#coding: utf-8

from django import forms
from django.forms.extras.widgets import SelectDateWidget

from .models import *
from staff.models import *

class CreateClassesForm(forms.Form):
    _selected_action = forms.CharField(widget = forms.MultipleHiddenInput)
    date_start       = forms.DateField(label = u'Дата первого занятия', widget = SelectDateWidget)
    date_end         = forms.DateField(label = u'Дата последнего занятия', widget = SelectDateWidget)
    couples          = forms.ModelChoiceField(queryset = Couple.objects.all(), label=u'Пара')

class AddGroupForm(forms.Form):
    _selected_action = forms.CharField(widget = forms.MultipleHiddenInput)
    group            = forms.ModelChoiceField(queryset = StudentsGroup.objects.all(), label=u'Группа')
