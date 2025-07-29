# apps/core/urls.py - VERSÃO CORRIGIDA
from django.urls import path
from . import views

urlpatterns = [
    # Página principal - única página do app
    path('', views.home, name='home'),
    
    # API endpoints para download
    path('api/download/', views.download_music, name='download_music'),
    path('api/progress/', views.download_progress, name='download_progress'),
    
    # Download de arquivos
    path('download/<str:filename>/', views.download_file, name='download_file'),
]