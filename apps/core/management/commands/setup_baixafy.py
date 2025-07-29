# apps/core/management/commands/setup_baixafy.py
import os
import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from apps.baixador.services import get_spotify_service


class Command(BaseCommand):
    """
    Comando para configurar completamente o BaixaFy após instalação do FFmpeg.
    
    Usage:
        python manage.py setup_baixafy
    """
    
    help = 'Configura completamente o BaixaFy após instalação do FFmpeg'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reconfiguration even if already setup',
        )
        
        parser.add_argument(
            '--no-config',
            action='store_true',
            help='Skip SpotDL config generation',
        )
    
    def handle(self, *args, **options):
        """
        Executa o setup completo do BaixaFy.
        """
        self.stdout.write(
            self.style.HTTP_INFO('🎵 SETUP COMPLETO DO BAIXAFY')
        )
        self.stdout.write('=' * 50)
        
        try:
            # 1. Verificar Python
            self.check_python()
            
            # 2. Verificar SpotDL
            self.check_spotdl()
            
            # 3. Verificar FFmpeg
            self.check_ffmpeg()
            
            # 4. Gerar configuração do SpotDL
            if not options['no_config']:
                self.setup_spotdl_config(force=options['force'])
            
            # 5. Verificar diretórios
            self.setup_directories()
            
            # 6. Testar serviço
            self.test_service()
            
            # 7. Mostrar próximos passos
            self.show_success_message()
            
        except CommandError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Setup falhou: {str(e)}')
            )
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro inesperado: {str(e)}')
            )
            sys.exit(1)
    
    def check_python(self):
        """Verifica versão do Python."""
        self.stdout.write('\n🔍 Verificando Python...')
        
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Python {version.major}.{version.minor}.{version.micro} OK')
            )
        else:
            raise CommandError('Python 3.8+ é necessário')
    
    def check_spotdl(self):
        """Verifica se SpotDL está instalado."""
        self.stdout.write('🔍 Verificando SpotDL...')
        
        try:
            result = subprocess.run(
                [sys.executable, '-c', 'import spotdl; print(spotdl.__version__)'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ SpotDL {version} instalado')
                )
            else:
                raise CommandError('SpotDL não está instalado. Execute: pip install spotdl')
                
        except subprocess.TimeoutExpired:
            raise CommandError('Timeout ao verificar SpotDL')
        except Exception as e:
            raise CommandError(f'Erro ao verificar SpotDL: {str(e)}')
    
    def check_ffmpeg(self):
        """Verifica se FFmpeg está instalado."""
        self.stdout.write('🔍 Verificando FFmpeg...')
        
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Extrair versão
                lines = result.stdout.split('\n')
                version_line = lines[0] if lines else "Versão desconhecida"
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {version_line}')
                )
            else:
                raise CommandError('FFmpeg não está funcionando')
                
        except FileNotFoundError:
            raise CommandError(
                'FFmpeg não está instalado. Execute install_ffmpeg.bat como Administrador'
            )
        except subprocess.TimeoutExpired:
            raise CommandError('Timeout ao verificar FFmpeg')
        except Exception as e:
            raise CommandError(f'Erro ao verificar FFmpeg: {str(e)}')
    
    def setup_spotdl_config(self, force=False):
        """Gera configuração do SpotDL."""
        self.stdout.write('🔧 Configurando SpotDL...')
        
        config_dir = Path.home() / '.spotdl'
        config_file = config_dir / 'config.json'
        
        if config_file.exists() and not force:
            self.stdout.write(
                self.style.WARNING('⚠️ Configuração já existe (use --force para recriar)')
            )
            return
        
        try:
            # Executar comando para gerar config
            result = subprocess.run(
                ['spotdl', '--generate-config'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS('✅ Configuração do SpotDL criada')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Aviso: {result.stderr}')
                )
                # Continuar mesmo com aviso
                
        except subprocess.TimeoutExpired:
            raise CommandError('Timeout ao gerar configuração do SpotDL')
        except FileNotFoundError:
            raise CommandError('Comando spotdl não encontrado no PATH')
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Erro ao gerar config: {str(e)}')
            )
            # Continuar mesmo com erro
    
    def setup_directories(self):
        """Configura diretórios necessários."""
        self.stdout.write('📁 Configurando diretórios...')
        
        # Diretório de downloads
        download_dir = Path(settings.MEDIA_ROOT)
        download_dir.mkdir(exist_ok=True)
        
        # Verificar permissões
        if not os.access(download_dir, os.W_OK):
            raise CommandError(f'Sem permissão de escrita em: {download_dir}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Diretório de downloads: {download_dir}')
        )
    
    def test_service(self):
        """Testa se o serviço está funcionando."""
        self.stdout.write('🧪 Testando serviço...')
        
        try:
            # Tentar obter o serviço
            service = get_spotify_service()
            
            if service is None:
                raise CommandError('Serviço não foi inicializado')
            
            # Verificar health check
            health = service.health_check()
            
            if health['status'] == 'ok':
                self.stdout.write(
                    self.style.SUCCESS('✅ Serviço funcionando corretamente!')
                )
            elif health['status'] == 'warning':
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Serviço com avisos: {health["message"]}')
                )
            else:
                raise CommandError(f'Erro no serviço: {health["message"]}')
                
        except Exception as e:
            raise CommandError(f'Erro ao testar serviço: {str(e)}')
    
    def show_success_message(self):
        """Mostra mensagem de sucesso e próximos passos."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('🎉 SETUP CONCLUÍDO COM SUCESSO!')
        )
        self.stdout.write('='*50)
        
        self.stdout.write('\n📋 PRÓXIMOS PASSOS:')
        
        self.stdout.write('\n1. 🚀 Iniciar servidor:')
        self.stdout.write('   python manage.py runserver')
        
        self.stdout.write('\n2. 🌐 Acessar aplicação:')
        self.stdout.write('   http://127.0.0.1:8000')
        
        self.stdout.write('\n3. 🎵 Testar download:')
        self.stdout.write('   - Faça login/cadastro')
        self.stdout.write('   - Cole um link do Spotify')
        self.stdout.write('   - Baixe sua música!')
        
        # Credenciais opcionais
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        if not client_id:
            self.stdout.write('\n💡 OPCIONAL - Melhor performance:')
            self.stdout.write('   Configure credenciais do Spotify em .env:')
            self.stdout.write('   SPOTIFY_CLIENT_ID=seu_client_id')
            self.stdout.write('   SPOTIFY_CLIENT_SECRET=seu_client_secret')
            self.stdout.write('   Obtenha em: https://developer.spotify.com/')
        else:
            self.stdout.write('\n✅ Credenciais do Spotify configuradas')
        
        self.stdout.write('\n🎵 BaixaFy está pronto para usar!')
        self.stdout.write('='*50)