"""
Views para BaixaFy Desktop Application
Sistema de downloads com controle de licença local
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from urllib.parse import urlparse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.core.paginator import Paginator

from .models import DesktopLicense, DownloadHistory, AppSettings
from .forms import ActivationForm, DownloadForm
from .license_manager import get_license_status, validate_license

# Configurar logging
logger = logging.getLogger('baixafy')


def home(request):
    """
    Página inicial - Dashboard do usuário
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        license = request.user.desktop_license
    except:
        # Criar licença se não existir
        license = DesktopLicense.objects.create(
            user=request.user,
            license_type='trial',
            max_downloads=10  # 10 downloads no trial
        )
    
    # Verificar status da licença segura
    secure_license_status = get_license_status()
    
    # Estatísticas do usuário
    recent_downloads = DownloadHistory.objects.filter(user=request.user)[:5]
    total_downloads = DownloadHistory.objects.filter(user=request.user).count()
    
    # Determinar status real baseado na licença segura
    if secure_license_status['status'] == 'active':
        can_download = True
        downloads_remaining = float('inf')  # Ilimitado
        days_remaining = secure_license_status['days_remaining']
        license_message = f"Licença Premium ativa ({days_remaining} dias restantes)"
    elif secure_license_status['status'] == 'expired':
        can_download = False
        downloads_remaining = 0
        days_remaining = 0
        license_message = "Licença expirada - Renove para continuar"
    else:  # trial
        can_download = license.downloads_used < 10
        downloads_remaining = 10 - license.downloads_used
        days_remaining = 0
        license_message = f"Modo Trial ({downloads_remaining} downloads restantes)"
    
    context = {
        'license': license,
        'recent_downloads': recent_downloads,
        'total_downloads': total_downloads,
        'can_download': can_download,
        'downloads_remaining': downloads_remaining,
        'days_remaining': days_remaining,
        'license_message': license_message,
        'secure_license_status': secure_license_status,
    }
    
    return render(request, 'core/home.html', context)


def register_view(request):
    """
    Registro de novo usuário
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Você tem 1 download grátis.')
            # Login automático após registro
            user = authenticate(username=user.username, password=form.cleaned_data['password1'])
            if user:
                login(request, user)
                return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """
    Login do usuário
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bem-vindo de volta, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """
    Logout do usuário
    """
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')


@login_required
def download_music(request):
    """
    Página principal de download de música com sistema de licenciamento seguro
    """
    try:
        license = request.user.desktop_license
    except:
        license = DesktopLicense.objects.create(
            user=request.user,
            license_type='trial',
            max_downloads=10
        )
    
    # Verificar licença segura
    secure_license_status = get_license_status()
    
    # Determinar se pode baixar
    can_download = False
    error_message = None
    
    if secure_license_status['status'] == 'active':
        can_download = True  # Licença premium ativa
    elif secure_license_status['status'] == 'trial':
        # Modo trial - verificar limite de 10 downloads
        if license.downloads_used < 10:
            can_download = True
        else:
            error_message = "Você já usou seus 10 downloads gratuitos! Ative sua licença para continuar."
    else:  # expired
        error_message = "Sua licença expirou! Renove para continuar baixando."
    
    if request.method == 'POST':
        form = DownloadForm(request.POST)
        if form.is_valid():
            if not can_download:
                messages.error(request, error_message)
                return redirect('activate_license')
            
            spotify_url = form.cleaned_data['spotify_url']
            
            # Processar download
            download_result = process_download(request.user, spotify_url)
            
            if download_result['success']:
                messages.success(request, f'✅ Download concluído: {download_result["track_name"]}')
                
                # Incrementar contador apenas se for trial
                if secure_license_status['status'] == 'trial':
                    license.increment_download_count()
                
                return redirect('download_history')
            else:
                messages.error(request, f'❌ Erro no download: {download_result["error"]}')
    else:
        form = DownloadForm()
    
    # Calcular downloads restantes
    if secure_license_status['status'] == 'active':
        downloads_remaining = float('inf')  # Ilimitado
    else:
        downloads_remaining = max(0, 10 - license.downloads_used)
    
    context = {
        'form': form,
        'license': license,
        'can_download': can_download,
        'downloads_remaining': downloads_remaining,
        'error_message': error_message,
        'secure_license_status': secure_license_status,
    }
    
    return render(request, 'core/download.html', context)


