from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    """
    Modelo de usuário personalizado com istema de assinatura.
    Estende o User padrao do Django com funcionalidades de pagamento.
    """
    # Informações de pagamento
    payment_valid_until = models.DateTimeField(null=True, blank=True, verbose_name="Valido até")
    is_subscriber = models.BooleanField(default=False, verbose_name="É assinante")
    free_downloads_used = models.IntegerField(default=0, verbose_name="Downloads gratuitos usados")
    total_downloads = models.IntegerField(default=0, verbose_name="Total de downloads")
    
    # Data de criação personalizada
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-created_at']
        
    def is_premium_active(self) -> bool:
        """
        Verifica se a assinatura premium está ativa.
        Retorna True se a assinatura estiver ativa, False caso contrário.
        """
        if not self.is_subscriber or not self.payment_valid_until:
            return False
        return timezone.now() < self.payment_valid_until
    
    def days_remaining(self) -> int:
        """
        Retorna o número de dias restantes na assinatura.
        Se a assinatura não estiver ativa, retorna 0.
        """
        if not self.is_premium_active():
            return 0
        
        
        remaining = self.payment_valid_until - timezone.now()
        return max(0, remaining.days)


    def can_download(self) -> bool:
        """
        Verifica se o usuario pode realizar downloads.
        
        return bool: True se pode baixar, False caso contrário.
        """
        
        if self.is_premium_active():
            return True
        
        #Se nao é premium, verifica se ainda tem download gratuitos disponíveis
        return self.free_downloads_used < 1
    
    
    def activate_premium(self, days: int = 30) -> None:
        """
        Ativa a assinatura premium por um número de dias especificado.
        
        args:
            days (int): Número de dias de assinatura (padrão é 30).
            
        """
        self.is_subscriber = True
        self.payment_valid_until = timezone.now() + timedelta(days=days)
        self.save()
    
    def use_download(self) -> None:
        """
        Registra o uso de um download pelo usuário.
        Incrementa contadores apropriados.
        """
        self.total_downloads += 1
        
        if not self.is_premium_active():
            self.free_downloads_used += 1
        
        self.save()
    
    def __str__(self):
        status = "Premium" if self.is_premium_active() else "Gratuito"
        return f"{self.username} ({status})"


class DownloadHistory(models.Model):
    """
    Histórico de downloads dos usuários.
    Registra todas as músicas baixadas para controle e estatísticas.
    """
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Usuário")
    spotify_url = models.URLField(verbose_name="URL do Spotify")
    song_title = models.CharField(max_length=200, verbose_name="Título da música")
    artist_name = models.CharField(max_length=200, verbose_name="Artista")
    album_name = models.CharField(max_length=200, blank=True, verbose_name="Álbum")
    download_date = models.DateTimeField(auto_now_add=True, verbose_name="Data do download")
    file_path = models.CharField(max_length=500, blank=True, verbose_name="Caminho do arquivo")
    success = models.BooleanField(default=True, verbose_name="Download bem-sucedido")
    
    class Meta:
        verbose_name = "Histórico de Download"
        verbose_name_plural = "Históricos de Downloads"
        ordering = ['-download_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.song_title} by {self.artist_name}"