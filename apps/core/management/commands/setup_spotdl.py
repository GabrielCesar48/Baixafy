# apps/core/management/__init__.py
# (arquivo vazio)

# apps/core/management/commands/__init__.py  
# (arquivo vazio)

# apps/core/management/commands/setup_spotdl.py
import os
import json
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    """
    Comando para configurar o spotDL automaticamente.
    
    Usage:
        python manage.py setup_spotdl
        python manage.py setup_spotdl --force
    """
    
    help = 'Configura o spotDL criando arquivo de configuração e testando funcionamento'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força recriação do arquivo de configuração mesmo se já existir',
        )
        
        parser.add_argument(
            '--client-id',
            type=str,
            help='Client ID do Spotify (opcional)',
        )
        
        parser.add_argument(
            '--client-secret',
            type=str,
            help='Client Secret do Spotify (opcional)',
        )
    
    def handle(self, *args, **options):
        """
        Executa o comando de configuração.
        """
        self.stdout.write(
            self.style.HTTP_INFO('🎵 Configurando spotDL para BaixaFy...')
        )
        
        try:
            # Verificar se spotDL está instalado
            self.check_spotdl_installation()
            
            # Configurar arquivo de config
            config_created = self.setup_config_file(
                force=options['force'],
                client_id=options.get('client_id'),
                client_secret=options.get('client_secret')
            )
            
            # Criar diretório de downloads
            self.setup_download_directory()
            
            # Testar funcionamento
            self.test_spotdl_functionality()
            
            if config_created:
                self.stdout.write(
                    self.style.SUCCESS('✅ spotDL configurado com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ spotDL já estava configurado!')
                )
                
            self.show_next_steps()
            
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f'Erro inesperado: {str(e)}')
    
    def check_spotdl_installation(self):
        """
        Verifica se spotDL está instalado.
        """
        try:
            result = subprocess.run(
                ['spotdl', '--version'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.stdout.write(f'📦 spotDL encontrado: {version}')
            else:
                raise CommandError(
                    '❌ spotDL não está instalado corretamente. '
                    'Execute: pip install spotdl'
                )
                
        except FileNotFoundError:
            raise CommandError(
                '❌ spotDL não encontrado. Instale com: pip install spotdl'
            )
        except subprocess.TimeoutExpired:
            raise CommandError('❌ Timeout ao verificar spotDL')
    
    def setup_config_file(self, force=False, client_id=None, client_secret=None):
        """
        Configura o arquivo de configuração do spotDL.
        
        Returns:
            bool: True se arquivo foi criado, False se já existia
        """
        config_dir = Path.home() / '.spotdl'
        config_file = config_dir / 'config.json'
        
        # Verificar se já existe
        if config_file.exists() and not force:
            self.stdout.write(f'📁 Arquivo de configuração já existe: {config_file}')
            return False
        
        # Criar diretório se não existir
        config_dir.mkdir(exist_ok=True)
        cache_dir = config_dir / 'cache'
        cache_dir.mkdir(exist_ok=True)
        
        # Obter credenciais do Spotify
        if not client_id:
            client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
        if not client_secret:
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')
        
        # Configuração padrão otimizada para BaixaFy
        config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "user_auth": False,
            "cache_path": str(cache_dir),
            "audio_provider": "youtube-music",
            "lyrics_provider": "musixmatch",
            "playlist_numbering": False,
            "scan_for_songs": False,
            "m3u": False,
            "output": str(Path(settings.MEDIA_ROOT)),
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
            json.dump(config, f, indent=2)
        
        self.stdout.write(f'✅ Configuração criada: {config_file}')
        
        # Mostrar informações sobre credenciais
        if client_id and client_secret:
            self.stdout.write('🔑 Credenciais do Spotify configuradas')
        else:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️ Funcionando sem credenciais do Spotify (modo público)\n'
                    '   Para melhor performance, configure SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET'
                )
            )
        
        return True
    
    def setup_download_directory(self):
        """
        Cria e configura o diretório de downloads.
        """
        download_dir = Path(settings.MEDIA_ROOT)
        download_dir.mkdir(exist_ok=True)
        
        # Verificar permissões
        if not os.access(download_dir, os.W_OK):
            raise CommandError(f'❌ Sem permissão de escrita em: {download_dir}')
        
        self.stdout.write(f'📁 Diretório de downloads: {download_dir}')
    
    def test_spotdl_functionality(self):
        """
        Testa se o spotDL está funcionando corretamente.
        """
        self.stdout.write('🧪 Testando spotDL...')
        
        try:
            # Testar comando básico
            result = subprocess.run(
                ['spotdl', '--help'], 
                capture_output=True, 
                text=True,
                timeout=15
            )
            
            if result.returncode != 0:
                raise CommandError('❌ spotDL não está respondendo corretamente')
            
            self.stdout.write('✅ spotDL está funcionando')
            
        except subprocess.TimeoutExpired:
            raise CommandError('❌ Timeout ao testar spotDL')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Aviso no teste: {str(e)}')
            )
    
    def show_next_steps(self):
        """
        Mostra os próximos passos para o usuário.
        """
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.HTTP_INFO('📋 PRÓXIMOS PASSOS:'))
        
        self.stdout.write('\n1. 🔑 Para melhor performance, configure credenciais do Spotify:')
        self.stdout.write('   - Crie um app em: https://developer.spotify.com/')
        self.stdout.write('   - Adicione ao .env:')
        self.stdout.write('     SPOTIFY_CLIENT_ID=seu_client_id')
        self.stdout.write('     SPOTIFY_CLIENT_SECRET=seu_client_secret')
        
        self.stdout.write('\n2. 🎵 Instale o FFmpeg se ainda não tiver:')
        self.stdout.write('   - Windows: https://ffmpeg.org/download.html')
        self.stdout.write('   - Ubuntu/Debian: sudo apt install ffmpeg')
        self.stdout.write('   - macOS: brew install ffmpeg')
        
        self.stdout.write('\n3. 🚀 Reinicie o servidor Django:')
        self.stdout.write('   python manage.py runserver')
        
        self.stdout.write('\n4. ✅ Teste um download no painel!')
        self.stdout.write('='*50)