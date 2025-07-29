# ffmpeg_helper.py - Adicione ao seu app Django
import os
import shutil
import subprocess
from pathlib import Path
from django.conf import settings

class FFmpegHelper:
    """Helper para o Django encontrar e usar FFmpeg."""
    
    def __init__(self):
        self.ffmpeg_path = self._encontrar_ffmpeg()
    
    def _encontrar_ffmpeg(self):
        """Encontra FFmpeg de todas as formas possíveis."""
        
        # 1. Verificar se está configurado no settings.py
        if hasattr(settings, 'FFMPEG_PATH'):
            if os.path.exists(settings.FFMPEG_PATH):
                return settings.FFMPEG_PATH
        
        # 2. Verificar PATH do sistema
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
        
        # 3. Verificar locais comuns no Windows
        caminhos_comuns = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
            Path.home() / 'ffmpeg' / 'bin' / 'ffmpeg.exe',
        ]
        
        for caminho in caminhos_comuns:
            if Path(caminho).exists():
                return str(caminho)
        
        return None
    
    def esta_disponivel(self):
        """Verifica se FFmpeg está disponível."""
        if not self.ffmpeg_path:
            return False
        
        try:
            subprocess.run(
                [self.ffmpeg_path, '-version'], 
                capture_output=True, 
                check=True, 
                timeout=5
            )
            return True
        except:
            return False
    
    def obter_comando_base(self):
        """Retorna o comando base para usar com subprocess."""
        return self.ffmpeg_path if self.ffmpeg_path else 'ffmpeg'

# Instância global
ffmpeg_helper = FFmpegHelper()

def verificar_ffmpeg_para_django():
    """
    Função para usar nas suas views para verificar FFmpeg.
    
    Returns:
        dict: Status do FFmpeg para o Django
    """
    helper = FFmpegHelper()
    
    return {
        'disponivel': helper.esta_disponivel(),
        'caminho': helper.ffmpeg_path,
        'comando': helper.obter_comando_base()
    }
