# fix_spotdl_now.py - Execute na raiz do projeto para corrigir SpotDL agora
import os
import sys
from pathlib import Path

def corrigir_services_py():
    """Corrige o arquivo services.py com a sintaxe correta do SpotDL."""
    
    print("🔧 Corrigindo services.py...")
    
    # Encontrar arquivo services.py
    services_file = Path("apps/baixador/services.py")
    
    if not services_file.exists():
        print("❌ Arquivo services.py não encontrado!")
        print("   Verifique se está executando na raiz do projeto")
        return False
    
    # Ler arquivo atual
    try:
        with open(services_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler services.py: {e}")
        return False
    
    # Fazer backup
    backup_file = services_file.parent / "services.py.backup"
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Backup criado: {backup_file}")
    except Exception as e:
        print(f"⚠️ Não foi possível criar backup: {e}")
    
    # Correções necessárias
    corrections = [
        # Correção 1: Remover config do construtor
        (
            'self.spotdl = Spotdl(\n                    client_id=settings.SPOTIFY_CLIENT_ID if hasattr(settings, \'SPOTIFY_CLIENT_ID\') else None,\n                    client_secret=settings.SPOTIFY_CLIENT_SECRET if hasattr(settings, \'SPOTIFY_CLIENT_SECRET\') else None,\n                    config=config\n                )',
            '''self.spotdl = Spotdl(
                    client_id=getattr(settings, 'SPOTIFY_CLIENT_ID', '') or os.getenv('SPOTIFY_CLIENT_ID', ''),
                    client_secret=getattr(settings, 'SPOTIFY_CLIENT_SECRET', '') or os.getenv('SPOTIFY_CLIENT_SECRET', '')
                )'''
        ),
        
        # Correção 2: Remover importação de get_config
        (
            'from spotdl.utils.config import get_config',
            '# from spotdl.utils.config import get_config  # Não usado'
        ),
        
        # Correção 3: Remover configuração manual
        (
            '''# Configurar SpotDL com FFmpeg correto
                config = get_config()
                config['ffmpeg'] = self.ffmpeg_manager.obter_comando()''',
            '''# SpotDL será inicializado com configuração padrão'''
        )
    ]
    
    # Aplicar correções
    modified = False
    for old_text, new_text in corrections:
        if old_text in content:
            content = content.replace(old_text, new_text)
            modified = True
            print("✅ Correção aplicada")
    
    # Se não achou as strings exatas, criar um novo arquivo
    if not modified:
        print("⚠️ Padrões específicos não encontrados, criando novo services.py...")
        content = criar_services_correto()
        modified = True
    
    # Salvar arquivo corrigido
    if modified:
        try:
            with open(services_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ services.py corrigido!")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return False
    else:
        print("ℹ️ Nenhuma correção necessária")
        return True

def criar_services_correto():
    """Cria um services.py completamente correto."""
    return '''# apps/baixador/services.py - VERSÃO CORRIGIDA
import os
import shutil
import subprocess
from pathlib import Path
from django.conf import settings

class FFmpegManager:
    """Gerenciador inteligente do FFmpeg para Django."""
    
    def __init__(self):
        self.ffmpeg_path = self._encontrar_ffmpeg()
        self.disponivel = self._verificar_disponibilidade()
    
    def _encontrar_ffmpeg(self):
        """Encontra FFmpeg em todos os locais possíveis."""
        
        # 1. Verificar settings.py
        if hasattr(settings, 'FFMPEG_PATH'):
            if os.path.exists(settings.FFMPEG_PATH):
                return settings.FFMPEG_PATH
        
        # 2. Verificar PATH do sistema
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
        
        # 3. Locais comuns no Windows
        caminhos_windows = [
            r'C:\\ffmpeg\\bin\\ffmpeg.exe',
            r'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe', 
            r'C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe',
            Path.home() / 'ffmpeg' / 'bin' / 'ffmpeg.exe',
        ]
        
        for caminho in caminhos_windows:
            if Path(caminho).exists():
                return str(caminho)
        
        return None
    
    def _verificar_disponibilidade(self):
        """Verifica se FFmpeg funciona realmente."""
        if not self.ffmpeg_path:
            return False
        
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                timeout=5,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def obter_comando(self):
        """Retorna comando para usar em subprocess."""
        return self.ffmpeg_path if self.ffmpeg_path else 'ffmpeg'
    
    def diagnostico(self):
        """Retorna diagnóstico completo."""
        return {
            'ffmpeg_path': self.ffmpeg_path,
            'disponivel': self.disponivel,
            'no_path': shutil.which('ffmpeg') is not None,
            'erro': None if self.disponivel else 'FFmpeg não encontrado ou não funciona'
        }


class SpotifyDownloadService:
    """Serviço de download do Spotify com verificação adequada de FFmpeg."""
    
    def __init__(self):
        self.ffmpeg_manager = FFmpegManager()
        self.download_path = Path(settings.MEDIA_ROOT) / 'downloads'
        self.download_path.mkdir(exist_ok=True)
        
        # Inicializar SpotDL apenas se FFmpeg estiver disponível
        self.spotdl = None
        if self.ffmpeg_manager.disponivel:
            try:
                from spotdl import Spotdl
                
                # CORREÇÃO: SpotDL não aceita 'config' no construtor
                # Usar apenas client_id e client_secret
                client_id = getattr(settings, 'SPOTIFY_CLIENT_ID', '') or os.getenv('SPOTIFY_CLIENT_ID', '')
                client_secret = getattr(settings, 'SPOTIFY_CLIENT_SECRET', '') or os.getenv('SPOTIFY_CLIENT_SECRET', '')
                
                # Se não tiver credenciais, usar valores vazios (modo público)
                if not client_id or not client_secret:
                    print("⚠️ Credenciais do Spotify não configuradas. Usando modo público.")
                    client_id = ""
                    client_secret = ""
                
                # Inicializar SpotDL com sintaxe correta
                self.spotdl = Spotdl(
                    client_id=client_id,
                    client_secret=client_secret
                )
                
                print("✅ SpotDL inicializado com sucesso")
                
            except Exception as e:
                print(f"❌ Erro ao inicializar SpotDL: {e}")
                self.spotdl = None
    
    def health_check(self):
        """
        Verifica saúde do serviço com diagnóstico detalhado.
        
        Returns:
            dict: Status completo do serviço
        """
        ffmpeg_status = self.ffmpeg_manager.diagnostico()
        
        if not ffmpeg_status['disponivel']:
            return {
                'status': 'error',
                'message': 'Serviço Indisponível - FFmpeg não encontrado ou não funciona',
                'details': {
                    'ffmpeg_path': ffmpeg_status['ffmpeg_path'],
                    'ffmpeg_no_path': ffmpeg_status['no_path'],
                    'spotdl_inicializado': self.spotdl is not None,
                    'solucao': 'Execute o script fix_ffmpeg_django.py'
                }
            }
        
        if not self.spotdl:
            return {
                'status': 'error', 
                'message': 'SpotDL não inicializado',
                'details': {
                    'ffmpeg_ok': True,
                    'spotdl_erro': 'Falha na inicialização do SpotDL'
                }
            }
        
        return {
            'status': 'ok',
            'message': 'Serviço funcionando',
            'details': {
                'ffmpeg_path': ffmpeg_status['ffmpeg_path'],
                'download_path': str(self.download_path),
                'spotdl_ok': True
            }
        }
    
    def baixar_musica(self, spotify_url, user):
        """
        Baixa música do Spotify usando SpotDL.
        
        Args:
            spotify_url (str): URL da música/playlist do Spotify
            user: Usuário que está fazendo o download
            
        Returns:
            dict: Resultado do download
        """
        # Verificar se serviço está funcionando
        health = self.health_check()
        if health['status'] == 'error':
            return {
                'success': False,
                'error': health['message'],
                'details': health.get('details')
            }
        
        # Verificar permissões do usuário
        if not user.can_download():
            return {
                'success': False,
                'error': 'Usuário não tem permissão para download'
            }
        
        try:
            # CORREÇÃO: Usar sintaxe correta do SpotDL
            # 1. Buscar informações da música
            songs = self.spotdl.search([spotify_url])
            
            if not songs:
                return {
                    'success': False,
                    'error': 'Música não encontrada'
                }
            
            # 2. Baixar primeira música
            song = songs[0]
            
            # 3. Fazer download usando método correto
            downloaded_files = self.spotdl.downloader.download_multiple_songs(songs)
            
            if downloaded_files and len(downloaded_files) > 0:
                # Atualizar contador do usuário
                user.increment_downloads()
                
                # Pegar primeiro arquivo baixado
                file_path = downloaded_files[0]
                
                return {
                    'success': True,
                    'file_path': str(file_path),
                    'song_info': {
                        'title': song.display_name,
                        'artist': ', '.join(song.artists) if hasattr(song, 'artists') else song.artist,
                        'duration': getattr(song, 'duration', 0)
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Falha no download - arquivo não foi criado'
                }
                
        except Exception as e:
            print(f"❌ Erro no download: {str(e)}")
            return {
                'success': False,
                'error': f'Erro no download: {str(e)}'
            }


# Instância global
spotify_service = None

def get_spotify_service():
    """
    Retorna a instância do serviço com lazy loading.
    
    Returns:
        SpotifyDownloadService: Instância do serviço
    """
    global spotify_service
    if spotify_service is None:
        try:
            spotify_service = SpotifyDownloadService()
            print("✅ SpotifyDownloadService inicializado")
        except Exception as e:
            print(f"❌ Erro ao inicializar serviço: {e}")
            return None
    return spotify_service

# Tentar inicializar na importação
try:
    spotify_service = SpotifyDownloadService()
    print("✅ SpotifyDownloadService inicializado automaticamente")
except Exception as e:
    print(f"⚠️ Serviço será inicializado sob demanda: {e}")
    spotify_service = None
'''

def main():
    """Função principal de correção."""
    print("🚀 CORREÇÃO RÁPIDA DO SPOTDL")
    print("=" * 40)
    
    # Verificar se estamos no diretório correto
    if not Path("manage.py").exists():
        print("❌ Execute este script na raiz do projeto (onde está manage.py)")
        return
    
    # Fazer correção
    if corrigir_services_py():
        print("\n🎉 CORREÇÃO CONCLUÍDA!")
        print("\n🎯 Próximos passos:")
        print("1. Execute: python manage.py runserver")
        print("2. O erro 'config' não deve mais aparecer")
        print("3. Teste o download na interface")
        print("\n💡 Para testar: python manage.py test_spotdl")
    else:
        print("\n❌ Correção falhou. Verifique os erros acima.")

if __name__ == '__main__':
    main()