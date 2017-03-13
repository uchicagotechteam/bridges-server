from django.conf.urls import url

from rest_framework.urlpatterns import format_suffix_patterns

from bridges_api import views

urlpatterns = [
    url(r'^questions/$', views.QuestionList.as_view(), name='question-list'),
    url(r'^questions/(?P<pk>[0-9]+)/$', views.QuestionDetail.as_view()),
    url(r'^users/$', views.UserList.as_view(), name='user-list'),
    url(r'^user-info/$', views.UserDetail.as_view(), name='user-info'),
    url(r'^tags/$', views.TagList.as_view(), name='tag-list'),
    url(r'^employers/$', views.EmployerList.as_view(), name='employer-list'),
    url(r'^employers/(?P<pk>[0-9]+)/$', views.EmployerDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
