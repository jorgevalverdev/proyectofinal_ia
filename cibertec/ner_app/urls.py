from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('saved_results/', views.saved_results, name='saved_results'),
]