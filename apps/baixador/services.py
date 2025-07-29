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
            
            # Inicializar spotDL sem parâmetro config (CORREÇÃO DO BUG)
            try:
                client_id = os.getenv('SPOTIFY_CLIENT_ID')
                client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
                
                if client_id and client_secret:
                    # Inicializar com credenciais (SEM parâmetro config)
                    self.spotdl = Spotdl(
                        client_id=client_id,
                        client_secret=client_secret
                    )
                    print("✅ SpotDL inicializado com credenciais do Spotify")
                else:
                    # Modo público (sem credenciais e SEM parâmetro config)
                    self.spotdl = Spotdl()
                    print("⚠️ SpotDL inicializado sem credenciais (modo público)")
                    
            except Exception as e:
                print(f"⚠️ Erro ao inicializar com credenciais: {e}")
                # Fallback para modo público
                try:
                    self.spotdl = Spotdl()
                    print("✅ SpotDL inicializado em modo fallback")
                except Exception as fallback_error:
                    print(f"❌ Erro no fallback: {fallback_error}")
                    raise
                
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
            
            # Personalizar configurações importantes
            self._update_config_if_needed(config)
            
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
                    # Criar config manualmente como fallback
                    self._create_manual_config()
                    
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"⚠️ Erro ao executar spotdl --generate-config: {e}")
                # Criar config manualmente
                self._create_manual_config()
    
    def _update_config_if_needed(self, config):
        """
        Atualiza configurações importantes se necessário.
        """
        try:
            # Configurações importantes para o BaixaFy
            updates_needed = False
            
            if config.get("output") != str(self.download_path):
                config["output"] = str(self.download_path)
                updates_needed = True
            
            if config.get("format") != "mp3":
                config["format"] = "mp3"
                updates_needed = True
                
            if config.get("bitrate") != "192k":
                config["bitrate"] = "192k"
                updates_needed = True
            
            # Configurações otimizadas
            optimal_settings = {
                "song_format": "{artists} - {title}",
                "restrict_filenames": True,
                "overwrite": "metadata",
                "threads": 4,
                "audio_provider": "youtube-music"
            }
            
            for key, value in optimal_settings.items():
                if config.get(key) != value:
                    config[key] = value
                    updates_needed = True
            
            if updates_needed:
                self._save_config(config)
                print("✅ Configuração do SpotDL atualizada")
                
        except Exception as e:
            print(f"⚠️ Erro ao atualizar configuração: {e}")
    
    def _save_config(self, config):
        """
        Salva a configuração no arquivo.
        """
        try:
            config_dir = Path.home() / '.spotdl'
            config_file = config_dir / 'config.json'
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar configuração: {e}")
    
    def _create_manual_config(self):
        """
        Cria manualmente o arquivo de configuração do spotDL.
        """
        try:
            # Diretório de configuração do spotDL
            config_dir = Path.home() / '.spotdl'
            config_dir.mkdir(exist_ok=True)
            
            # Criar diretório de cache
            cache_dir = config_dir / 'cache'
            cache_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / 'config.json'
            
            # Configuração padrão otimizada para BaixaFy
            default_config = {
                "client_id": os.getenv('SPOTIFY_CLIENT_ID', ''),
                "client_secret": os.getenv('SPOTIFY_CLIENT_SECRET', ''),
                "user_auth": False,
                "cache_path": str(cache_dir),
                "audio_provider": "youtube-music",
                "lyrics_provider": "musixmatch",
                "playlist_numbering": False,
                "scan_for_songs": False,
                "m3u": False,
                "output": str(self.download_path),
                "overwrite": "metadata",
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
            else:
                return {'error': f'Erro ao obter metadados: {error_msg}'}
    
    def can_user_download(self, user: CustomUser) -> Tuple[bool, str]:
        """
        Verifica se o usuário pode fazer download.
        
        Args:
            user (CustomUser): Usuário a ser verificado
            
        Returns:
            Tuple[bool, str]: (pode_baixar, mensagem)
        """
        # Verificar se é usuário premium válido
        if user.is_premium_active():
            return True, "Usuário premium ativo"
        
        # Verificar quantos downloads gratuitos já fez
        free_downloads = DownloadHistory.objects.filter(
            user=user,
            is_premium_download=False
        ).count()
        
        # Limite de downloads gratuitos
        FREE_DOWNLOAD_LIMIT = 1
        
        if free_downloads >= FREE_DOWNLOAD_LIMIT:
            return False, f"Limite de {FREE_DOWNLOAD_LIMIT} download gratuito atingido. Assine para downloads ilimitados!"
        
        return True, f"Download gratuito disponível ({FREE_DOWNLOAD_LIMIT - free_downloads} restante)"
    
    def baixar_musica(self, url: str, user: CustomUser) -> Dict:
        """
        Realiza o download de uma música do Spotify.
        
        Args:
            url (str): URL da música no Spotify
            user (CustomUser): Usuário que está fazendo o download
            
        Returns:
            Dict: Resultado do download com caminho do arquivo ou erro
        """
        try:
            # Verificar permissões do usuário
            can_download, message = self.can_user_download(user)
            if not can_download:
                return {'error': message}
            
            # Verificar se spotDL está configurado
            if not hasattr(self, 'spotdl'):
                return {'error': 'Serviço de download não está configurado'}
            
            # Extrair informações da URL
            url_info = self.extract_spotify_info(url)
            if 'error' in url_info:
                return url_info
            
            # Obter metadados primeiro
            metadata = self.get_track_metadata(url)
            if 'error' in metadata:
                return metadata
            
            print(f"🎵 Iniciando download: {metadata.get('artists', 'N/A')} - {metadata.get('name', 'N/A')}")
            
            # Realizar download
            songs = self.spotdl.search([url])
            if not songs:
                return {'error': 'Música não encontrada'}
            
            # Download da música
            download_result = self.spotdl.download(songs)
            
            # Procurar arquivo baixado
            downloaded_files = []
            for item in self.download_path.iterdir():
                if item.is_file() and item.suffix.lower() == '.mp3':
                    # Verificar se foi criado recentemente (últimos 2 minutos)
                    if (item.stat().st_mtime > (os.path.getmtime(__file__) - 120)):
                        downloaded_files.append(item)
            
            if not downloaded_files:
                return {'error': 'Arquivo de áudio não foi encontrado após o download'}
            
            # Pegar o arquivo mais recente
            downloaded_file = max(downloaded_files, key=lambda x: x.stat().st_mtime)
            
            # Registrar download no histórico
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
                'download_url': self.get_file_url(str(downloaded_file)),
                'metadata': metadata,
                'is_premium_download': is_premium
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erro no download: {error_msg}")
            
            # Mensagens de erro mais amigáveis
            if 'ffmpeg' in error_msg.lower():
                return {'error': 'FFmpeg não está instalado ou configurado corretamente'}
            elif 'youtube' in error_msg.lower():
                return {'error': 'Erro ao acessar YouTube. Tente novamente em alguns minutos.'}
            elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                return {'error': 'Erro de conexão. Verifique sua internet e tente novamente.'}
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


# Instância global do serviço - Inicialização mais segura
spotify_service = None

def get_spotify_service():
    """
    Retorna a instância do serviço, inicializando se necessário.
    """
    global spotify_service
    if spotify_service is None:
        try:
            spotify_service = SpotifyDownloadService()
            print("✅ SpotifyDownloadService inicializado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao inicializar SpotifyDownloadService: {e}")
            return None
    return spotify_service

# Tentar inicializar na importação
try:
    spotify_service = SpotifyDownloadService()
    print("✅ SpotifyDownloadService inicializado com sucesso")
except Exception as e:
    print(f"❌ Erro ao inicializar SpotifyDownloadService: {e}")
    spotify_service = None