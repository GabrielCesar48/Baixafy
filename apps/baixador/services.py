# baixador/services.py
import os
import re
import requests
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
        
        # Configurar spotDL
        config = get_config()
        config["output"] = str(self.download_path)
        config["format"] = "mp3"
        config["bitrate"] = "192k"
        
        try:
            self.spotdl = Spotdl(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                config=config
            )
        except Exception as e:
            # Fallback sem credenciais (modo público)
            self.spotdl = Spotdl(config=config)
    
    def extract_spotify_info(self, url: str) -> Dict:
        """
        Extrai informações básicas de uma URL do Spotify.
        
        Args:
            url (str): URL do Spotify
            
        Returns:
            Dict: Informações extraídas da URL
        """
        try:
            # Determinar tipo de conteúdo
            if 'track/' in url:
                content_type = 'track'
                track_id = re.search(r'track/([a-zA-Z0-9]+)', url).group(1)
            elif 'playlist/' in url:
                content_type = 'playlist'
                track_id = re.search(r'playlist/([a-zA-Z0-9]+)', url).group(1)
            elif 'album/' in url:
                content_type = 'album'
                track_id = re.search(r'album/([a-zA-Z0-9]+)', url).group(1)
            else:
                return {'error': 'Tipo de conteúdo não suportado'}
            
            return {
                'type': content_type,
                'id': track_id,
                'url': url
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
            # Usar spotDL para obter metadados
            songs = self.spotdl.search([url])
            
            if not songs:
                return {'error': 'Música não encontrada'}
            
            song = songs[0]
            
            return {
                'title': song.name,
                'artist': ', '.join(song.artists),
                'album': song.album_name,
                'duration': f"{song.duration // 60}:{song.duration % 60:02d}",
                'cover_url': song.cover_url,
                'spotify_url': url,
                'year': getattr(song, 'year', 'N/A'),
                'genre': ', '.join(getattr(song, 'genres', [])) if hasattr(song, 'genres') else 'N/A'
            }
            
        except Exception as e:
            return {'error': f'Erro ao obter metadados: {str(e)}'}
    
    def get_playlist_metadata(self, url: str) -> Dict:
        """
        Obtém metadados de uma playlist do Spotify.
        
        Args:
            url (str): URL da playlist no Spotify
            
        Returns:
            Dict: Metadados da playlist e suas músicas
        """
        try:
            songs = self.spotdl.search([url])
            
            if not songs:
                return {'error': 'Playlist não encontrada'}
            
            playlist_info = {
                'type': 'playlist',
                'total_tracks': len(songs),
                'tracks': []
            }
            
            for song in songs:
                track_info = {
                    'title': song.name,
                    'artist': ', '.join(song.artists),
                    'album': song.album_name,
                    'duration': f"{song.duration // 60}:{song.duration % 60:02d}",
                    'cover_url': song.cover_url,
                    'spotify_url': song.url
                }
                playlist_info['tracks'].append(track_info)
            
            return playlist_info
            
        except Exception as e:
            return {'error': f'Erro ao obter playlist: {str(e)}'}
    
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
            
            # Baixar a música
            songs = self.spotdl.search([url])
            if not songs:
                return {'error': 'Música não encontrada'}
            
            song = songs[0]
            
            # Fazer download
            downloaded_files = self.spotdl.download(songs)
            
            if not downloaded_files:
                return {'error': 'Falha no download da música'}
            
            file_path = downloaded_files[0]
            
            # Registrar no histórico
            DownloadHistory.objects.create(
                user=user,
                spotify_url=url,
                song_title=metadata['title'],
                artist_name=metadata['artist'],
                album_name=metadata['album'],
                file_path=str(file_path),
                success=True
            )
            
            # Atualizar contador do usuário
            user.use_download()
            
            return {
                'success': True,
                'file_path': str(file_path),
                'filename': os.path.basename(file_path),
                'metadata': metadata
            }
            
        except Exception as e:
            # Registrar falha no histórico
            DownloadHistory.objects.create(
                user=user,
                spotify_url=url,
                song_title=url,
                artist_name='Desconhecido',
                success=False
            )
            
            return {'error': f'Erro durante o download: {str(e)}'}
    
    def download_playlist(self, url: str, user: CustomUser) -> Dict:
        """
        Baixa uma playlist completa do Spotify.
        Processa música por música sequencialmente.
        
        Args:
            url (str): URL da playlist no Spotify
            user (CustomUser): Usuário solicitando o download
            
        Returns:
            Dict: Resultado do download com informações detalhadas
        """
        try:
            # Verificar se usuário pode baixar
            if not user.can_download():
                return {
                    'error': 'Limite de downloads atingido. Assine o plano premium!',
                    'needs_subscription': True
                }
            
            # Obter informações da playlist
            playlist_info = self.get_playlist_metadata(url)
            if 'error' in playlist_info:
                return playlist_info
            
            results = {
                'type': 'playlist',
                'total_tracks': playlist_info['total_tracks'],
                'successful_downloads': [],
                'failed_downloads': [],
                'skipped_tracks': []
            }
            
            # Processar cada música da playlist
            for i, track in enumerate(playlist_info['tracks'], 1):
                try:
                    print(f"Baixando {i}/{playlist_info['total_tracks']}: {track['title']}")
                    
                    # Verificar se ainda pode baixar (para usuários gratuitos)
                    if not user.can_download() and not user.is_premium_active():
                        results['skipped_tracks'].extend(
                            playlist_info['tracks'][i-1:]
                        )
                        break
                    
                    # Baixar música individual
                    download_result = self.download_track(track['spotify_url'], user)
                    
                    if download_result.get('success'):
                        results['successful_downloads'].append({
                            'track': track,
                            'file_path': download_result['file_path'],
                            'filename': download_result['filename']
                        })
                    else:
                        results['failed_downloads'].append({
                            'track': track,
                            'error': download_result.get('error', 'Erro desconhecido')
                        })
                
                except Exception as e:
                    results['failed_downloads'].append({
                        'track': track,
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            return {'error': f'Erro ao processar playlist: {str(e)}'}
    
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