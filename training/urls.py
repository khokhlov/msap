from django.conf.urls import url

from . import views

app_name = 'training'
urlpatterns = [
    # ex: /course/5/
    url(r'^course/(?P<pk>[0-9]+)/$', views.CourseDetailView.as_view(), name='course'),
    url(r'^attendance_all_check/(?P<course_id>[0-9]+)/(?P<clazz_id>[0-9]+)/(?P<attendance_status>[0-9]+)/$', views.AttendanceAllCheck.as_view(), name='attendance_all_check'),
    url(r'^attendance_check/(?P<attendance_id>[0-9]+)/$', views.AttendanceCheck.as_view(), name='attendance_check'),
    url(r'^course_task_solution_hand_set/(?P<solution_id>[0-9]+)/(?P<val>[0-9\.]+)$', views.CourseTaskSolutionHandSet.as_view(), name='course_task_solution_hand_set'),
]
