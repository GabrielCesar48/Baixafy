# fix_ffmpeg_django.py - Script para diagnosticar e corrigir FFmpeg no Django
import os
import sys
import subprocess
import shutil
from pathlib import Path

def verificar_ffmpeg_detalhado():
    """
    Verifica FFmpeg de forma detalhada para Django.
    
    Returns:
        dict: Status completo do FFmpeg
    """
    print("🔍 DIAGNÓSTICO COMPLETO DO FFMPEG\n")
    print("=" * 50)
    
    status = {
        'ffmpeg_no_path': False,
        'ffmpeg_path': None,
        'ffmpeg_funciona': False,
        'ffmpeg_versao': None,
        'erro_django': None
    }
    
    # 1. Verificar se está no PATH
    print("1️⃣ Verificando PATH do sistema...")
    ffmpeg_path = shutil.which('ffmpeg')
    
    if ffmpeg_path:
        print(f"   ✅ FFmpeg encontrado: {ffmpeg_path}")
        status['ffmpeg_no_path'] = True
        status['ffmpeg_path'] = ffmpeg_path
    else:
        print("   ❌ FFmpeg NÃO está no PATH")
        
        # Verificar locais comuns no Windows
        print("   🔍 Procurando em locais comuns...")
        caminhos_comuns = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
            Path.home() / 'ffmpeg' / 'bin' / 'ffmpeg.exe',
        ]
        
        for caminho in caminhos_comuns:
            if Path(caminho).exists():
                print(f"   ✅ Encontrado em: {caminho}")
                status['ffmpeg_path'] = str(caminho)
                break
        else:
            print("   ❌ FFmpeg não encontrado em locais comuns")
    
    # 2. Testar execução
    if status['ffmpeg_path']:
        print(f"\n2️⃣ Testando execução do FFmpeg...")
        try:
            # Teste 1: Versão
            result = subprocess.run(
                [status['ffmpeg_path'], '-version'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                versao = result.stdout.split('\n')[0]
                print(f"   ✅ FFmpeg funciona: {versao}")
                status['ffmpeg_funciona'] = True
                status['ffmpeg_versao'] = versao
            else:
                print(f"   ❌ Erro ao executar: {result.stderr}")
                status['erro_django'] = result.stderr
                
        except subprocess.TimeoutExpired:
            print("   ❌ Timeout ao executar FFmpeg")
            status['erro_django'] = "Timeout"
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            status['erro_django'] = str(e)
    
    # 3. Simular chamada do Django
    print(f"\n3️⃣ Simulando como Django chama FFmpeg...")
    try:
        # Exatamente como o Django tenta chamar
        result = subprocess.run(
            ['ffmpeg', '-version'], 
            capture_output=True, 
            timeout=5
        )
        
        if result.returncode == 0:
            print("   ✅ Django conseguiria chamar FFmpeg")
        else:
            print("   ❌ Django NÃO conseguiria chamar FFmpeg")
            print(f"   Motivo: {result.stderr.decode() if result.stderr else 'Erro desconhecido'}")
            
    except FileNotFoundError:
        print("   ❌ Django NÃO conseguiria chamar FFmpeg")
        print("   Motivo: Comando 'ffmpeg' não encontrado")
        status['erro_django'] = "Comando não encontrado no PATH"
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        status['erro_django'] = str(e)
    
    return status

def corrigir_path_windows(caminho_ffmpeg):
    """
    Adiciona FFmpeg ao PATH do usuário no Windows.
    
    Args:
        caminho_ffmpeg (str): Caminho para a pasta bin do FFmpeg
    """
    try:
        import winreg
        
        # Abrir chave do registro
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 
            'Environment', 
            0, 
            winreg.KEY_ALL_ACCESS
        )
        
        try:
            # Obter PATH atual
            path_atual, _ = winreg.QueryValueEx(key, 'PATH')
        except FileNotFoundError:
            path_atual = ''
        
        # Verificar se já está no PATH
        if caminho_ffmpeg.lower() not in path_atual.lower():
            novo_path = f"{path_atual};{caminho_ffmpeg}" if path_atual else caminho_ffmpeg
            winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, novo_path)
            print(f"✅ {caminho_ffmpeg} adicionado ao PATH")
            print("⚠️  IMPORTANTE: Reinicie o VSCode/PyCharm e o terminal")
            return True
        else:
            print(f"✅ {caminho_ffmpeg} já está no PATH")
            return True
        
        winreg.CloseKey(key)
        
    except Exception as e:
        print(f"❌ Erro ao modificar PATH: {e}")
        return False

