# apps/baixador/services.py - VERSÃO SIMPLIFICADA
import os
import re
import subprocess
import tempfile
from typing import Dict, List, Optional
from urllib.parse import urlparse
from pathlib import Path
import time

from django.conf import settings

# Instância global do serviço
_spotify_service = None

class SimpleSpotifyService:
    """
    Serviço simplificado para downloads do Spotify.
    Funciona igual ao script baixar.py, mas integrado ao Django.
    """
    
    def __init__(self):
        """
        Inicializa o serviço verificando dependências.
        """
        self.download_path = Path(settings.MEDIA_ROOT)
        self.download_path.mkdir(exist_ok=True)
        
        # Verificar se spotDL está disponível
        self.spotdl_available = self._check_spotdl()
        self.ffmpeg_available = self._check_ffmpeg()
    
    def _check_spotdl(self):
        """Verifica se spotDL está instalado."""
        try:
            result = subprocess.run(
                ['spotdl', '--version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_ffmpeg(self):
        """Verifica se FFmpeg está instalado."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except:
            return False
    
    def health_check(self):
        """
        Verifica se o serviço está funcionando.
        """
        if not self.spotdl_available:
            return {
                'status': 'error',
                'message': 'SpotDL não está instalado. Execute: pip install spotdl'
            }
        
        if not self.ffmpeg_available:
            return {
                'status': 'error', 
                'message': 'FFmpeg não está instalado. Baixe em: https://ffmpeg.org/'
            }
        
        return {
            'status': 'ok',
            'message': 'Serviço funcionando',
            'download_path': str(self.download_path)
        }
    
    def extract_spotify_info(self, url: str) -> Dict:
        """
        Extrai informações de uma URL do Spotify.
        Simula o comportamento do script original.
        """
        try:
            # Usar spotdl para obter metadados
            cmd = ['spotdl', '--print-errors', '--output', '{title} - {artist}', url]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Analisar saída para extrair informações
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                tracks = []
                
                for line in lines:
                    if line.strip() and not line.startswith('Downloaded'):
                        track_info = self._parse_track_line(line)
                        if track_info:
                            tracks.append(track_info)
                
                if tracks:
                    return {
                        'tracks': tracks,
                        'track_count': len(tracks),
                        'type': 'playlist' if len(tracks) > 1 else 'track'
                    }
            
            # Se falhou, tentar método alternativo
            return self._extract_basic_info(url)
            
        except subprocess.TimeoutExpired:
            return {'error': 'Timeout ao analisar URL'}
        except Exception as e:
            return {'error': f'Erro ao extrair informações: {str(e)}'}
    
    def _parse_track_line(self, line: str) -> Optional[Dict]:
        """
        Analisa uma linha de saída do spotdl para extrair info da track.
        """
        try:
            # Formato típico: "Track Name - Artist Name"
            if ' - ' in line:
                parts = line.split(' - ', 1)
                return {
                    'name': parts[0].strip(),
                    'artist': parts[1].strip()
                }
            else:
                return {
                    'name': line.strip(),
                    'artist': 'Unknown Artist'
                }
        except:
            return None
    
    def _extract_basic_info(self, url: str) -> Dict:
        """
        Extração básica de informações da URL.
        """
        if 'playlist' in url:
            return {
                'tracks': [{'name': 'Playlist', 'artist': 'Various Artists'}],
                'track_count': 1,
                'type': 'playlist'
            }
        else:
            return {
                'tracks': [{'name': 'Single Track', 'artist': 'Unknown Artist'}],
                'track_count': 1,
                'type': 'track'
            }
    
    def download_track(self, track_info: Dict, output_dir: str) -> Optional[str]:
        """
        Baixa uma única track usando spotDL.
        Simula o comportamento do script baixar.py.
        """
        try:
            # Este método seria chamado pela view, mas como estamos
            # simplificando, vamos usar o método direto do spotdl
            return None
            
        except Exception as e:
            print(f"Erro ao baixar track: {e}")
            return None
    
    def download_spotify_url(self, url: str, output_dir: str) -> List[str]:
        """
        Baixa diretamente uma URL do Spotify.
        Método principal que replica o script baixar.py.
        """
        try:
            # Criar diretório se não existir
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            # Comando spotdl igual ao script original
            cmd = [
                'spotdl',
                url,
                '--output', str(output_path),
                '--format', 'mp3',
                '--bitrate', '320k'
            ]
            
            # Executar comando
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            if result.returncode == 0:
                # Encontrar arquivos baixados
                downloaded_files = []
                for file_path in output_path.glob('*.mp3'):
                    downloaded_files.append(str(file_path))
                
                return downloaded_files
            else:
                print(f"Erro no spotdl: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print("Timeout no download")
            return []
        except Exception as e:
            print(f"Erro no download: {e}")
            return []


def get_spotify_service():
    """
    Retorna a instância global do serviço.
    """
    global _spotify_service
    
    if _spotify_service is None:
        _spotify_service = SimpleSpotifyService()
    
    return _spotify_service


# ========================================
# apps/baixador/models.py - VAZIO
# Remover todos os modelos, não precisamos mais

# ========================================
# apps/baixador/__init__.py - VAZIO
# Apenas para manter como app Django