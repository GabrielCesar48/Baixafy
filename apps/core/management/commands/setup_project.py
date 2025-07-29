# apps/core/management/commands/setup_project.py
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import os

class Command(BaseCommand):
    help = 'Configura estrutura inicial do projeto BaixaFy'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('🚀 CONFIGURANDO PROJETO BAIXAFY')
        )
        
        # 1. Criar diretórios necessários
        self.stdout.write('\n📁 Criando diretórios...')
        
        diretorios = [
            settings.BASE_DIR / 'media',
            settings.BASE_DIR / 'media' / 'downloads',
            settings.BASE_DIR / 'media' / 'temp',
            settings.BASE_DIR / 'staticfiles',
        ]
        
        for diretorio in diretorios:
            try:
                diretorio.mkdir(parents=True, exist_ok=True)
                self.stdout.write(
                    self.style.SUCCESS(f'   ✅ {diretorio}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Erro ao criar {diretorio}: {e}')
                )
        
        # 2. Verificar permissões
        self.stdout.write('\n🔐 Verificando permissões...')
        
        for diretorio in diretorios:
            if diretorio.exists():
                if os.access(diretorio, os.W_OK):
                    self.stdout.write(
                        self.style.SUCCESS(f'   ✅ Escrita OK: {diretorio}')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'   ❌ Sem permissão: {diretorio}')
                    )
        
        # 3. Verificar FFmpeg
        self.stdout.write('\n🎵 Verificando FFmpeg...')
        
        if hasattr(settings, 'FFMPEG_PATH') and settings.FFMPEG_PATH:
            if Path(settings.FFMPEG_PATH).exists():
                self.stdout.write(
                    self.style.SUCCESS(f'   ✅ FFmpeg encontrado: {settings.FFMPEG_PATH}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ FFmpeg não existe: {settings.FFMPEG_PATH}')
                )
        else:
            self.stdout.write(
                self.style.WARNING('   ⚠️ FFMPEG_PATH não configurado')
            )
        
        # 4. Testar serviço
        self.stdout.write('\n🧪 Testando serviço...')
        
        try:
            from apps.baixador.services import get_spotify_service
            service = get_spotify_service()
            
            if service:
                health = service.health_check()
                if health['status'] == 'ok':
                    self.stdout.write(
                        self.style.SUCCESS('   ✅ Serviço funcionando!')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'   ⚠️ {health["message"]}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR('   ❌ Serviço não inicializado')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro: {str(e)}')
            )
        
        # 5. Resumo
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.SUCCESS('🎉 CONFIGURAÇÃO CONCLUÍDA!')
        )
        
        self.stdout.write('\n🎯 Próximos passos:')
        self.stdout.write('1. Execute: python manage.py migrate')
        self.stdout.write('2. Execute: python manage.py createsuperuser')
        self.stdout.write('3. Execute: python manage.py runserver')
        self.stdout.write('4. Acesse: http://127.0.0.1:8000')