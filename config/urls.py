# config/urls.py - VERSÃO SIMPLIFICADA
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root=settings.MEDIA_ROOT
    )

# ====================================

# apps/core/urls.py - VERSÃO SIMPLIFICADA
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