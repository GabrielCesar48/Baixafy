# apps/core/views.py
import json
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import get_user_model
from django.conf import settings

from apps.users.forms import DownloadForm
from apps.baixador.services import SpotifyDownloadService, spotify_service
from apps.users.models import DownloadHistory

User = get_user_model()


def home(request):
    """
    Página inicial do BaixaFy.
    Mostra informações gerais e convida para cadastro/login.
    
    Args:
        request: Objeto de requisição HTTP
        
    Returns:
        HttpResponse: Página inicial renderizada
    """
    return render(request, 'home.html')


@login_required
def painel(request):
    """
    Painel principal do usuário logado.
    Mostra status da conta, formulário de download e histórico.
    
    Args:
        request: Objeto de requisição HTTP
        
    Returns:
        HttpResponse: Painel do usuário renderizado
    """
    user = request.user
    
    # Verificar se serviço está funcionando
    service_status = None
    if spotify_service:
        service_status = spotify_service.health_check()
    
    # Informações do usuário para o template
    context = {
        'user': user,
        'is_premium': user.is_premium_active(),
        'days_remaining': user.days_remaining(),
        'can_download': user.can_download(),
        'free_downloads_used': user.free_downloads_used,
        'total_downloads': user.total_downloads,
        'download_form': DownloadForm(),
        'recent_downloads': DownloadHistory.objects.filter(
            user=user, success=True
        ).order_by('-download_date')[:5],
        'service_status': service_status  # Para mostrar status do spotDL
    }
    
    # Adicionar aviso se serviço não estiver funcionando
    if not spotify_service or service_status.get('status') != 'ok':
        messages.warning(
            request,
            '⚠️ Serviço de download temporariamente indisponível. '
            'Nossos técnicos estão trabalhando para resolver.'
        )
    
    return render(request, 'painel.html', context)


@login_required
def pagamento(request):
    """
    Página de simulação de pagamento.
    Permite ao usuário "ativar" sua assinatura premium.
    
    Args:
        request: Objeto de requisição HTTP
        
    Returns:
        HttpResponse: Página de pagamento ou redirect após ativação
    """
    if request.method == 'POST':
        # Simular pagamento bem-sucedido
        request.user.activate_premium(days=30)
        
        messages.success(
            request, 
            f"🎉 Parabéns, {request.user.first_name}! "
            "Sua assinatura premium foi ativada com sucesso! "
            "Agora você pode baixar músicas ilimitadas por 30 dias."
        )
        
        return redirect('painel')
    
    return render(request, 'pagamento.html')


