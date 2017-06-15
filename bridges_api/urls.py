from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from rest_framework.urlpatterns import format_suffix_patterns

from bridges_api import views

urlpatterns = [
    url(r'^questions/$', views.QuestionList.as_view(), name='question-list'),
    url(r'^questions/(?P<pk>[0-9]+)/$', views.QuestionDetail.as_view()),
    url(r'^users/$', views.UserList.as_view(), name='user-list'),
    url(r'^user-info/$', views.UserDetail.as_view(), name='user-info'),
    url(r'^tags/$', views.TagList.as_view(), name='tag-list'),
    url(r'^employers/$', views.EmployerList.as_view(), name='employer-list'),
    url(r'^employers/(?P<pk>[0-9]+)/$', views.EmployerDetail.as_view()),
    url(r'^positions/$', views.PositionList.as_view(), name='position-list'),
    url(r'^ethnicities/$', views.EthnicityList.as_view(), name='ethnicity-list'),
    url(r'^genders/$', views.GenderList.as_view(), name='gender-list'),
    url(r'^bookmarks/', views.BookmarksManager.as_view(), name='bookmarks')
]

urlpatterns = format_suffix_patterns(urlpatterns)

# So we can serve profile pictures in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
