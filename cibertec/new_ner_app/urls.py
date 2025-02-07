from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('save_results/', views.save_results, name='save_results'),
    path('results/', views.results, name='results'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('delete_ner_text/<int:id>/', views.delete_ner_text, name='delete_ner_text'),
]