def criar_helper_django():
    """
    Cria um helper para o Django encontrar FFmpeg.
    """
    helper_code = '''# ffmpeg_helper.py - Adicione ao seu app Django
import os
import shutil
import subprocess
from pathlib import Path
from django.conf import settings

class FFmpegHelper:
    """Helper para o Django encontrar e usar FFmpeg."""
    
    def __init__(self):
        self.ffmpeg_path = self._encontrar_ffmpeg()
    
    def _encontrar_ffmpeg(self):
        """Encontra FFmpeg de todas as formas possíveis."""
        
        # 1. Verificar se está configurado no settings.py
        if hasattr(settings, 'FFMPEG_PATH'):
            if os.path.exists(settings.FFMPEG_PATH):
                return settings.FFMPEG_PATH
        
        # 2. Verificar PATH do sistema
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
        
        # 3. Verificar locais comuns no Windows
        caminhos_comuns = [
            r'C:\\ffmpeg\\bin\\ffmpeg.exe',
            r'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe',
            r'C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe',
            Path.home() / 'ffmpeg' / 'bin' / 'ffmpeg.exe',
        ]
        
        for caminho in caminhos_comuns:
            if Path(caminho).exists():
                return str(caminho)
        
        return None
    
    def esta_disponivel(self):
        """Verifica se FFmpeg está disponível."""
        if not self.ffmpeg_path:
            return False
        
        try:
            subprocess.run(
                [self.ffmpeg_path, '-version'], 
                capture_output=True, 
                check=True, 
                timeout=5
            )
            return True
        except:
            return False
    
    def obter_comando_base(self):
        """Retorna o comando base para usar com subprocess."""
        return self.ffmpeg_path if self.ffmpeg_path else 'ffmpeg'

# Instância global
ffmpeg_helper = FFmpegHelper()

def verificar_ffmpeg_para_django():
    """
    Função para usar nas suas views para verificar FFmpeg.
    
    Returns:
        dict: Status do FFmpeg para o Django
    """
    helper = FFmpegHelper()
    
    return {
        'disponivel': helper.esta_disponivel(),
        'caminho': helper.ffmpeg_path,
        'comando': helper.obter_comando_base()
    }
'''
    
    with open('ffmpeg_helper.py', 'w', encoding='utf-8') as f:
        f.write(helper_code)
    
    print("✅ Arquivo 'ffmpeg_helper.py' criado!")
    print("📋 Agora adicione ao seu projeto:")
    print("   1. Copie ffmpeg_helper.py para o seu app")
    print("   2. Importe: from .ffmpeg_helper import verificar_ffmpeg_para_django")

def main():
    """Função principal."""
    print("🔧 CORRETOR DE FFMPEG PARA DJANGO\n")
    
    # Fazer diagnóstico
    status = verificar_ffmpeg_detalhado()
    
    print(f"\n" + "=" * 50)
    print("📋 RESUMO:")
    
    if status['ffmpeg_funciona']:
        print("✅ FFmpeg está instalado e funcionando")
        print(f"📍 Localização: {status['ffmpeg_path']}")
        
        if not status['ffmpeg_no_path']:
            print("\n⚠️  PROBLEMA IDENTIFICADO:")
            print("FFmpeg não está no PATH do sistema!")
            
            # Oferecer correção
            caminho_bin = str(Path(status['ffmpeg_path']).parent)
            resposta = input(f"\n❓ Adicionar {caminho_bin} ao PATH? (s/n): ")
            
            if resposta.lower() in ['s', 'sim', 'y', 'yes']:
                if corrigir_path_windows(caminho_bin):
                    print("\n🎉 CORREÇÃO APLICADA!")
                    print("⚠️  REINICIE o VSCode/PyCharm e o terminal")
                else:
                    print("\n❌ Falha na correção automática")
                    print("🔧 CORREÇÃO MANUAL:")
                    print(f"   1. Abra Configurações do Sistema > Variáveis de Ambiente")
                    print(f"   2. Adicione {caminho_bin} ao PATH")
                    print(f"   3. Reinicie o terminal")
    
    else:
        print("❌ PROBLEMAS ENCONTRADOS:")
        if not status['ffmpeg_path']:
            print("   • FFmpeg não está instalado")
        elif status['erro_django']:
            print(f"   • Erro: {status['erro_django']}")
    
    # Criar helper
    print(f"\n" + "=" * 50)
    resposta = input("❓ Criar helper Django para FFmpeg? (s/n): ")
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        criar_helper_django()
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print("1. Reinicie o terminal/IDE")
    print("2. Teste novamente sua aplicação Django")
    print("3. Se ainda não funcionar, use o ffmpeg_helper.py")

if __name__ == '__main__':
    main()