from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.save_results, name='save_results'),
    path('results/', views.results, name='results'),
]