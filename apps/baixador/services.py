# apps/baixador/services.py
import os
import re
import json
import subprocess
import tempfile
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from pathlib import Path

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
            
            # Obter configuração padrão
            config = get_config()
            
            # Personalizar configurações
            config["output"] = str(self.download_path)
            config["format"] = "mp3"
            config["bitrate"] = "192k"
            config["threads"] = 4
            config["song_format"] = "{artists} - {title}"
            config["restrict_filenames"] = True
            config["overwrite"] = "metadata"
            
            # Tentar inicializar com credenciais do Spotify
            try:
                client_id = os.getenv('SPOTIFY_CLIENT_ID')
                client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
                
                if client_id and client_secret:
                    self.spotdl = Spotdl(
                        client_id=client_id,
                        client_secret=client_secret,
                        config=config
                    )
                    print("✅ SpotDL inicializado com credenciais do Spotify")
                else:
                    # Modo público (sem credenciais)
                    self.spotdl = Spotdl(config=config)
                    print("⚠️ SpotDL inicializado sem credenciais (modo público)")
                    
            except Exception as e:
                print(f"⚠️ Erro ao inicializar com credenciais: {e}")
                # Fallback para modo público
                self.spotdl = Spotdl(config=config)
                
        except Exception as e:
            print(f"❌ Erro crítico ao configurar SpotDL: {e}")
            raise Exception(f"Falha na inicialização do SpotDL: {str(e)}")
    
    def _ensure_config_exists(self):
        """
        Garante que o arquivo de configuração do spotDL existe.
        Se não existir, cria um automaticamente.
        """
        try:
            # Tentar obter config (isso falhará se não existir)
            config = get_config()
            print("✅ Arquivo de configuração do SpotDL encontrado")
            
        except Exception as config_error:
            print("⚠️ Arquivo de configuração não encontrado. Criando...")
            
            try:
                # Executar comando para gerar config
                result = subprocess.run(
                    ['spotdl', '--generate-config'], 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("✅ Arquivo de configuração criado com sucesso")
                else:
                    print(f"⚠️ Aviso ao criar config: {result.stderr}")
                    # Criar config manualmente
                    self._create_manual_config()
                    
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"⚠️ Erro ao executar spotdl --generate-config: {e}")
                # Criar config manualmente
                self._create_manual_config()
    
    def _create_manual_config(self):
        """
        Cria manualmente o arquivo de configuração do spotDL.
        """
        try:
            # Diretório de configuração do spotDL
            config_dir = Path.home() / '.spotdl'
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / 'config.json'
            
            # Configuração padrão
            default_config = {
                "client_id": "",
                "client_secret": "",
                "user_auth": False,
                "cache_path": str(config_dir / 'cache'),
                "audio_provider": "youtube-music",
                "lyrics_provider": "musixmatch",
                "playlist_numbering": False,
                "scan_for_songs": False,
                "m3u": False,
                "output": str(self.download_path),
                "overwrite": "skip",
                "format": "mp3",
                "bitrate": "192k",
                "ffmpeg": "ffmpeg",
                "threads": 4,
                "cookie_file": None,
                "restrict_filenames": True,
                "print_errors": False,
                "sponsor_block": False,
                "preload": False,
                "archive": None,
                "load_config": True,
                "log_level": "INFO",
                "simple_tui": False,
                "fetch_albums": False,
                "id3_separator": "/",
                "ytm_data": False,
                "add_unavailable": False,
                "generate_lrc": False,
                "force_update_metadata": False,
                "only_verified_results": False,
                "sync_without_deleting": False,
                "max_filename_length": 200,
                "yt_dlp_args": None,
                "detect_formats": None,
                "save_file": None,
                "filter_results": True,
                "search_query": None,
                "don_not_filter_results": False,
                "bitrate_str": "192k",
                "song_format": "{artists} - {title}",
                "album_format": "{album-artist}/{album}",
                "playlist_format": "{playlist-name}/{artists} - {title}",
                "restrict": False,
                "print_completion": False,
                "download_ffmpeg": False,
                "generate_config": False,
                "check_installed": False,
                "profile": False,
                "preload_mp3": False
            }
            
            # Salvar configuração
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            
            print(f"✅ Configuração manual criada em: {config_file}")
            
        except Exception as e:
            print(f"❌ Erro ao criar configuração manual: {e}")
            raise Exception(f"Não foi possível criar arquivo de configuração: {str(e)}")
    
    def extract_spotify_info(self, url: str) -> Dict:
        """
        Extrai informações básicas de uma URL do Spotify.
        
        Args:
            url (str): URL do Spotify
            
        Returns:
            Dict: Informações extraídas da URL
        """
        try:
            # Limpar URL
            url = url.strip()
            
            # Determinar tipo de conteúdo
            if 'track/' in url:
                content_type = 'track'
                match = re.search(r'track/([a-zA-Z0-9]+)', url)
            elif 'playlist/' in url:
                content_type = 'playlist'
                match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
            elif 'album/' in url:
                content_type = 'album'
                match = re.search(r'album/([a-zA-Z0-9]+)', url)
            else:
                return {'error': 'Tipo de conteúdo não suportado. Use links de música, playlist ou álbum.'}
            
            if not match:
                return {'error': 'URL do Spotify inválida'}
            
            track_id = match.group(1)
            
            return {
                'type': content_type,
                'id': track_id,
                'url': url,
                'success': True
            }
            
        except Exception as e:
            return {'error': f'Erro ao processar URL: {str(e)}'}
    
    def get_track_metadata(self, url: str) -> Dict:
        """
        Obtém metadados de uma música do Spotify.
        
        Args:
            url (str): URL da música no Spotify
            
        Returns:
            Dict: Metadados da música (título, artista, álbum, capa, etc.)
        """
        try:
            # Verificar se spotDL está configurado
            if not hasattr(self, 'spotdl'):
                return {'error': 'Serviço de download não está configurado'}
            
            # Usar spotDL para obter metadados
            songs = self.spotdl.search([url])
            
            if not songs:
                return {'error': 'Música não encontrada no Spotify'}
            
            song = songs[0]
            
            return {
                'success': True,
                'name': song.name,
                'artists': song.artists,
                'album': song.album_name,
                'duration': f"{song.duration // 60}:{song.duration % 60:02d}",
                'cover_url': song.cover_url or '',
                'spotify_url': url,
                'year': getattr(song, 'year', 'N/A'),
                'isrc': getattr(song, 'isrc', 'N/A'),
                'track_number': getattr(song, 'track_number', 'N/A'),
                'disc_number': getattr(song, 'disc_number', 'N/A')
            }
            
        except Exception as e:
            error_msg = str(e)
            if 'Config file not found' in error_msg:
                return {'error': 'Erro de configuração do SpotDL. Tente novamente.'}
            elif 'No results found' in error_msg:
                return {'error': 'Música não encontrada ou não disponível'}
            else:
                return {'error': f'Erro ao obter informações: {error_msg}'}
    
    def download_track(self, url: str, user: CustomUser) -> Dict:
        """
        Baixa uma única música do Spotify.
        
        Args:
            url (str): URL da música no Spotify
            user (CustomUser): Usuário solicitando o download
            
        Returns:
            Dict: Resultado do download com informações do arquivo
        """
        try:
            # Verificar se usuário pode baixar
            if not user.can_download():
                return {
                    'error': 'Limite de downloads atingido. Assine o plano premium!',
                    'needs_subscription': True
                }
            
            # Obter metadados primeiro
            metadata = self.get_track_metadata(url)
            if 'error' in metadata:
                return metadata
            
            # Preparar informações para download
            track_name = metadata['name']
            artist_name = ', '.join(metadata['artists'])
            album_name = metadata['album']
            
            print(f"🎵 Iniciando download: {artist_name} - {track_name}")
            
            # Baixar a música usando spotDL
            songs = self.spotdl.search([url])
            if not songs:
                return {'error': 'Música não encontrada para download'}
            
            # Realizar download
            downloaded_files, errors = self.spotdl.download(songs)
            
            if errors:
                error_msg = '; '.join([str(err) for err in errors])
                print(f"❌ Erros durante download: {error_msg}")
                
                # Registrar falha no histórico
                DownloadHistory.objects.create(
                    user=user,
                    spotify_url=url,
                    track_name=track_name,
                    artist_name=artist_name,
                    album_name=album_name,
                    success=False,
                    error_message=error_msg
                )
                
                return {'error': f'Erro no download: {error_msg}'}
            
            if not downloaded_files:
                return {'error': 'Nenhum arquivo foi baixado'}
            
            file_path = downloaded_files[0]
            filename = os.path.basename(file_path)
            
            print(f"✅ Download concluído: {filename}")
            
            # Registrar sucesso no histórico
            DownloadHistory.objects.create(
                user=user,
                spotify_url=url,
                track_name=track_name,
                artist_name=artist_name,
                album_name=album_name,
                file_path=str(file_path),
                file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                success=True
            )
            
            # Atualizar contador do usuário
            user.use_download()
            
            return {
                'success': True,
                'file_path': str(file_path),
                'filename': filename,
                'metadata': metadata,
                'download_url': self.get_file_url(str(file_path))
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erro durante download: {error_msg}")
            
            # Registrar falha no histórico
            DownloadHistory.objects.create(
                user=user,
                spotify_url=url,
                track_name=url,
                artist_name='Desconhecido',
                success=False,
                error_message=error_msg
            )
            
            # Tratar erros específicos
            if 'Config file not found' in error_msg:
                return {'error': 'Erro de configuração. Tente novamente em alguns instantes.'}
            elif 'ffmpeg' in error_msg.lower():
                return {'error': 'Erro de conversão de áudio. Verifique se o FFmpeg está instalado.'}
            elif 'youtube' in error_msg.lower():
                return {'error': 'Erro ao acessar o YouTube. Tente novamente mais tarde.'}
            else:
                return {'error': f'Erro no download: {error_msg}'}
    
    def get_file_url(self, file_path: str) -> str:
        """
        Gera URL para download do arquivo.
        
        Args:
            file_path (str): Caminho do arquivo no sistema
            
        Returns:
            str: URL para download
        """
        filename = os.path.basename(file_path)
        return f"{settings.MEDIA_URL}{filename}"
    
    def health_check(self) -> Dict:
        """
        Verifica se o serviço está funcionando corretamente.
        
        Returns:
            Dict: Status do serviço
        """
        try:
            # Verificar se spotDL está inicializado
            if not hasattr(self, 'spotdl'):
                return {
                    'status': 'error',
                    'message': 'SpotDL não está inicializado'
                }
            
            # Verificar se diretório de download existe
            if not self.download_path.exists():
                return {
                    'status': 'error',
                    'message': 'Diretório de download não existe'
                }
            
            # Verificar se tem permissão de escrita
            if not os.access(self.download_path, os.W_OK):
                return {
                    'status': 'error',
                    'message': 'Sem permissão de escrita no diretório de download'
                }
            
            return {
                'status': 'ok',
                'message': 'Serviço funcionando corretamente',
                'download_path': str(self.download_path),
                'spotdl_initialized': True
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Erro no health check: {str(e)}'
            }


# Instância global do serviço
try:
    spotify_service = SpotifyDownloadService()
    print("✅ SpotifyDownloadService inicializado com sucesso")
except Exception as e:
    print(f"❌ Erro ao inicializar SpotifyDownloadService: {e}")
    spotify_service = None