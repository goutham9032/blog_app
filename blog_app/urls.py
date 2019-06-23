# Django imports
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

# user imports
from app import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^accounts/login/$', app_views.login_user, name="login_user"),
    url(r'^accounts/register/$', app_views.register, name="register"),
    url(r'^accounts/logout/$', app_views.logout_user, name='logout_user'),
    url(r'^', include('app.urls')), 
]
