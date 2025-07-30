"""
Models para BaixaFy Desktop Application
Sistema de licenças locais e controle de downloads
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import os
import json
import hashlib
import platform


class DesktopLicense(models.Model):
    """
    Modelo para gerenciar licenças da versão desktop
    Substitui o sistema de pagamento online
    """
    LICENSE_TYPES = [
        ('trial', 'Trial (1 download)'),
        ('activated', 'Ativado (30 dias)'),
        ('expired', 'Expirado'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='desktop_license')
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPES, default='trial')
    activation_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    activation_code = models.CharField(max_length=100, null=True, blank=True)
    hardware_id = models.CharField(max_length=100, null=True, blank=True)
    downloads_used = models.IntegerField(default=0)
    max_downloads = models.IntegerField(default=10)  # 10 para trial, ilimitado para ativado
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Licença Desktop"
        verbose_name_plural = "Licenças Desktop"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_license_type_display()}"
    
    @property
    def is_active(self):
        """Verifica se a licença está ativa e válida"""
        if self.license_type == 'trial':
            return self.downloads_used < self.max_downloads
        elif self.license_type == 'activated':
            return self.expiry_date and self.expiry_date > timezone.now()
        return False
    
    @property
    def days_remaining(self):
        """Retorna quantos dias restam na licença"""
        if self.license_type == 'activated' and self.expiry_date:
            delta = self.expiry_date - timezone.now()
            return max(0, delta.days)
        return 0
    
    @property
    def downloads_remaining(self):
        """Retorna quantos downloads restam"""
        if self.license_type == 'trial':
            return max(0, self.max_downloads - self.downloads_used)
        elif self.license_type == 'activated' and self.is_active:
            return float('inf')  # Ilimitado
        return 0
    
    def activate_license(self, activation_code):
        """
        Ativa a licença com código de ativação
        """
        # Validar código de ativação (implementar sua lógica)
        if self.validate_activation_code(activation_code):
            self.license_type = 'activated'
            self.activation_code = activation_code
            self.activation_date = timezone.now()
            self.expiry_date = timezone.now() + timedelta(days=30)
            self.max_downloads = 999999  # Ilimitado
            self.hardware_id = self.generate_hardware_id()
            self.save()
            return True
        return False
    
    def validate_activation_code(self, code):
        """
        Valida código de ativação
        Implementar sua lógica de validação aqui
        """
        # Exemplo simples: códigos pré-definidos
        valid_codes = [
            'BAIXAFY2024PRO',
            'MUSICLOVER30D',
            'SPOTDL999FREE',
        ]
        return code.upper() in valid_codes
    
    def generate_hardware_id(self):
        """
        Gera ID único baseado no hardware da máquina
        """
        try:
            # Combina informações do sistema
            system_info = f"{platform.node()}-{platform.processor()}-{platform.system()}"
            return hashlib.md5(system_info.encode()).hexdigest()[:16]
        except:
            return "generic-hardware-id"
    
    def increment_download_count(self):
        """
        Incrementa contador de downloads usados
        """
        self.downloads_used += 1
        self.save()
    
    def reset_trial(self):
        """
        Reseta trial (apenas para debug/admin)
        """
        self.downloads_used = 0
        self.license_type = 'trial'
        self.max_downloads = 1
        self.save()


class DownloadHistory(models.Model):
    """
    Histórico de downloads realizados pelo usuário
    """
    DOWNLOAD_STATUS = [
        ('pending', 'Pendente'),
        ('downloading', 'Baixando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='downloads')
    spotify_url = models.URLField(max_length=500)
    track_name = models.CharField(max_length=200, null=True, blank=True)
    artist_name = models.CharField(max_length=200, null=True, blank=True)
    album_name = models.CharField(max_length=200, null=True, blank=True)
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # em bytes
    status = models.CharField(max_length=20, choices=DOWNLOAD_STATUS, default='pending')
    error_message = models.TextField(null=True, blank=True)
    download_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Histórico de Download"
        verbose_name_plural = "Histórico de Downloads"
        ordering = ['-download_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.track_name or 'Unknown'}"
    
    @property
    def file_exists(self):
        """Verifica se o arquivo ainda existe no sistema"""
        return self.file_path and os.path.exists(self.file_path)
    
    @property
    def file_size_mb(self):
        """Retorna tamanho do arquivo em MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0


class AppSettings(models.Model):
    """
    Configurações da aplicação desktop
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração da App"
        verbose_name_plural = "Configurações da App"
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
    
    @classmethod
    def get_setting(cls, key, default=None):
        """
        Busca uma configuração pelo key
        """
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_setting(cls, key, value, description=None):
        """
        Define ou atualiza uma configuração
        """
        setting, created = cls.objects.get_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        if not created:
            setting.value = value
            if description:
                setting.description = description
            setting.save()
        return setting


# Signal para criar licença automaticamente quando usuário é criado
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_desktop_license(sender, instance, created, **kwargs):
    """
    Cria automaticamente uma licença trial quando usuário é criado
    """
    if created:
        DesktopLicense.objects.create(
            user=instance,
            license_type='trial',
            max_downloads=10  # 10 downloads no trial
        )

@receiver(post_save, sender=User)
def save_desktop_license(sender, instance, **kwargs):
    """
    Salva a licença quando usuário é salvo
    """
    if hasattr(instance, 'desktop_license'):
        instance.desktop_license.save()