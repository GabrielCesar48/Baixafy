# users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CustomUser, DownloadHistory

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuração do admin para o modelo CustomUser.
    Estende o UserAdmin padrão com campos personalizados.
    """
    
    # Campos exibidos na lista
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'premium_status', 'downloads_count', 'subscription_status', 
        'created_at', 'is_active'
    )
    
    # Filtros laterais
    list_filter = (
        'is_subscriber', 'is_active', 'is_staff', 
        'created_at', 'payment_valid_until'
    )
    
    # Campos de busca
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Ordenação padrão
    ordering = ('-created_at',)
    
    # Campos na visualização de detalhes
    fieldsets = UserAdmin.fieldsets + (
        ('Informações de Pagamento', {
            'fields': (
                'is_subscriber', 'payment_valid_until', 
                'free_downloads_used', 'total_downloads'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # Campos somente leitura
    readonly_fields = ('created_at', 'updated_at', 'total_downloads')
    
    # Campos no formulário de adição
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {
            'fields': ('first_name', 'last_name', 'email')
        }),
    )
    
    def premium_status(self, obj):
        """
        Exibe o status premium com formatação colorida.
        
        Args:
            obj (CustomUser): Instância do usuário
            
        Returns:
            str: HTML formatado com o status
        """
        if obj.is_premium_active():
            return format_html(
                '<span style="color: #1db954; font-weight: bold;">✓ Premium</span>'
            )
        else:
            return format_html(
                '<span style="color: #999;">Gratuito</span>'
            )
    premium_status.short_description = 'Status Premium'
    
    def downloads_count(self, obj):
        """
        Exibe a contagem de downloads com link para o histórico.
        
        Args:
            obj (CustomUser): Instância do usuário
            
        Returns:
            str: HTML com contagem e link
        """
        count = obj.total_downloads
        if count > 0:
            url = reverse('admin:users_downloadhistory_changelist')
            return format_html(
                '<a href="{}?user__id__exact={}" style="color: #1db954;">{} downloads</a>',
                url, obj.id, count
            )
        return format_html('<span style="color: #999;">0 downloads</span>')
    downloads_count.short_description = 'Downloads'
    
    def subscription_status(self, obj):
        """
        Exibe informações detalhadas da assinatura.
        
        Args:
            obj (CustomUser): Instância do usuário
            
        Returns:
            str: HTML com informações da assinatura
        """
        if obj.is_premium_active():
            days = obj.days_remaining()
            return format_html(
                '<span style="color: #1db954;">{} dias restantes</span>',
                days
            )
        elif obj.is_subscriber and not obj.is_premium_active():
            return format_html(
                '<span style="color: #ff6b6b;">Expirado</span>'
            )
        else:
            free_used = obj.free_downloads_used
            return format_html(
                '<span style="color: #999;">{}/1 grátis usado</span>',
                free_used
            )
    subscription_status.short_description = 'Assinatura'
    
    # Ações personalizadas
    actions = ['activate_premium', 'deactivate_premium', 'reset_free_downloads']
    
    def activate_premium(self, request, queryset):
        """
        Ação para ativar premium em massa.
        
        Args:
            request: Requisição HTTP
            queryset: Usuários selecionados
        """
        for user in queryset:
            user.activate_premium(days=30)
        
        self.message_user(
            request, 
            f'{queryset.count()} usuário(s) ativado(s) como premium.'
        )
    activate_premium.short_description = 'Ativar premium (30 dias)'
    
    def deactivate_premium(self, request, queryset):
        """
        Ação para desativar premium em massa.
        
        Args:
            request: Requisição HTTP
            queryset: Usuários selecionados
        """
        queryset.update(is_subscriber=False, payment_valid_until=None)
        self.message_user(
            request, 
            f'{queryset.count()} usuário(s) teve premium desativado.'
        )
    deactivate_premium.short_description = 'Desativar premium'
    
    def reset_free_downloads(self, request, queryset):
        """
        Ação para resetar downloads gratuitos.
        
        Args:
            request: Requisição HTTP
            queryset: Usuários selecionados
        """
        queryset.update(free_downloads_used=0)
        self.message_user(
            request, 
            f'{queryset.count()} usuário(s) teve downloads gratuitos resetados.'
        )
    reset_free_downloads.short_description = 'Resetar downloads gratuitos'


@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo DownloadHistory.
    Permite visualização e gestão do histórico de downloads.
    """
    
    # Campos exibidos na lista
    list_display = (
        'song_title', 'artist_name', 'user_link', 
        'download_status', 'download_date', 'spotify_link'
    )
    
    # Filtros laterais
    list_filter = (
        'success', 'download_date', 'user__is_subscriber'
    )
    
    # Campos de busca
    search_fields = (
        'song_title', 'artist_name', 'album_name', 
        'user__username', 'user__email'
    )
    
    # Ordenação padrão
    ordering = ('-download_date',)
    
    # Campos somente leitura
    readonly_fields = ('download_date',)
    
    # Campos no formulário
    fields = (
        'user', 'spotify_url', 'song_title', 'artist_name', 
        'album_name', 'file_path', 'success', 'download_date'
    )
    
    # Paginação
    list_per_page = 50
    
    def user_link(self, obj):
        """
        Cria link para o usuário no admin.
        
        Args:
            obj (DownloadHistory): Instância do histórico
            
        Returns:
            str: HTML com link para o usuário
        """
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        premium_icon = '👑' if obj.user.is_premium_active() else '👤'
        return format_html(
            '<a href="{}">{} {}</a>',
            url, premium_icon, obj.user.username
        )
    user_link.short_description = 'Usuário'
    
    def download_status(self, obj):
        """
        Exibe o status do download com formatação.
        
        Args:
            obj (DownloadHistory): Instância do histórico
            
        Returns:
            str: HTML formatado com o status
        """
        if obj.success:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Sucesso</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✗ Falhou</span>'
            )
    download_status.short_description = 'Status'
    
    def spotify_link(self, obj):
        """
        Cria link para o Spotify.
        
        Args:
            obj (DownloadHistory): Instância do histórico
            
        Returns:
            str: HTML com link para o Spotify
        """
        if obj.spotify_url:
            return format_html(
                '<a href="{}" target="_blank" style="color: #1db954;">🎵 Ver no Spotify</a>',
                obj.spotify_url
            )
        return '-'
    spotify_link.short_description = 'Spotify'
    
    # Ações personalizadas
    actions = ['mark_as_success', 'mark_as_failed', 'export_csv']
    
    def mark_as_success(self, request, queryset):
        """
        Marca downloads como bem-sucedidos.
        
        Args:
            request: Requisição HTTP
            queryset: Downloads selecionados
        """
        queryset.update(success=True)
        self.message_user(
            request, 
            f'{queryset.count()} download(s) marcado(s) como sucesso.'
        )
    mark_as_success.short_description = 'Marcar como bem-sucedido'
    
    def mark_as_failed(self, request, queryset):
        """
        Marca downloads como falhados.
        
        Args:
            request: Requisição HTTP
            queryset: Downloads selecionados
        """
        queryset.update(success=False)
        self.message_user(
            request, 
            f'{queryset.count()} download(s) marcado(s) como falha.'
        )
    mark_as_failed.short_description = 'Marcar como falha'


# Personalização do Admin Site
admin.site.site_header = 'BaixaFy - Administração'
admin.site.site_title = 'BaixaFy Admin'
admin.site.index_title = 'Painel Administrativo'

# Registrar modelos do Django padrão (opcional)
from django.contrib.auth.models import Group
admin.site.unregister(Group)