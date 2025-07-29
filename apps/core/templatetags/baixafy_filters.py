# core/templatetags/__init__.py
# (arquivo vazio)

# core/templatetags/baixafy_filters.py
import os
from django import template

register = template.Library()

@register.filter
def filename(value):
    """
    Extrai o nome do arquivo de um caminho completo.
    
    Args:
        value (str): Caminho completo do arquivo
        
    Returns:
        str: Nome do arquivo
        
    Usage:
        {{ file_path|filename }}
    """
    if not value:
        return ""
    return os.path.basename(str(value))

@register.filter
def split(value, arg):
    """
    Divide uma string usando um separador.
    
    Args:
        value (str): String a ser dividida
        arg (str): Separador
        
    Returns:
        list: Lista com as partes divididas
        
    Usage:
        {{ "path/to/file.mp3"|split:"/"|last }}
    """
    if not value:
        return []
    return str(value).split(str(arg))

@register.filter
def file_size(value):
    """
    Converte tamanho de arquivo em bytes para formato legível.
    
    Args:
        value (int): Tamanho em bytes
        
    Returns:
        str: Tamanho formatado (ex: "3.2 MB")
    """
    if not value or value == 0:
        return "0 B"
    
    try:
        size = int(value)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except (ValueError, TypeError):
        return "N/A"

@register.filter
def truncate_title(value, length=30):
    """
    Trunca o título da música se for muito longo.
    
    Args:
        value (str): Título da música
        length (int): Comprimento máximo
        
    Returns:
        str: Título truncado
    """
    if not value:
        return ""
    
    if len(value) <= length:
        return value
    
    return value[:length] + "..."

@register.filter
def premium_badge(user):
    """
    Retorna HTML para badge de status premium.
    
    Args:
        user: Instância do usuário
        
    Returns:
        str: HTML do badge
    """
    if user.is_premium_active():
        return '<span class="badge bg-spotify">👑 Premium</span>'
    else:
        return '<span class="badge bg-secondary">👤 Gratuito</span>'

@register.filter
def download_status_icon(success):
    """
    Retorna ícone baseado no status do download.
    
    Args:
        success (bool): Se o download foi bem-sucedido
        
    Returns:
        str: HTML do ícone
    """
    if success:
        return '<i class="fas fa-check-circle text-success"></i>'
    else:
        return '<i class="fas fa-times-circle text-danger"></i>'

@register.simple_tag
def download_progress_bar(current, total):
    """
    Cria uma barra de progresso para downloads.
    
    Args:
        current (int): Progresso atual
        total (int): Total
        
    Returns:
        str: HTML da barra de progresso
    """
    if total == 0:
        percentage = 0
    else:
        percentage = (current / total) * 100
    
    return f'''
    <div class="progress" style="height: 8px;">
        <div class="progress-bar bg-spotify" 
             role="progressbar" 
             style="width: {percentage}%"
             aria-valuenow="{current}" 
             aria-valuemin="0" 
             aria-valuemax="{total}">
        </div>
    </div>
    <small class="text-muted">{current}/{total} músicas</small>
    '''