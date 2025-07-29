# apps/baixador/services.py
import os
import re
import json
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from pathlib import Path
import time

from spotdl import Spotdl
from spotdl.utils.config import get_config
from django.conf import settings
from apps.users.models import CustomUser, DownloadHistory


class SpotifyDownloadService:
    """
    Serviço responsável por gerenciar downloads de músicas do Spotify.
    Utiliza a biblioteca spotDL para baixar áudios via YouTube.
    """
    
    def __init__(self):
        """
        Inicializa o serviço de download configurando o spotDL.
        """
        self.download_path = Path(settings.MEDIA_ROOT)
        self.download_path.mkdir(exist_ok=True)
        
        # Configurar e inicializar spotDL
        self._setup_spotdl()
    
    def _setup_spotdl(self):
        """
        Configura o spotDL criando arquivo de config se necessário.
        """
        try:
            # Tentar criar arquivo de configuração se não existir
            self._ensure_config_exists()
            
            # CORREÇÃO: SpotDL precisa de credenciais obrigatórias
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            # Se não tiver credenciais, usar valores padrão vazios
            if not client_id or not client_secret:
                print("⚠️ Credenciais do Spotify não configuradas. Usando valores padrão.")
                client_id = ""
                client_secret = ""
            
            try:
                self.spotdl = Spotdl(client_id=client_id, client_secret=client_secret)
                print("✅ SpotDL inicializado")
            except Exception as e:
                print(f"⚠️ Erro ao inicializar: {e}")
                # Tentar com credenciais vazias explicitamente
                self.spotdl = Spotdl(client_id="", client_secret="")
                print("✅ SpotDL inicializado com credenciais vazias")
                
        except Exception as e:
            print(f"❌ Erro crítico: {e}")
            raise Exception(f"Falha na inicialização do SpotDL: {str(e)}")
    
    def _ensure_config_exists(self):
        """
        Garante que o arquivo de configuração do spotDL existe.
        """
        try:
            config = get_config()
            print("✅ Configuração do SpotDL encontrada")
        except Exception:
            print("⚠️ Criando configuração...")
            try:
                subprocess.run(['spotdl', '--generate-config'], capture_output=True, timeout=30)
                print("✅ Configuração criada")
            except Exception as e:
                print(f"⚠️ Erro ao criar config: {e}")
    
    def extract_spotify_info(self, url: str) -> Dict:
        """
        Extrai informações básicas de uma URL do Spotify.
        """
        try:
            url = url.strip()
            
            if 'track/' in url:
                match = re.search(r'track/([a-zA-Z0-9]+)', url)
                return {'type': 'track', 'id': match.group(1), 'url': url, 'success': True} if match else {'error': 'URL inválida'}
            elif 'playlist/' in url:
                match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
                return {'type': 'playlist', 'id': match.group(1), 'url': url, 'success': True} if match else {'error': 'URL inválida'}
            elif 'album/' in url:
                match = re.search(r'album/([a-zA-Z0-9]+)', url)
                return {'type': 'album', 'id': match.group(1), 'url': url, 'success': True} if match else {'error': 'URL inválida'}
            else:
                return {'error': 'Tipo não suportado. Use links de música, playlist ou álbum.'}
        except Exception as e:
            return {'error': f'Erro ao processar URL: {str(e)}'}
    
    def get_track_metadata(self, url: str) -> Dict:
        """
        Obtém metadados de uma música do Spotify.
        """
        try:
            if not hasattr(self, 'spotdl'):
                return {'error': 'Serviço não configurado'}
            
            songs = self.spotdl.search([url])
            if not songs:
                return {'error': 'Música não encontrada'}
            
            song = songs[0]
            return {
                'success': True,
                'name': song.name,
                'artists': song.artists,
                'album': song.album_name,
                'duration': f"{song.duration // 60}:{song.duration % 60:02d}",
                'cover_url': song.cover_url or '',
                'spotify_url': url,
                'year': getattr(song, 'year', 'N/A')
            }
        except Exception as e:
            error_msg = str(e)
            if 'Config file not found' in error_msg:
                return {'error': 'Execute: spotdl --generate-config'}
            elif 'FFmpeg' in error_msg:
                return {'error': 'FFmpeg não instalado'}
            else:
                return {'error': f'Erro: {error_msg}'}
    
    def get_playlist_info(self, url: str) -> Dict:
        """
        NOVO: Obtém informações de uma playlist do Spotify.
        """
        try:
            if not hasattr(self, 'spotdl'):
                return {'error': 'Serviço não configurado'}
            
            songs = self.spotdl.search([url])
            if not songs:
                return {'error': 'Playlist não encontrada'}
            
            tracks = []
            for i, song in enumerate(songs):
                tracks.append({
                    'index': i + 1,
                    'name': song.name,
                    'artists': song.artists,
                    'album': song.album_name,
                    'duration': f"{song.duration // 60}:{song.duration % 60:02d}",
                    'cover_url': song.cover_url or '',
                    'year': getattr(song, 'year', 'N/A')
                })
            
            return {
                'success': True,
                'name': f"Playlist com {len(tracks)} músicas",
                'total_tracks': len(tracks),
                'tracks': tracks,
                'owner': 'Usuário do Spotify',
                'spotify_url': url
            }
        except Exception as e:
            error_msg = str(e)
            if 'Config file not found' in error_msg:
                return {'error': 'Execute: spotdl --generate-config'}
            elif 'FFmpeg' in error_msg:
                return {'error': 'FFmpeg não instalado'}
            else:
                return {'error': f'Erro: {error_msg}'}
    
    def can_user_download(self, user: CustomUser) -> Tuple[bool, str]:
        """
        Verifica se o usuário pode fazer download.
        """
        if user.is_premium_active():
            return True, "Premium ativo"
        
        free_downloads = DownloadHistory.objects.filter(user=user, is_premium_download=False).count()
        if free_downloads >= 1:
            return False, "Limite gratuito atingido. Assine Premium!"
        
        return True, "Download gratuito disponível"
    
    def download_track(self, url: str, user: CustomUser) -> Dict:
        """
        Realiza o download de uma música do Spotify.
        """
        try:
            can_download, message = self.can_user_download(user)
            if not can_download:
                return {'error': message}
            
            if not hasattr(self, 'spotdl'):
                return {'error': 'Serviço não configurado'}
            
            # Obter metadados
            metadata = self.get_track_metadata(url)
            if 'error' in metadata:
                return metadata
            
            print(f"🎵 Baixando: {metadata.get('name', 'N/A')}")
            
            # Download
            songs = self.spotdl.search([url])
            if not songs:
                return {'error': 'Música não encontrada'}
            
            self.spotdl.download(songs)
            
            # Procurar arquivo baixado
            downloaded_files = []
            current_time = time.time()
            
            for item in self.download_path.iterdir():
                if item.is_file() and item.suffix.lower() == '.mp3':
                    if (current_time - item.stat().st_mtime) < 300:  # 5 minutos
                        downloaded_files.append(item)
            
            if not downloaded_files:
                return {'error': 'Arquivo não encontrado após download'}
            
            downloaded_file = max(downloaded_files, key=lambda x: x.stat().st_mtime)
            
            # Registrar no histórico
            is_premium = user.is_premium_active()
            DownloadHistory.objects.create(
                user=user,
                spotify_url=url,
                song_name=metadata.get('name', 'Desconhecido'),
                artist_name=', '.join(metadata.get('artists', ['Desconhecido'])),
                file_path=str(downloaded_file),
                is_premium_download=is_premium
            )
            
            print(f"✅ Download concluído: {downloaded_file.name}")
            
            return {
                'success': True,
                'file_path': str(downloaded_file),
                'file_name': downloaded_file.name,
                'download_url': f"{settings.MEDIA_URL}{downloaded_file.name}",
                'metadata': metadata,
                'is_premium_download': is_premium
            }
            
        except Exception as e:
            error_msg = str(e)
            if 'ffmpeg' in error_msg.lower():
                return {'error': 'FFmpeg não instalado'}
            else:
                return {'error': f'Erro no download: {error_msg}'}
    
    def health_check(self) -> Dict:
        """
        Verifica se o serviço está funcionando.
        """
        try:
            if not hasattr(self, 'spotdl'):
                return {'status': 'error', 'message': 'SpotDL não inicializado'}
            
            if not self.download_path.exists():
                return {'status': 'error', 'message': 'Diretório não existe'}
            
            # Verificar FFmpeg
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
                ffmpeg_ok = True
            except:
                ffmpeg_ok = False
            
            return {
                'status': 'ok' if ffmpeg_ok else 'error',
                'message': 'Funcionando' if ffmpeg_ok else 'FFmpeg não instalado',
                'download_path': str(self.download_path),
                'ffmpeg_available': ffmpeg_ok
            }
        except Exception as e:
            return {'status': 'error', 'message': f'Erro: {str(e)}'}


# Instância global
spotify_service = None

def get_spotify_service():
    """Retorna a instância do serviço."""
    global spotify_service
    if spotify_service is None:
        try:
            spotify_service = SpotifyDownloadService()
            print("✅ SpotifyDownloadService inicializado")
        except Exception as e:
            print(f"❌ Erro ao inicializar: {e}")
            return None
    return spotify_service

# Tentar inicializar
try:
    spotify_service = SpotifyDownloadService()
    print("✅ SpotifyDownloadService inicializado")
except Exception as e:
    print(f"❌ Erro ao inicializar: {e}")
    spotify_service = None