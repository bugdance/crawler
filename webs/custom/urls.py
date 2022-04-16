from django.urls import path

from . import views

urlpatterns = [
    path('sync/', views.sync_charts, name='sync_charts'),
]