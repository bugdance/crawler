from django.urls import path, include
# from rest_framework import routers

from . import views


urlpatterns = [
    path('overview/', views.OverView, name='overview'),
    path('industry/', views.IndustryView, name='industry'),
    path('platform/', views.PlatformView, name='platform'),
    path('medium/', views.MediumView, name='medium'),
]