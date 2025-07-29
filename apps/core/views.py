# core/views.py
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import get_user_model

from apps.users.forms import DownloadForm
from apps.baixador.services import SpotifyDownloadService
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
        ).order_by('-download_date')[:5]
    }
    
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
        request: Objeto de requisição HTTP (POST)
        
    Returns:
        JsonResponse: Metadados ou informações de erro
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        spotify_url = data.get('spotify_url', '').strip()
        
        if not spotify_url:
            return JsonResponse({'error': 'URL não fornecida'}, status=400)
        
        service = SpotifyDownloadService()
        
        # Verificar tipo de conteúdo
        url_info = service.extract_spotify_info(spotify_url)
        
        if 'error' in url_info:
            return JsonResponse(url_info, status=400)
        
        if url_info['type'] == 'track':
            # Obter metadados da música
            metadata = service.get_track_metadata(spotify_url)
            if 'error' in metadata:
                return JsonResponse(metadata, status=400)
            
            return JsonResponse({
                'type': 'track',
                'data': metadata
            })
        
        elif url_info['type'] in ['playlist', 'album']:
            # Obter metadados da playlist/álbum
            playlist_data = service.get_playlist_metadata(spotify_url)
            if 'error' in playlist_data:
                return JsonResponse(playlist_data, status=400)
            
            return JsonResponse({
                'type': 'playlist',
                'data': playlist_data
            })
        
        else:
            return JsonResponse({
                'error': 'Tipo de conteúdo não suportado'
            }, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    
    except Exception as e:
        return JsonResponse({
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@login_required
@csrf_exempt
def download_music(request):
    """
    Endpoint para iniciar download de música ou playlist.
    Processa a solicitação e retorna informações do download.
    
    Args:
        request: Objeto de requisição HTTP (POST)
        
    Returns:
        JsonResponse: Resultado do download ou informações de erro
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        spotify_url = data.get('spotify_url', '').strip()
        
        if not spotify_url:
            return JsonResponse({'error': 'URL não fornecida'}, status=400)
        
        # Verificar se usuário pode baixar
        if not request.user.can_download():
            return JsonResponse({
                'error': 'Você já usou seu download gratuito! Assine o plano premium para downloads ilimitados.',
                'needs_subscription': True
            }, status=403)
        
        service = SpotifyDownloadService()
        url_info = service.extract_spotify_info(spotify_url)
        
        if 'error' in url_info:
            return JsonResponse(url_info, status=400)
        
        if url_info['type'] == 'track':
            # Download de música única
            result = service.download_track(spotify_url, request.user)
            
            if result.get('success'):
                return JsonResponse({
                    'success': True,
                    'type': 'track',
                    'message': f"✅ Música '{result['metadata']['title']}' baixada com sucesso!",
                    'download_url': f'/download-file/?file={result["filename"]}',
                    'metadata': result['metadata']
                })
            else:
                return JsonResponse({
                    'error': result.get('error', 'Erro desconhecido'),
                    'needs_subscription': result.get('needs_subscription', False)
                }, status=400)
        
        elif url_info['type'] in ['playlist', 'album']:
            # Download de playlist/álbum
            result = service.download_playlist(spotify_url, request.user)
            
            if 'error' in result:
                return JsonResponse({
                    'error': result['error'],
                    'needs_subscription': result.get('needs_subscription', False)
                }, status=400)
            
            # Preparar informações do resultado
            successful_count = len(result['successful_downloads'])
            failed_count = len(result['failed_downloads'])
            
            message = f"📥 Playlist processada! "
            message += f"✅ {successful_count} músicas baixadas"
            
            if failed_count > 0:
                message += f", ❌ {failed_count} falharam"
            
            if result['skipped_tracks']:
                skipped_count = len(result['skipped_tracks'])
                message += f", ⏭️ {skipped_count} puladas (limite atingido)"
            
            return JsonResponse({
                'success': True,
                'type': 'playlist',
                'message': message,
                'results': {
                    'total': result['total_tracks'],
                    'successful': successful_count,
                    'failed': failed_count,
                    'skipped': len(result['skipped_tracks']),
                    'downloads': result['successful_downloads']
                }
            })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    
    except Exception as e:
        return JsonResponse({
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@login_required
def download_file(request):
    """
    Endpoint para servir arquivos de música baixados.
    Verifica permissões e serve o arquivo solicitado.
    
    Args:
        request: Objeto de requisição HTTP (GET)
        
    Returns:
        FileResponse: Arquivo de música ou erro 404
    """
    filename = request.GET.get('file')
    
    if not filename:
        raise Http404("Arquivo não especificado")
    
    # Verificar se o usuário baixou este arquivo
    file_exists = DownloadHistory.objects.filter(
        user=request.user,
        file_path__icontains=filename,
        success=True
    ).exists()
    
    if not file_exists:
        raise Http404("Arquivo não encontrado ou sem permissão")
    
    # Construir caminho completo do arquivo
    import os
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    
    if not os.path.exists(file_path):
        raise Http404("Arquivo não encontrado no servidor")
    
    # Servir arquivo
    response = FileResponse(
        open(file_path, 'rb'),
        as_attachment=True,
        filename=filename
    )
    
    return response


@login_required
def historico(request):
    """
    Página com histórico completo de downloads do usuário.
    
    Args:
        request: Objeto de requisição HTTP
        
    Returns:
        HttpResponse: Página de histórico renderizada
    """
    downloads = DownloadHistory.objects.filter(
        user=request.user
    ).order_by('-download_date')
    
    context = {
        'downloads': downloads,
        'total_downloads': downloads.filter(success=True).count(),
        'failed_downloads': downloads.filter(success=False).count()
    }
    
    return render(request, 'historico.html', context)