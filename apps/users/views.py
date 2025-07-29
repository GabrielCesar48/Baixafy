# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views import View
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser


class RegisterView(View):
    """
    View para cadastro de novos usuários.
    Processa formulário de registro e cria conta automaticamente.
    """
    
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    
    def get(self, request):
        """
        Exibe formulário de cadastro.
        
        Args:
            request: Objeto de requisição HTTP
            
        Returns:
            HttpResponse: Página de cadastro com formulário
        """
        # Redirecionar se já estiver logado
        if request.user.is_authenticated:
            return redirect('painel')
        
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """
        Processa dados do formulário de cadastro.
        
        Args:
            request: Objeto de requisição HTTP com dados POST
            
        Returns:
            HttpResponse: Redirect para painel ou formulário com erros
        """
        form = self.form_class(request.POST)
        
        if form.is_valid():
            try:
                user = form.save()
                
                # Fazer login automático após cadastro
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=password)
                
                if user:
                    login(request, user)
                    
                    messages.success(
                        request,
                        f"🎉 Bem-vindo(a) ao BaixaFy, {user.first_name}! "
                        "Sua conta foi criada com sucesso. "
                        "Você tem 1 download gratuito para testar nosso serviço!"
                    )
                    
                    return redirect('painel')
                
            except Exception as e:
                messages.error(
                    request,
                    f"Erro ao criar conta: {str(e)}"
                )
        
        return render(request, self.template_name, {'form': form})


class CustomLoginView(LoginView):
    """
    View customizada para login de usuários.
    Utiliza formulário personalizado e templates customizados.
    """
    
    template_name = 'login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        """
        Define URL de redirecionamento após login bem-sucedido.
        
        Returns:
            str: URL de redirecionamento
        """
        return reverse_lazy('painel')
    
    def form_valid(self, form):
        """
        Processa login válido com mensagem de boas-vindas.
        
        Args:
            form: Formulário de autenticação validado
            
        Returns:
            HttpResponse: Redirect para página de sucesso
        """
        user = form.get_user()
        
        # Mensagem personalizada baseada no status do usuário
        if user.is_premium_active():
            greeting = f"🎵 Olá, {user.first_name}! Bem-vindo de volta ao BaixaFy!"
            status_msg = f"Sua assinatura premium está ativa por mais {user.days_remaining()} dias."
        else:
            greeting = f"👋 Olá, {user.first_name}! Bem-vindo de volta!"
            if user.free_downloads_used < 1:
                status_msg = "Você ainda tem seu download gratuito disponível!"
            else:
                status_msg = "Que tal assinar o plano premium para downloads ilimitados?"
        
        messages.success(self.request, f"{greeting} {status_msg}")
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Trata erros de login com mensagens personalizadas.
        
        Args:
            form: Formulário com erros de validação
            
        Returns:
            HttpResponse: Página de login com erros
        """
        messages.error(
            self.request,
            "🚫 Ops! Credenciais incorretas. Verifique seu usuário/e-mail e senha."
        )
        
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    View customizada para logout de usuários.
    Adiciona mensagem de despedida personalizada.
    """
    
    next_page = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        """
        Processa logout com mensagem de despedida.
        
        Args:
            request: Objeto de requisição HTTP
            
        Returns:
            HttpResponse: Redirect para página inicial
        """
        if request.user.is_authenticated:
            user_name = request.user.first_name or request.user.username
            
            messages.info(
                request,
                f"👋 Até logo, {user_name}! Obrigado por usar o BaixaFy. "
                "Volte sempre que quiser baixar suas músicas favoritas!"
            )
        
        return super().dispatch(request, *args, **kwargs)


def profile_view(request):
    """
    Página de perfil do usuário com informações detalhadas.
    Mostra estatísticas de uso e status da assinatura.
    
    Args:
        request: Objeto de requisição HTTP
        
    Returns:
        HttpResponse: Página de perfil renderizada
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    
    # Estatísticas do usuário
    from users.models import DownloadHistory
    
    recent_downloads = DownloadHistory.objects.filter(
        user=user,
        success=True
    ).order_by('-download_date')[:10]
    
    failed_downloads = DownloadHistory.objects.filter(
        user=user,
        success=False
    ).count()
    
    context = {
        'user': user,
        'is_premium': user.is_premium_active(),
        'days_remaining': user.days_remaining(),
        'total_downloads': user.total_downloads,
        'free_downloads_used': user.free_downloads_used,
        'recent_downloads': recent_downloads,
        'failed_downloads': failed_downloads,
        'subscription_expired': (
            user.is_subscriber and not user.is_premium_active()
        )
    }
    
    return render(request, 'profile.html', context)