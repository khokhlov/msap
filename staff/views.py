from django.shortcuts import render
from django.views import generic

from .models import *

class MailinsStatusReadView(generic.DetailView):
    model = MailingStatus
    template_name = 'staff/mailing_status_read.html'
    
    def get_context_data(self, **kwargs):
        context = super(MailinsStatusReadView, self).get_context_data(**kwargs)
        o = self.get_object()
        o.received = True
        o.save()
        return context


