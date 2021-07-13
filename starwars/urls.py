from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dataset/<uuid:dataset_uuid>/', views.details, name='details'),
    path('fetch/', views.fetch, name='fetch'),
]