def process_download(user, spotify_url):
    """
    Processa o download da música usando spotDL
    
    Args:
        user: Usuário que está baixando
        spotify_url: URL do Spotify
    
    Returns:
        dict: Resultado do download
    """
    try:
        # Criar registro de download
        download_record = DownloadHistory.objects.create(
            user=user,
            spotify_url=spotify_url,
            status='pending'
        )
        
        # Preparar diretório de download
        downloads_dir = settings.BAIXAFY_SETTINGS['DOWNLOADS_PATH']
        user_dir = downloads_dir / f'user_{user.id}'
        user_dir.mkdir(exist_ok=True)
        
        # Atualizar status
        download_record.status = 'downloading'
        download_record.save()
        
        # Comando spotDL
        spotdl_cmd = [
            'python', '-m', 'spotdl',
            '--output', str(user_dir),
            '--format', 'mp3',
            '--bitrate', '320k',
            spotify_url
        ]
        
        logger.info(f"Executando comando: {' '.join(spotdl_cmd)}")
        
        # Executar spotDL
        result = subprocess.run(
            spotdl_cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos timeout
            cwd=str(settings.BASE_DIR)
        )
        
        if result.returncode == 0:
            # Sucesso - encontrar arquivo baixado
            mp3_files = list(user_dir.glob('*.mp3'))
            if mp3_files:
                latest_file = max(mp3_files, key=os.path.getctime)
                
                # Extrair informações do arquivo
                track_info = extract_track_info(str(latest_file))
                
                # Atualizar registro
                download_record.track_name = track_info.get('title', 'Unknown')
                download_record.artist_name = track_info.get('artist', 'Unknown')
                download_record.album_name = track_info.get('album', 'Unknown')
                download_record.file_path = str(latest_file)
                download_record.file_size = latest_file.stat().st_size if latest_file.exists() else 0
                download_record.status = 'completed'
                download_record.save()
                
                logger.info(f"Download concluído: {latest_file}")
                
                return {
                    'success': True,
                    'track_name': download_record.track_name,
                    'file_path': str(latest_file),
                    'download_id': download_record.id
                }
            else:
                raise Exception("Nenhum arquivo MP3 encontrado após download")
        else:
            raise Exception(f"spotDL falhou: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        error_msg = "Download cancelado por timeout (5 minutos)"
        logger.error(error_msg)
        download_record.status = 'failed'
        download_record.error_message = error_msg
        download_record.save()
        return {'success': False, 'error': error_msg}
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Erro no download: {error_msg}")
        download_record.status = 'failed'
        download_record.error_message = error_msg
        download_record.save()
        return {'success': False, 'error': error_msg}


def extract_track_info(file_path):
    """
    Extrai informações de metadata do arquivo MP3
    """
    try:
        # Usar mutagen para extrair metadata (se disponível)
        from mutagen.mp3 import MP3
        from mutagen.id3 import ID3NoHeaderError
        
        audio = MP3(file_path)
        return {
            'title': str(audio.get('TIT2', ['Unknown'])[0]),
            'artist': str(audio.get('TPE1', ['Unknown'])[0]),
            'album': str(audio.get('TALB', ['Unknown'])[0]),
        }
    except:
        # Fallback: extrair do nome do arquivo
        filename = Path(file_path).stem
        parts = filename.split(' - ')
        if len(parts) >= 2:
            return {
                'artist': parts[0].strip(),
                'title': parts[1].strip(),
                'album': 'Unknown'
            }
        return {
            'title': filename,
            'artist': 'Unknown',
            'album': 'Unknown'
        }


@login_required
def activate_license(request):
    """
    Página de ativação de licença com sistema seguro
    """
    try:
        license = request.user.desktop_license
    except:
        license = DesktopLicense.objects.create(
            user=request.user,
            license_type='trial',
            max_downloads=10
        )
    
    # Verificar se já tem licença ativa
    secure_license_status = get_license_status()
    if secure_license_status['status'] == 'active':
        messages.info(request, f'Você já tem uma licença ativa! ({secure_license_status["days_remaining"]} dias restantes)')
        return redirect('home')
    
    if request.method == 'POST':
        form = ActivationForm(request.POST)
        if form.is_valid():
            activation_code = form.cleaned_data['activation_code']
            
            # Validar com sistema seguro
            validation_result = validate_license(activation_code)
            
            if validation_result['valid']:
                # Atualizar licença local também
                license.license_type = 'activated'
                license.activation_code = activation_code
                license.activation_date = timezone.now()
                license.expiry_date = timezone.now() + timedelta(days=validation_result['days'])
                license.max_downloads = 999999  # Ilimitado
                license.save()
                
                messages.success(
                    request, 
                    f'🎉 Licença ativada com sucesso! '
                    f'Você agora tem downloads ilimitados por {validation_result["days"]} dias.'
                )
                return redirect('home')
            else:
                messages.error(request, f'❌ {validation_result["error"]}')
    else:
        form = ActivationForm()
    
    context = {
        'form': form,
        'license': license,
        'secure_license_status': secure_license_status,
    }
    
    return render(request, 'core/activate.html', context)


@login_required
def download_history(request):
    """
    Histórico de downloads do usuário
    """
    downloads = DownloadHistory.objects.filter(user=request.user).order_by('-download_date')
    
    # Paginação
    paginator = Paginator(downloads, 10)  # 10 downloads por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'downloads': page_obj.object_list,
    }
    
    return render(request, 'core/history.html', context)


