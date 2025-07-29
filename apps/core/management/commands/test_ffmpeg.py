# apps/core/management/commands/test_ffmpeg.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import subprocess
import shutil
from pathlib import Path

class Command(BaseCommand):
    help = 'Testa e diagnostica FFmpeg no Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Tenta corrigir problemas automaticamente'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('🔍 DIAGNÓSTICO DO FFMPEG NO DJANGO')
        )
        self.stdout.write('=' * 50)
        
        # 1. Verificar configuração do settings
        self.stdout.write('\n1️⃣ Verificando configuração do settings.py...')
        
        if hasattr(settings, 'FFMPEG_PATH') and settings.FFMPEG_PATH:
            self.stdout.write(
                self.style.SUCCESS(f'   ✅ FFMPEG_PATH configurado: {settings.FFMPEG_PATH}')
            )
            
            if Path(settings.FFMPEG_PATH).exists():
                self.stdout.write('   ✅ Arquivo existe')
            else:
                self.stdout.write(
                    self.style.ERROR('   ❌ Arquivo não existe!')
                )
        else:
            self.stdout.write(
                self.style.WARNING('   ⚠️ FFMPEG_PATH não configurado')
            )
        
        # 2. Verificar PATH do sistema
        self.stdout.write('\n2️⃣ Verificando PATH do sistema...')
        ffmpeg_in_path = shutil.which('ffmpeg')
        
        if ffmpeg_in_path:
            self.stdout.write(
                self.style.SUCCESS(f'   ✅ FFmpeg no PATH: {ffmpeg_in_path}')
            )
        else:
            self.stdout.write(
                self.style.ERROR('   ❌ FFmpeg NÃO está no PATH')
            )
        
        # 3. Testar execução
        self.stdout.write('\n3️⃣ Testando execução...')
        
        # Testar com diferentes métodos
        metodos = []
        
        if hasattr(settings, 'FFMPEG_PATH') and settings.FFMPEG_PATH:
            metodos.append(('Settings', settings.FFMPEG_PATH))
        
        if ffmpeg_in_path:
            metodos.append(('PATH', 'ffmpeg'))
            
        # Locais comuns
        caminhos_comuns = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
        ]
        
        for caminho in caminhos_comuns:
            if Path(caminho).exists():
                metodos.append(('Local comum', caminho))
        
        funcionando = []
        
        for nome, comando in metodos:
            try:
                result = subprocess.run(
                    [comando, '-version'],
                    capture_output=True,
                    timeout=5,
                    check=True
                )
                
                versao = result.stdout.decode().split('\n')[0]
                self.stdout.write(
                    self.style.SUCCESS(f'   ✅ {nome}: {versao}')
                )
                funcionando.append((nome, comando))
                
            except subprocess.CalledProcessError as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ {nome}: Erro de execução')
                )
            except subprocess.TimeoutExpired:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ {nome}: Timeout')
                )
            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ {nome}: Comando não encontrado')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ {nome}: {str(e)}')
                )
        
        # 4. Testar serviço
        self.stdout.write('\n4️⃣ Testando serviço do Django...')
        
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
                        self.style.ERROR(f'   ❌ Serviço com erro: {health["message"]}')
                    )
                    
                    if 'details' in health:
                        for key, value in health['details'].items():
                            self.stdout.write(f'      {key}: {value}')
            else:
                self.stdout.write(
                    self.style.ERROR('   ❌ Serviço não inicializado')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro ao testar serviço: {str(e)}')
            )
        
        # 5. Resumo e recomendações
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.HTTP_INFO('📋 RESUMO E RECOMENDAÇÕES')
        )
        
        if funcionando:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ FFmpeg funciona via: {", ".join([f[0] for f in funcionando])}')
            )
            
            # Recomendar melhor opção
            if any('PATH' in f[0] for f in funcionando):
                self.stdout.write('✅ Recomendação: Use o FFmpeg do PATH (já funciona)')
            else:
                melhor = funcionando[0]
                self.stdout.write(f'✅ Recomendação: Configure FFMPEG_PATH = "{melhor[1]}"')
                
                if options['fix']:
                    self.stdout.write('\n🔧 Aplicando correção...')
                    self.stdout.write(f'Adicione ao settings.py: FFMPEG_PATH = "{melhor[1]}"')
        else:
            self.stdout.write(
                self.style.ERROR('\n❌ NENHUM FFmpeg funcionando!')
            )
            self.stdout.write('\n🔧 SOLUÇÕES:')
            self.stdout.write('1. Baixe FFmpeg de https://ffmpeg.org/download.html')
            self.stdout.write('2. Extraia para C:\\ffmpeg')
            self.stdout.write('3. Adicione C:\\ffmpeg\\bin ao PATH do sistema')
            self.stdout.write('4. Reinicie o terminal e teste novamente')
            
        self.stdout.write('\n🎯 PRÓXIMOS PASSOS:')
        self.stdout.write('1. Aplique as recomendações acima')
        self.stdout.write('2. Reinicie o servidor Django')
        self.stdout.write('3. Teste novamente com: python manage.py test_ffmpeg')