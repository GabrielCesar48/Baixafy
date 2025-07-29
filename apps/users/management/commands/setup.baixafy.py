from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import os

User = get_user_model()

class Command(BaseCommand):
    """
    Comando para configuração inicial do BaixaFy.
    Cria usuários de teste, dados de exemplo e verifica configurações.
    """
    
    help = 'Configura o ambiente inicial do BaixaFy com dados de teste'
    
    def add_arguments(self, parser):
        """
        Adiciona argumentos ao comando.
        
        Args:
            parser: Parser de argumentos do comando
        """
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Cria dados de demonstração'
        )
        
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reseta todos os dados (CUIDADO!)'
        )
    
    def handle(self, *args, **options):
        """
        Executa o comando principal.
        
        Args:
            *args: Argumentos posicionais
            **options: Argumentos nomeados
        """
        self.stdout.write(
            self.style.SUCCESS('🎵 Configurando BaixaFy...')
        )
        
        # Verificar configurações essenciais
        self.check_settings()
        
        # Criar diretórios necessários
        self.create_directories()
        
        if options['reset']:
            self.reset_data()
        
        if options['demo']:
            self.create_demo_data()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Setup concluído com sucesso!')
        )
    
    def check_settings(self):
        """
        Verifica se as configurações essenciais estão corretas.
        """
        self.stdout.write('🔍 Verificando configurações...')
        
        # Verificar SECRET_KEY
        if not settings.SECRET_KEY or settings.SECRET_KEY.startswith('django-insecure'):
            self.stdout.write(
                self.style.WARNING('⚠️  SECRET_KEY não configurada adequadamente')
            )
        
        # Verificar MEDIA_ROOT
        if not settings.MEDIA_ROOT:
            self.stdout.write(
                self.style.ERROR('❌ MEDIA_ROOT não configurado')
            )
            return
        
        # Verificar AUTH_USER_MODEL
        if not hasattr(settings, 'AUTH_USER_MODEL'):
            self.stdout.write(
                self.style.ERROR('❌ AUTH_USER_MODEL não configurado')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('✅ Configurações verificadas')
        )
    
    def create_directories(self):
        """
        Cria diretórios necessários para o funcionamento.
        """
        self.stdout.write('📁 Criando diretórios...')
        
        directories = [
            settings.MEDIA_ROOT,
            os.path.join(settings.BASE_DIR, 'static'),
            os.path.join(settings.BASE_DIR, 'staticfiles'),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.stdout.write(f'   ✓ {directory}')
        
        self.stdout.write(
            self.style.SUCCESS('✅ Diretórios criados')
        )
    
    def reset_data(self):
        """
        Reseta todos os dados de usuários (CUIDADO!).
        """
        self.stdout.write(
            self.style.WARNING('⚠️  Resetando dados de usuários...')
        )
        
        # Confirmar ação
        confirm = input('Tem certeza? Isso apagará TODOS os usuários (exceto superusers). Digite "confirmar": ')
        
        if confirm.lower() != 'confirmar':
            self.stdout.write('❌ Operação cancelada')
            return
        
        # Deletar usuários não-staff
        deleted_count = User.objects.filter(is_staff=False).delete()[0]
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {deleted_count} usuários removidos')
        )
    
    def create_demo_data(self):
        """
        Cria dados de demonstração para testes.
        """
        self.stdout.write('🎭 Criando dados de demonstração...')
        
        # Usuário gratuito
        free_user, created = User.objects.get_or_create(
            username='usuario_free',
            defaults={
                'email': 'free@baixafy.com',
                'first_name': 'Usuário',
                'last_name': 'Gratuito',
                'free_downloads_used': 0,
                'total_downloads': 0
            }
        )
        
        if created:
            free_user.set_password('123456')
            free_user.save()
            self.stdout.write('   ✓ Usuário gratuito criado')
        
        # Usuário premium
        premium_user, created = User.objects.get_or_create(
            username='usuario_premium',
            defaults={
                'email': 'premium@baixafy.com',
                'first_name': 'Usuário',
                'last_name': 'Premium',
                'total_downloads': 25
            }
        )
        
        if created:
            premium_user.set_password('123456')
            premium_user.activate_premium(days=30)
            self.stdout.write('   ✓ Usuário premium criado')
        
        # Usuário com downloads usados
        used_user, created = User.objects.get_or_create(
            username='usuario_usado',
            defaults={
                'email': 'usado@baixafy.com',
                'first_name': 'Usuário',
                'last_name': 'Limitado',
                'free_downloads_used': 1,
                'total_downloads': 1
            }
        )
        
        if created:
            used_user.set_password('123456')
            used_user.save()
            self.stdout.write('   ✓ Usuário com limite atingido criado')
        
        self.stdout.write(
            self.style.SUCCESS('✅ Dados de demonstração criados')
        )
        
        # Exibir informações de login
        self.stdout.write('\n🔑 Contas de teste criadas:')
        self.stdout.write('   👤 Gratuito: usuario_free / 123456')
        self.stdout.write('   👑 Premium: usuario_premium / 123456')
        self.stdout.write('   🚫 Limitado: usuario_usado / 123456')


