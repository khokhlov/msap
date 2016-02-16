from django.shortcuts import render
from django.views import generic
from django import http

from .models import *

class MailinsStatusReadView(generic.DetailView):
    model = MailingStatus
    template_name = 'staff/mailing_status_read.html'
    
    def get(self, *args, **kwargs):
        o = self.get_object()
        o.received = True
        o.save()
        if o.redirect_url and o.redirect_url != '':
            return http.HttpResponsePermanentRedirect(o.redirect_url)
        return super(MailinsStatusReadView, self).get(*args, **kwargs)


