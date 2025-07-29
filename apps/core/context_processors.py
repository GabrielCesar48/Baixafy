# apps/core/context_processors.py
from datetime import datetime
from django.conf import settings
from apps.baixador.services import spotify_service


def baixafy_context(request):
    """
    Context processor que adiciona variáveis globais aos templates.
    
    Args:
        request: HttpRequest object
        
    Returns:
        dict: Contexto adicional para templates
    """
    context = {
        # Informações do projeto
        'project_name': 'BaixaFy',
        'project_version': '1.0.0',
        'current_year': datetime.now().year,
        
        # Status do serviço
        'service_available': spotify_service is not None,
        
        # Configurações do BaixaFy
        'free_download_limit': getattr(settings, 'BAIXAFY_SETTINGS', {}).get('FREE_DOWNLOAD_LIMIT', 1),
        'premium_duration_days': getattr(settings, 'BAIXAFY_SETTINGS', {}).get('PREMIUM_DURATION_DAYS', 30),
        
        # URLs úteis
        'spotify_developer_url': 'https://developer.spotify.com/',
        'ffmpeg_download_url': 'https://ffmpeg.org/download.html',
        
        # Features disponíveis
        'features': {
            'individual_tracks': True,
            'playlists': True,
            'albums': True,
            'premium_subscription': True,
            'download_history': True,
        }
    }
    
    # Adicionar informações do usuário se autenticado
    if request.user.is_authenticated:
        context.update({
            'user_is_premium': request.user.is_premium_active(),
            'user_days_remaining': request.user.days_remaining(),
            'user_can_download': request.user.can_download(),
            'user_free_downloads_used': request.user.free_downloads_used,
            'user_total_downloads': request.user.total_downloads,
        })
    
    # Informações do serviço se disponível
    if spotify_service:
        try:
            health_status = spotify_service.health_check()
            context['service_health'] = health_status
        except Exception as e:
            context['service_health'] = {
                'status': 'error',
                'message': f'Erro ao verificar status: {str(e)}'
            }
    else:
        context['service_health'] = {
            'status': 'error',
            'message': 'Serviço não inicializado'
        }
    
    return context


def debug_context(request):
    """
    Context processor para informações de debug (apenas em desenvolvimento).
    
    Args:
        request: HttpRequest object
        
    Returns:
        dict: Contexto de debug
    """
    if not settings.DEBUG:
        return {}
    
    return {
        'debug_info': {
            'django_version': settings.DJANGO_VERSION if hasattr(settings, 'DJANGO_VERSION') else 'Unknown',
            'python_version': f"{settings.PYTHON_VERSION}" if hasattr(settings, 'PYTHON_VERSION') else 'Unknown',
            'request_path': request.path,
            'request_method': request.method,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
            'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest',
        }
    }