# users/management/commands/check_downloads.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import DownloadHistory
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    """
    Comando para verificar estatísticas de downloads.
    Útil para monitoramento e análise de uso.
    """
    
    help = 'Verifica estatísticas de downloads do BaixaFy'
    
    def handle(self, *args, **options):
        """
        Gera relatório de estatísticas de downloads.
        """
        self.stdout.write(
            self.style.SUCCESS('📊 Relatório de Downloads - BaixaFy')
        )
        self.stdout.write('=' * 50)
        
        # Estatísticas gerais
        total_users = User.objects.count()
        premium_users = User.objects.filter(
            is_subscriber=True,
            payment_valid_until__gt=timezone.now()
        ).count()
        
        total_downloads = DownloadHistory.objects.count()
        successful_downloads = DownloadHistory.objects.filter(success=True).count()
        failed_downloads = DownloadHistory.objects.filter(success=False).count()
        
        self.stdout.write(f'\n👥 USUÁRIOS:')
        self.stdout.write(f'   Total de usuários: {total_users}')
        self.stdout.write(f'   Usuários premium: {premium_users}')
        self.stdout.write(f'   Usuários gratuitos: {total_users - premium_users}')
        
        self.stdout.write(f'\n📥 DOWNLOADS:')
        self.stdout.write(f'   Total de tentativas: {total_downloads}')
        self.stdout.write(f'   Downloads bem-sucedidos: {successful_downloads}')
        self.stdout.write(f'   Downloads falhados: {failed_downloads}')
        
        if total_downloads > 0:
            success_rate = (successful_downloads / total_downloads) * 100
            self.stdout.write(f'   Taxa de sucesso: {success_rate:.1f}%')
        
        # Estatísticas dos últimos 7 dias
        last_week = timezone.now() - timedelta(days=7)
        recent_downloads = DownloadHistory.objects.filter(
            download_date__gte=last_week
        )
        
        self.stdout.write(f'\n📅 ÚLTIMOS 7 DIAS:')
        self.stdout.write(f'   Downloads esta semana: {recent_downloads.count()}')
        self.stdout.write(f'   Sucessos: {recent_downloads.filter(success=True).count()}')
        
        # Top usuários
        top_users = User.objects.annotate(
            download_count=Count('downloadhistory')
        ).filter(download_count__gt=0).order_by('-download_count')[:5]
        
        if top_users:
            self.stdout.write(f'\n🏆 TOP USUÁRIOS (por downloads):')
            for i, user in enumerate(top_users, 1):
                status = '👑' if user.is_premium_active() else '👤'
                self.stdout.write(
                    f'   {i}. {status} {user.username}: {user.download_count} downloads'
                )
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(
            self.style.SUCCESS('✅ Relatório concluído!')
        )