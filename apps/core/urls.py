# apps/core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Páginas principais
    path('', views.home, name='home'),
    path('painel/', views.painel, name='painel'),
    path('pagamento/', views.pagamento, name='pagamento'),
    
    # Endpoints AJAX para downloads
    path('api/spotify-info/', views.get_spotify_info, name='spotify_info'),
    path('api/download/', views.download_music, name='download_music'),
    
    # Downloads de arquivos
    path('download/<str:filename>/', views.download_file, name='download_file'),
    
    # Histórico
    path('historico/', views.historico, name='historico'),
]