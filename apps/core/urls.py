# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('painel/', views.painel, name='painel'),
    path('pagamento/', views.pagamento, name='pagamento'),
    path('historico/', views.historico, name='historico'),
    
    # Endpoints AJAX
    path('api/spotify-info/', views.get_spotify_info, name='spotify_info'),
    path('api/download/', views.download_music, name='download_music'),
    path('download-file/', views.download_file, name='download_file'),
]