@login_required
@csrf_exempt
def get_spotify_info(request):
    """
    Endpoint AJAX para obter informações de uma URL do Spotify.
    Retorna metadados da música ou playlist em formato JSON.
    
    Args:
        request: Objeto de requisição HTTP
        
    Returns:
        JsonResponse: Metadados da música/playlist ou erro
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        })
    
    spotify_url = request.POST.get('spotify_url', '').strip()
    
    if not spotify_url:
        return JsonResponse({
            'success': False,
            'message': 'URL do Spotify é obrigatória'
        })
    
    # Verificar se serviço está disponível
    if not spotify_service:
        return JsonResponse({
            'success': False,
            'message': 'Serviço de download não está disponível. Tente novamente mais tarde.',
            'error_type': 'service_unavailable'
        })
    
    try:
        # Verificar se URL é válida
        url_info = spotify_service.extract_spotify_info(spotify_url)
        if 'error' in url_info:
            return JsonResponse({
                'success': False,
                'message': url_info['error']
            })
        
        # Obter metadados
        if url_info['type'] == 'track':
            metadata = spotify_service.get_track_metadata(spotify_url)
        else:
            # Para playlists e álbuns, usar método específico futuramente
            return JsonResponse({
                'success': False,
                'message': 'No momento, apenas músicas individuais são suportadas'
            })
        
        if 'error' in metadata:
            # Tratar erros específicos do spotDL
            error_msg = metadata['error']
            
            if 'Config file not found' in error_msg:
                return JsonResponse({
                    'success': False,
                    'message': '🔧 Sistema em configuração. Tente novamente em alguns minutos.',
                    'error_type': 'config_error',
                    'technical_message': 'spotDL config file missing'
                })
            elif 'No results found' in error_msg:
                return JsonResponse({
                    'success': False,
                    'message': '🎵 Música não encontrada ou não disponível para download'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao buscar música: {error_msg}'
                })
        
        return JsonResponse({
            'success': True,
            'track_info': {
                'name': metadata['name'],
                'artists': metadata['artists'],
                'album': metadata['album'],
                'duration': metadata['duration'],
                'cover_url': metadata['cover_url'],
                'year': metadata.get('year', 'N/A')
            }
        })
        
    except Exception as e:
        print(f"❌ Erro em get_spotify_info: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Erro interno do servidor. Tente novamente.',
            'error_type': 'internal_error'
        })


@login_required
@csrf_exempt
def download_music(request):
    """
    Endpoint AJAX para baixar música do Spotify.
    Processa download e retorna link para o arquivo.
    
    Args:
        request: Objeto de requisição HTTP
        
    Returns:
        JsonResponse: Resultado do download ou erro
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        })
    
    spotify_url = request.POST.get('spotify_url', '').strip()
    user = request.user
    
    if not spotify_url:
        return JsonResponse({
            'success': False,
            'message': 'URL do Spotify é obrigatória'
        })
    
    # Verificar se serviço está disponível
    if not spotify_service:
        return JsonResponse({
            'success': False,
            'message': 'Serviço de download temporariamente indisponível',
            'error_type': 'service_unavailable'
        })
    
    # Verificar se usuário pode baixar
    if not user.can_download():
        return JsonResponse({
            'success': False,
            'message': '⛔ Limite de downloads atingido! Assine o Premium para downloads ilimitados.',
            'needs_subscription': True
        })
    
    try:
        # Realizar download
        result = spotify_service.download_track(spotify_url, user)
        
        if 'error' in result:
            error_msg = result['error']
            
            # Tratar erros específicos
            if 'Config file not found' in error_msg:
                return JsonResponse({
                    'success': False,
                    'message': '🔧 Sistema em manutenção. Nossa equipe está configurando o servidor. Tente novamente em alguns minutos.',
                    'error_type': 'config_error'
                })
            elif 'ffmpeg' in error_msg.lower():
                return JsonResponse({
                    'success': False,
                    'message': '🎵 Erro na conversão do áudio. Tente novamente.',
                    'error_type': 'conversion_error'
                })
            elif 'youtube' in error_msg.lower():
                return JsonResponse({
                    'success': False,
                    'message': '📺 Erro ao acessar fonte de áudio. Tente novamente mais tarde.',
                    'error_type': 'source_error'
                })
            elif result.get('needs_subscription'):
                return JsonResponse({
                    'success': False,
                    'message': error_msg,
                    'needs_subscription': True
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Erro no download: {error_msg}'
                })
        
        # Download bem-sucedido
        return JsonResponse({
            'success': True,
            'message': '🎵 Download concluído com sucesso!',
            'filename': result['filename'],
            'download_url': f"/download-file/?file={result['filename']}",
            'metadata': result['metadata']
        })
        
    except Exception as e:
        print(f"❌ Erro em download_music: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Erro interno. Tente novamente mais tarde.',
            'error_type': 'internal_error'
        })


@login_required
def download_file(request):
    """
    Serve arquivos de download para o usuário.
    Verifica se o arquivo pertence ao usuário antes de servir.
    
    Args:
        request: Objeto de requisição HTTP
        
    Returns:
        FileResponse: Arquivo para download ou erro 404
    """
    filename = request.GET.get('file')
    
    if not filename:
        raise Http404("Arquivo não especificado")
    
    # Verificar se download pertence ao usuário
    download = DownloadHistory.objects.filter(
        user=request.user,
        file_path__endswith=filename,
        success=True
    ).first()
    
    if not download:
        raise Http404("Arquivo não encontrado ou sem permissão")
    
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    
    if not os.path.exists(file_path):
        raise Http404("Arquivo não existe no servidor")
    
    try:
        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=filename
        )
        response['Content-Type'] = 'audio/mpeg'
        return response
        
    except Exception as e:
        print(f"❌ Erro ao servir arquivo: {str(e)}")
        raise Http404("Erro ao acessar arquivo")


@login_required
def historico(request):
    """
    Página com histórico completo de downloads do usuário.
    
    Args:
        request: Objeto de requisição HTTP
        
    Returns:
        HttpResponse: Página de histórico renderizada
    """
    user = request.user
    
    # Todos os downloads do usuário
    downloads = DownloadHistory.objects.filter(
        user=user
    ).order_by('-download_date')
    
    # Estatísticas
    total_downloads = downloads.filter(success=True).count()
    failed_downloads = downloads.filter(success=False).count()
    
    context = {
        'downloads': downloads,
        'total_downloads': total_downloads,
        'failed_downloads': failed_downloads,
        'user': user
    }
    
    return render(request, 'historico.html', context)


# View para debug (remover em produção)
@login_required
def debug_spotdl(request):
    """
    View de debug para verificar status do spotDL.
    REMOVER EM PRODUÇÃO!
    """
    if not settings.DEBUG:
        raise Http404("Não disponível em produção")
    
    status = {}
    
    if spotify_service:
        status = spotify_service.health_check()
        status['service_initialized'] = True
    else:
        status = {
            'service_initialized': False,
            'status': 'error',
            'message': 'SpotifyDownloadService não inicializado'
        }
    
    return JsonResponse(status, json_dumps_params={'indent': 2})