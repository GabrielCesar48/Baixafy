# apps/core/views.py
import json
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.conf import settings
import subprocess
import shutil

from apps.users.forms import DownloadForm
from apps.baixador.services import spotify_service
from apps.users.models import DownloadHistory

User = get_user_model()


def verificar_ffmpeg():
    """Verifica se FFmpeg está disponível no sistema."""
    try:
        # Verifica se FFmpeg está no PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            print(f"FFmpeg encontrado em: {ffmpeg_path}")
            return True
        else:
            print("FFmpeg não encontrado no PATH")
            return False
    except Exception as e:
        print(f"Erro ao verificar FFmpeg: {e}")
        return False

def home(request):
    """Página inicial do BaixaFy."""
    return render(request, 'home.html')


@login_required
def painel(request):
    """Painel principal do usuário logado."""
    user = request.user
    
    # Verificar se serviço está funcionando
    service_status = None
    if spotify_service:
        service_status = spotify_service.health_check()
    
    context = {
        'user': user,
        'is_premium': user.is_premium_active(),
        'days_remaining': user.days_remaining(),
        'can_download': user.can_download(),
        'free_downloads_used': user.free_downloads_used,
        'total_downloads': user.total_downloads,
        'download_form': DownloadForm(),
        'recent_downloads': DownloadHistory.objects.filter(user=user, success=True).order_by('-download_date')[:5],
        'service_status': service_status
    }
    
    # CORREÇÃO: Mostrar aviso apenas se realmente houver problema
    if not spotify_service or (service_status and service_status.get('status') == 'error'):
        if service_status and 'FFmpeg' in service_status.get('message', ''):
            messages.warning(request, '⚠️ FFmpeg não está instalado. Execute install_ffmpeg.bat como Administrador.')
        else:
            messages.warning(request, '⚠️ Serviço de download temporariamente indisponível.')
    
    return render(request, 'painel.html', context)


@login_required
def pagamento(request):
    """Página de simulação de pagamento."""
    if request.method == 'POST':
        request.user.activate_premium(days=30)
        messages.success(request, f"🎉 Premium ativado com sucesso! 30 dias de downloads ilimitados.")
        return redirect('painel')
    
    return render(request, 'pagamento.html')


@login_required
@csrf_exempt
def get_spotify_info(request):
    """
    CORREÇÃO: Endpoint que agora suporta playlists também.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    # Aceitar JSON ou form data
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            spotify_url = data.get('spotify_url', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'JSON inválido'})
    else:
        spotify_url = request.POST.get('spotify_url', '').strip()
    
    if not spotify_url:
        return JsonResponse({'success': False, 'message': 'URL obrigatória'})
    
    # CORREÇÃO: Verificar se serviço está disponível
    if not spotify_service:
        return JsonResponse({
            'success': False,
            'message': 'Serviço indisponível. Verifique se FFmpeg está instalado.',
            'error_type': 'service_unavailable'
        })
    
    try:
        # Verificar tipo de URL
        url_info = spotify_service.extract_spotify_info(spotify_url)
        if 'error' in url_info:
            return JsonResponse({'success': False, 'message': url_info['error']})
        
        # CORREÇÃO: Processar músicas E playlists
        if url_info['type'] == 'track':
            metadata = spotify_service.get_track_metadata(spotify_url)
            
            if 'error' in metadata:
                return JsonResponse({'success': False, 'message': metadata['error']})
            
            return JsonResponse({
                'success': True,
                'type': 'track',
                'track_info': {
                    'name': metadata['name'],
                    'artists': metadata['artists'],
                    'album': metadata['album'],
                    'duration': metadata['duration'],
                    'cover_url': metadata['cover_url'],
                    'year': metadata.get('year', 'N/A')
                }
            })
            
        elif url_info['type'] == 'playlist':
            # NOVO: Suporte a playlists
            playlist_info = spotify_service.get_playlist_info(spotify_url)
            
            if 'error' in playlist_info:
                return JsonResponse({'success': False, 'message': playlist_info['error']})
            
            return JsonResponse({
                'success': True,
                'type': 'playlist',
                'playlist_info': {
                    'name': playlist_info['name'],
                    'total_tracks': playlist_info['total_tracks'],
                    'tracks': playlist_info['tracks'][:10],  # Primeiras 10
                    'owner': playlist_info.get('owner', 'Desconhecido')
                }
            })
            
        elif url_info['type'] == 'album':
            # Usar mesmo método de playlist
            album_info = spotify_service.get_playlist_info(spotify_url)
            
            if 'error' in album_info:
                return JsonResponse({'success': False, 'message': album_info['error']})
            
            return JsonResponse({
                'success': True,
                'type': 'album',
                'album_info': {
                    'name': album_info['name'],
                    'total_tracks': album_info['total_tracks'],
                    'tracks': album_info['tracks'][:10],
                    'artist': album_info.get('owner', 'Desconhecido')
                }
            })
        else:
            return JsonResponse({'success': False, 'message': 'Tipo não suportado'})
        
    except Exception as e:
        print(f"❌ Erro em get_spotify_info: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Erro interno', 'error_type': 'internal_error'})


@login_required
@csrf_exempt
def download_music(request):
    """Endpoint para baixar música do Spotify."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'})
    
    # Aceitar JSON ou form data
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            spotify_url = data.get('spotify_url', '').strip()
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'JSON inválido'})
    else:
        spotify_url = request.POST.get('spotify_url', '').strip()
    
    user = request.user
    
    if not spotify_url:
        return JsonResponse({'success': False, 'message': 'URL obrigatória'})
    
    if not spotify_service:
        return JsonResponse({
            'success': False,
            'message': 'Serviço indisponível. FFmpeg pode estar ausente.',
            'error_type': 'service_unavailable'
        })
    
    if not user.can_download():
        return JsonResponse({
            'success': False,
            'message': '⛔ Limite atingido! Assine Premium para downloads ilimitados.',
            'needs_subscription': True
        })
    
    try:
        result = spotify_service.download_track(spotify_url, user)
        
        if 'error' in result:
            return JsonResponse({'success': False, 'message': result['error']})
        
        return JsonResponse({
            'success': True,
            'message': f'🎵 Download concluído: {result["file_name"]}',
            'download_url': result['download_url'],
            'file_name': result['file_name'],
            'metadata': result['metadata'],
            'is_premium_download': result['is_premium_download']
        })
        
    except Exception as e:
        print(f"❌ Erro em download_music: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Erro interno no download'})


@login_required
def download_file(request, filename):
    """Serve arquivos de download para usuários autenticados."""
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, filename)
        
        if not os.path.exists(file_path):
            raise Http404("Arquivo não encontrado")
        
        # Verificar se usuário tem permissão
        download_history = DownloadHistory.objects.filter(
            user=request.user,
            file_path__contains=filename
        ).first()
        
        if not download_history:
            raise Http404("Sem permissão para este arquivo")
        
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
        return response
        
    except Exception as e:
        print(f"❌ Erro ao servir arquivo {filename}: {str(e)}")
        raise Http404("Erro ao acessar arquivo")


@login_required  
def historico(request):
    """Página de histórico simples."""
    downloads = DownloadHistory.objects.filter(user=request.user).order_by('-download_date')
    return render(request, 'historico.html', {'downloads': downloads})