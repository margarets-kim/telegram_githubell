from django.urls import path
from . import views
from django.conf.urls import include

app_name = 'api'

urlpatterns = [
    path('', views,UserAlarm.as_view())
]