@login_required
def download_file(request, download_id):
    """
    Serve arquivo para download direto
    """
    download = get_object_or_404(DownloadHistory, id=download_id, user=request.user)
    
    if not download.file_exists:
        messages.error(request, 'Arquivo não encontrado. Pode ter sido removido.')
        return redirect('download_history')
    
    try:
        file_path = Path(download.file_path)
        response = FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=file_path.name
        )
        return response
    except Exception as e:
        logger.error(f"Erro ao servir arquivo: {e}")
        messages.error(request, 'Erro ao baixar arquivo.')
        return redirect('download_history')


@login_required
@require_http_methods(["POST"])
def delete_download(request, download_id):
    """
    Remove um download do histórico e deleta o arquivo
    """
    download = get_object_or_404(DownloadHistory, id=download_id, user=request.user)
    
    try:
        # Deletar arquivo físico se existir
        if download.file_exists:
            os.remove(download.file_path)
        
        # Deletar registro
        track_name = download.track_name or 'Unknown'
        download.delete()
        
        messages.success(request, f'"{track_name}" removido com sucesso.')
    except Exception as e:
        logger.error(f"Erro ao deletar download: {e}")
        messages.error(request, 'Erro ao remover arquivo.')
    
    return redirect('download_history')


@login_required
def profile(request):
    """
    Página de perfil do usuário
    """
    try:
        license = request.user.desktop_license
    except:
        license = DesktopLicense.objects.create(
            user=request.user,
            license_type='trial',
            max_downloads=1
        )
    
    # Estatísticas
    total_downloads = DownloadHistory.objects.filter(user=request.user).count()
    successful_downloads = DownloadHistory.objects.filter(user=request.user, status='completed').count()
    
    context = {
        'license': license,
        'total_downloads': total_downloads,
        'successful_downloads': successful_downloads,
    }
    
    return render(request, 'core/profile.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def check_url(request):
    """
    API endpoint para validar URL do Spotify
    """
    try:
        data = json.loads(request.body)
        url = data.get('url', '')
        
        # Validar URL do Spotify
        parsed = urlparse(url)
        
        if 'spotify.com' not in parsed.netloc:
            return JsonResponse({
                'valid': False,
                'error': 'URL deve ser do Spotify'
            })
        
        if not any(path in parsed.path for path in ['/track/', '/playlist/', '/album/']):
            return JsonResponse({
                'valid': False,
                'error': 'URL deve ser de uma música, playlist ou álbum'
            })
        
        return JsonResponse({
            'valid': True,
            'type': 'track' if '/track/' in parsed.path else 'playlist' if '/playlist/' in parsed.path else 'album'
        })
        
    except Exception as e:
        return JsonResponse({
            'valid': False,
            'error': 'Erro ao validar URL'
        })


def about(request):
    """
    Página sobre o BaixaFy Desktop
    """
    app_version = AppSettings.get_setting('app_version', '1.0.0')
    
    context = {
        'app_version': app_version,
    }
    
    return render(request, 'core/about.html', context)