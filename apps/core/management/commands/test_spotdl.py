# apps/core/management/commands/test_spotdl.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import sys

class Command(BaseCommand):
    help = 'Testa o SpotDL e diagnostica problemas'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('🧪 TESTANDO SPOTDL NO DJANGO')
        )
        self.stdout.write('=' * 50)
        
        # 1. Verificar instalação do SpotDL
        self.stdout.write('\n1️⃣ Verificando instalação do SpotDL...')
        
        try:
            import spotdl
            version = getattr(spotdl, '__version__', 'desconhecida')
            self.stdout.write(
                self.style.SUCCESS(f'   ✅ SpotDL instalado: versão {version}')
            )
        except ImportError:
            self.stdout.write(
                self.style.ERROR('   ❌ SpotDL não instalado!')
            )
            self.stdout.write('   Execute: pip install spotdl')
            return
        
        # 2. Testar importação das classes
        self.stdout.write('\n2️⃣ Testando importações...')
        
        try:
            from spotdl import Spotdl
            self.stdout.write('   ✅ Spotdl importado')
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro ao importar Spotdl: {e}')
            )
            return
        
        # 3. Testar inicialização
        self.stdout.write('\n3️⃣ Testando inicialização...')
        
        try:
            # Tentar com credenciais do ambiente
            client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')
            
            if client_id and client_secret:
                self.stdout.write(f'   🔑 Usando credenciais: {client_id[:10]}...')
            else:
                self.stdout.write('   ⚠️ Sem credenciais - usando modo público')
                client_id = ""
                client_secret = ""
            
            # Inicializar SpotDL
            spotdl_instance = Spotdl(
                client_id=client_id,
                client_secret=client_secret
            )
            
            self.stdout.write(
                self.style.SUCCESS('   ✅ SpotDL inicializado com sucesso!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro na inicialização: {str(e)}')
            )
            
            # Tentar diagnóstico do erro
            if "config" in str(e).lower():
                self.stdout.write('   💡 Erro relacionado a config - use versão sem config')
            elif "client" in str(e).lower():
                self.stdout.write('   💡 Erro relacionado a credenciais')
            
            return
        
        # 4. Testar busca simples (sem download)
        self.stdout.write('\n4️⃣ Testando busca...')
        
        test_url = "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"  # Never Gonna Give You Up
        
        try:
            # Testar busca
            songs = spotdl_instance.search([test_url])
            
            if songs and len(songs) > 0:
                song = songs[0]
                self.stdout.write(
                    self.style.SUCCESS(f'   ✅ Música encontrada: {song.display_name}')
                )
                self.stdout.write(f'      Artista: {", ".join(song.artists) if hasattr(song, "artists") else getattr(song, "artist", "N/A")}')
                self.stdout.write(f'      Duração: {getattr(song, "duration", "N/A")}s')
            else:
                self.stdout.write(
                    self.style.WARNING('   ⚠️ Nenhuma música encontrada')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro na busca: {str(e)}')
            )
        
        # 5. Testar serviço Django
        self.stdout.write('\n5️⃣ Testando serviço Django...')
        
        try:
            from apps.baixador.services import get_spotify_service
            
            service = get_spotify_service()
            
            if service:
                health = service.health_check()
                
                if health['status'] == 'ok':
                    self.stdout.write(
                        self.style.SUCCESS('   ✅ Serviço Django funcionando!')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'   ⚠️ Serviço com problemas: {health["message"]}')
                    )
                    
                    # Mostrar detalhes se disponíveis
                    if 'details' in health:
                        for key, value in health['details'].items():
                            self.stdout.write(f'      {key}: {value}')
            else:
                self.stdout.write(
                    self.style.ERROR('   ❌ Serviço Django não inicializado')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro no serviço Django: {str(e)}')
            )
        
        # 6. Resumo e recomendações
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.HTTP_INFO('📋 RESUMO E RECOMENDAÇÕES')
        )
        
        self.stdout.write('\n✅ Se todos os testes passaram:')
        self.stdout.write('   - SpotDL está funcionando corretamente')
        self.stdout.write('   - Reinicie o servidor Django')
        self.stdout.write('   - Teste o download na interface web')
        
        self.stdout.write('\n⚠️ Se houver problemas:')
        self.stdout.write('   - Verifique se FFmpeg está instalado')
        self.stdout.write('   - Configure credenciais do Spotify (opcional mas recomendado)')
        self.stdout.write('   - Execute: pip install --upgrade spotdl')
        
        self.stdout.write('\n🔑 Para configurar credenciais do Spotify:')
        self.stdout.write('   1. Acesse: https://developer.spotify.com/dashboard')
        self.stdout.write('   2. Crie um app e obtenha Client ID e Secret')
        self.stdout.write('   3. Configure as variáveis de ambiente:')
        self.stdout.write('      export SPOTIFY_CLIENT_ID="seu_client_id"')
        self.stdout.write('      export SPOTIFY_CLIENT_SECRET="seu_client_secret"')
        
        self.stdout.write('\n🎯 Próximos passos:')
        self.stdout.write('   1. Se tudo estiver OK, reinicie: python manage.py runserver')
        self.stdout.write('   2. Acesse o painel do usuário')
        self.stdout.write('   3. Teste um download real')