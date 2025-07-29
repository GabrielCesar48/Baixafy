# apps/core/views.py - VERSÃO SIMPLIFICADA
import json
import os
import uuid
import zipfile
import threading
import time
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages

from apps.baixador.services import get_spotify_service

# Dicionário global para armazenar progresso dos downloads
download_progress_tracker = {}

def home(request):
    """
    Página única do BaixaFy - Interface simples para downloads.
    """
    # Verificar se serviço está funcionando
    service = get_spotify_service()
    service_status = None
    
    if service:
        service_status = service.health_check()
    
    context = {
        'service_status': service_status,
    }
    
    # Mostrar aviso se houver problema
    if not service or (service_status and service_status.get('status') == 'error'):
        messages.warning(
            request, 
            '⚠️ Serviço temporariamente indisponível. Verifique se FFmpeg está instalado.'
        )
    
    return render(request, 'home.html', context)


@csrf_exempt
def download_music(request):
    """
    Inicia o download de música/playlist via AJAX.
    Funciona igual ao script baixar.py, mas via web.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        spotify_url = data.get('url', '').strip()
        
        if not spotify_url:
            return JsonResponse({'error': 'URL do Spotify é obrigatória'}, status=400)
        
        # Validar URL do Spotify
        if not _is_valid_spotify_url(spotify_url):
            return JsonResponse({'error': 'URL inválida. Use links do Spotify.'}, status=400)
        
        # Gerar ID único para este download
        download_id = str(uuid.uuid4())
        
        # Inicializar progresso
        download_progress_tracker[download_id] = {
            'status': 'starting',
            'progress': 0,
            'message': 'Iniciando download...',
            'current_track': '',
            'total_tracks': 0,
            'completed_tracks': 0,
            'download_path': None,
            'error': None
        }
        
        # Iniciar download em thread separada
        thread = threading.Thread(
            target=_process_download,
            args=(spotify_url, download_id)
        )
        thread.daemon = True
        thread.start()
        
        return JsonResponse({
            'success': True,
            'download_id': download_id,
            'message': 'Download iniciado com sucesso!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)


def download_progress(request):
    """
    Retorna o progresso atual de um download via AJAX.
    """
    download_id = request.GET.get('id')
    
    if not download_id or download_id not in download_progress_tracker:
        return JsonResponse({'error': 'Download não encontrado'}, status=404)
    
    progress_data = download_progress_tracker[download_id]
    
    return JsonResponse({
        'status': progress_data['status'],
        'progress': progress_data['progress'],
        'message': progress_data['message'],
        'current_track': progress_data['current_track'],
        'total_tracks': progress_data['total_tracks'],
        'completed_tracks': progress_data['completed_tracks'],
        'download_path': progress_data['download_path'],
        'error': progress_data['error']
    })


def download_file(request, filename):
    """
    Serve arquivo para download e remove após o download.
    """
    file_path = Path(settings.MEDIA_ROOT) / filename
    
    if not file_path.exists():
        raise Http404("Arquivo não encontrado")
    
    try:
        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=filename
        )
        
        # Agendar remoção do arquivo após 1 hora
        threading.Timer(3600, _cleanup_file, args=[file_path]).start()
        
        return response
        
    except Exception as e:
        raise Http404(f"Erro ao baixar arquivo: {str(e)}")


def _is_valid_spotify_url(url):
    """
    Valida se a URL é do Spotify.
    """
    return ('open.spotify.com' in url and 
            ('track/' in url or 'playlist/' in url or 'album/' in url))


def _process_download(spotify_url, download_id):
    """
    Processa o download em background.
    Replica EXATAMENTE o comportamento do script baixar.py.
    """
    try:
        service = get_spotify_service()
        if not service:
            _update_progress(download_id, 'error', 0, 'Serviço indisponível')
            return
        
        # Verificar health do serviço
        health = service.health_check()
        if health['status'] == 'error':
            _update_progress(download_id, 'error', 0, health['message'])
            return
        
        # Atualizar progresso: iniciando
        _update_progress(download_id, 'downloading', 5, 'Verificando URL...')
        
        # Criar pasta temporária para o download
        temp_dir = Path(settings.MEDIA_ROOT) / f"temp_{download_id}"
        temp_dir.mkdir(exist_ok=True)
        
        # Atualizar progresso
        _update_progress(download_id, 'downloading', 15, 'Iniciando download via SpotDL...')
        
        # USAR SPOTDL DIRETAMENTE (igual ao script baixar.py)
        downloaded_files = service.download_spotify_url(spotify_url, str(temp_dir))
        
        if not downloaded_files:
            _update_progress(download_id, 'error', 0, 'Nenhuma música foi baixada. Verifique a URL.')
            _cleanup_temp_dir(temp_dir)
            return
        
        # Simular progresso durante o download
        total_files = len(downloaded_files)
        for i, file_path in enumerate(downloaded_files, 1):
            progress = 15 + (i * 65 // total_files)  # 15-80%
            file_name = Path(file_path).stem
            _update_progress(
                download_id,
                'downloading',
                progress,
                f'Processando: {file_name}',
                file_name,
                total_files,
                i
            )
            time.sleep(0.5)  # Simular tempo de processamento
        
        # Criar arquivo ZIP
        _update_progress(download_id, 'zipping', 85, 'Criando arquivo ZIP...')
        
        zip_filename = f"baixafy_download_{download_id[:8]}.zip"
        zip_path = Path(settings.MEDIA_ROOT) / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in downloaded_files:
                file_path_obj = Path(file_path)
                if file_path_obj.exists():
                    # Manter apenas o nome do arquivo no ZIP
                    zipf.write(file_path_obj, file_path_obj.name)
        
        # Limpar arquivos temporários
        _cleanup_temp_dir(temp_dir)
        
        # Download concluído
        _update_progress(
            download_id, 
            'completed', 
            100, 
            f'Download concluído! {len(downloaded_files)} música(s) baixada(s).',
            download_path=zip_filename
        )
        
    except Exception as e:
        _update_progress(download_id, 'error', 0, f'Erro no download: {str(e)}')
        # Tentar limpar pasta temporária mesmo com erro
        try:
            temp_dir = Path(settings.MEDIA_ROOT) / f"temp_{download_id}"
            _cleanup_temp_dir(temp_dir)
        except:
            pass


def _cleanup_temp_dir(temp_dir):
    """
    Remove pasta temporária e todos os arquivos.
    """
    try:
        if temp_dir.exists():
            for file_path in temp_dir.iterdir():
                file_path.unlink()
            temp_dir.rmdir()
    except Exception as e:
        print(f"Erro ao limpar pasta temporária: {e}")


def _update_progress(download_id, status, progress, message, current_track='', total_tracks=0, completed_tracks=0, download_path=None):
    """
    Atualiza o progresso do download.
    """
    if download_id in download_progress_tracker:
        progress_data = download_progress_tracker[download_id]
        progress_data.update({
            'status': status,
            'progress': progress,
            'message': message,
            'current_track': current_track,
        })
        
        if total_tracks > 0:
            progress_data['total_tracks'] = total_tracks
            
        if completed_tracks > 0:
            progress_data['completed_tracks'] = completed_tracks
            
        if download_path:
            progress_data['download_path'] = download_path


def _cleanup_file(file_path):
    """
    Remove arquivo após delay.
    """
    try:
        if Path(file_path).exists():
            Path(file_path).unlink()
            print(f"Arquivo removido: {file_path}")
    except Exception as e:
        print(f"Erro ao remover arquivo {file_path}: {e}")