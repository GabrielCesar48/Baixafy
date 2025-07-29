from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """
    Formulário personalizado para cadastro de usuários.
    Inclui campos adicionais e validações customizadas.
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu melhor e-mail'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu primeiro nome'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customizando widgets dos campos herdados
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Escolha um nome de usuário'
        })
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Crie uma senha forte'
        })
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme sua senha'
        })
    
    def clean_email(self):
        """
        Valida se o e-mail já não está em uso.
        
        Returns:
            str: E-mail validado
            
        Raises:
            ValidationError: Se o e-mail já estiver em uso
        """
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está sendo usado por outro usuário.")
        return email
    
    def save(self, commit=True):
        """
        Salva o usuário com os dados adicionais.
        
        Args:
            commit (bool): Se deve salvar no banco imediatamente
            
        Returns:
            CustomUser: Instância do usuário criado
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulário personalizado para login de usuários.
    Melhora a experiência visual e de usabilidade.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Seu nome de usuário ou e-mail'
        })
        
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Sua senha'
        })
    
    def clean(self):
        """
        Validação customizada que permite login com e-mail ou username.
        
        Returns:
            dict: Dados limpos do formulário
            
        Raises:
            ValidationError: Se as credenciais estiverem incorretas
        """
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Tentar autenticar com username primeiro
            self.user_cache = authenticate(
                self.request, 
                username=username, 
                password=password
            )
            
            # Se não conseguir, tentar com e-mail
            if self.user_cache is None:
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    self.user_cache = authenticate(
                        self.request,
                        username=user_obj.username,
                        password=password
                    )
                except CustomUser.DoesNotExist:
                    pass
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Nome de usuário/e-mail ou senha incorretos. Tente novamente!",
                    code='invalid_login'
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data


class DownloadForm(forms.Form):
    """
    Formulário para solicitação de download de músicas.
    Valida URLs do Spotify e processa solicitações.
    """
    
    spotify_url = forms.URLField(
        label="Cole o link do Spotify aqui:",
        widget=forms.URLInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'https://open.spotify.com/track/...',
            'style': 'border-radius: 10px;'
        }),
        help_text="Cole o link de uma música ou playlist do Spotify"
    )
    
    def clean_spotify_url(self):
        """
        Valida se a URL é realmente do Spotify.
        
        Returns:
            str: URL validada
            
        Raises:
            ValidationError: Se a URL não for do Spotify
        """
        url = self.cleaned_data.get('spotify_url')
        
        if not url:
            return url
        
        # Verificar se é URL do Spotify
        valid_spotify_domains = [
            'open.spotify.com',
            'spotify.com',
            'play.spotify.com'
        ]
        
        if not any(domain in url for domain in valid_spotify_domains):
            raise forms.ValidationError(
                "Por favor, cole um link válido do Spotify."
            )
        
        # Verificar se é track ou playlist
        if not ('track/' in url or 'playlist/' in url or 'album/' in url):
            raise forms.ValidationError(
                "Link deve ser de uma música, álbum ou playlist do Spotify."
            )
        
        return url