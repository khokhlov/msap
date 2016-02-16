from django.conf.urls import url

from . import views

app_name = 'staff'
urlpatterns = [
    # ex: /course/5/
    url(r'^mailingstatus/(?P<slug>[\w-]+)/$', views.MailinsStatusReadView.as_view(), name='mailing_status_read'),
]
