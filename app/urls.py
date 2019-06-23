from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    url('^$', views.home, name='home'),
    url(r'^postfeed/$', views.post_feed, name='post_blog'),
    url(r'^createcomment/$', views.create_comment, name='create_comment'),
    url(r'^blogactivity/$', views.blog_activity, name='blog_activity'),
    url(r"^blog/(?P<slug>[\w-]+)/(?P<type>[\w-]+)$", views.view_edit_blog, name="view_edit_blog"),
    url(r"^users/(?P<username>[\w-]+)$", views.user_page, name="user_page"),
    url(r"^settings/(?P<user_type>[\w-]+)$", views.user_settings, name="user_settings"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
