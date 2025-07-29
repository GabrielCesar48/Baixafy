# apps/core/management/commands/test_spotdl.py
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.baixador.services import get_spotify_service
import os


class Command(BaseCommand):
    """
    Comando para testar se o SpotDL está funcionando após as correções.
    
    Usage:
        python manage.py test_spotdl
    """
    
    help = 'Testa se o SpotDL está funcionando corretamente após as correções'
    
    def handle(self, *args, **options):
        """
        Executa o teste do SpotDL.
        """
        self.stdout.write(
            self.style.HTTP_INFO('🧪 Testando SpotDL após correções...')
        )
        
        try:
            # Tentar obter o serviço
            service = get_spotify_service()
            
            if service is None:
                self.stdout.write(
                    self.style.ERROR('❌ Erro: Serviço não foi inicializado')
                )
                return
            
            # Verificar health check
            health = service.health_check()
            
            if health['status'] == 'ok':
                self.stdout.write(
                    self.style.SUCCESS('✅ SpotDL está funcionando corretamente!')
                )
                self.stdout.write(f"📁 Diretório de downloads: {health['download_path']}")
                
                # Verificar credenciais
                client_id = os.getenv('SPOTIFY_CLIENT_ID')
                if client_id:
                    self.stdout.write('🔑 Credenciais do Spotify configuradas')
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️ Funcionando sem credenciais do Spotify')
                    )
                
                self.show_usage_example()
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro no health check: {health["message"]}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro no teste: {str(e)}')
            )
    
    def show_usage_example(self):
        """
        Mostra exemplo de uso.
        """
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.HTTP_INFO('📋 EXEMPLO DE USO:'))
        self.stdout.write('\nPara testar um download real, use uma URL do Spotify como:')
        self.stdout.write('https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh')
        self.stdout.write('\n✅ Servidor pronto para downloads!')
        self.stdout.write('='*50)