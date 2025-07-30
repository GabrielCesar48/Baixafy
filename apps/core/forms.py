"""
Formulários para BaixaFy Desktop
"""

from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from urllib.parse import urlparse


class DownloadForm(forms.Form):
    """Formulário para download de música"""
    spotify_url = forms.URLField(
        label='URL do Spotify',
        widget=forms.URLInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Cole aqui o link da música ou playlist do Spotify...',
            'autocomplete': 'off',
        }),
        help_text='Cole o link de uma música, álbum ou playlist do Spotify'
    )
    
    def clean_spotify_url(self):
        url = self.cleaned_data['spotify_url']
        
        if 'spotify.com' not in url:
            raise ValidationError('A URL deve ser do Spotify.')
        
        if not any(x in url for x in ['/track/', '/playlist/', '/album/']):
            raise ValidationError('URL deve ser de uma música, playlist ou álbum.')
        
        return url


class ActivationForm(forms.Form):
    """Formulário para ativação de licença"""
    activation_code = forms.CharField(
        label='Código de Ativação',
        max_length=25,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': 'XXXX-XXXX-XXXX-XXXX-XXXX',
            'style': 'letter-spacing: 2px; font-family: monospace;',
        }),
        help_text='Digite a chave de ativação de 20 dígitos'
    )
    
    def clean_activation_code(self):
        code = self.cleaned_data['activation_code'].strip().upper()
        code = code.replace('-', '').replace(' ', '')
        
        if len(code) != 20:
            raise ValidationError('Código deve ter 20 dígitos.')
        
        return code