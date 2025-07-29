# fix_ffmpeg.py - Script para diagnosticar e corrigir problemas com FFmpeg
import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_ffmpeg_installation():
    """
    Verifica se FFmpeg está instalado e acessível.
    
    Returns:
        dict: Status da instalação do FFmpeg
    """
    status = {
        'installed': False,
        'path': None,
        'version': None,
        'errors': []
    }
    
    # Método 1: Verificar se está no PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        status['installed'] = True
        status['path'] = ffmpeg_path
        print(f"✅ FFmpeg encontrado no PATH: {ffmpeg_path}")
        
        # Tentar obter versão
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                status['version'] = version_line
                print(f"✅ Versão: {version_line}")
            else:
                status['errors'].append("Erro ao obter versão do FFmpeg")
        except subprocess.TimeoutExpired:
            status['errors'].append("Timeout ao executar FFmpeg")
        except Exception as e:
            status['errors'].append(f"Erro ao executar FFmpeg: {e}")
    else:
        print("❌ FFmpeg não encontrado no PATH")
        status['errors'].append("FFmpeg não está no PATH do sistema")
        
        # Método 2: Verificar locais comuns no Windows
        common_paths = [
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe',
            Path.home() / 'ffmpeg' / 'bin' / 'ffmpeg.exe',
        ]
        
        for path in common_paths:
            if Path(path).exists():
                status['installed'] = True
                status['path'] = str(path)
                print(f"✅ FFmpeg encontrado em: {path}")
                break
    
    return status

def add_to_path(ffmpeg_dir):
    """
    Adiciona diretório do FFmpeg ao PATH do sistema (Windows).
    
    Args:
        ffmpeg_dir (str): Diretório contendo o executável do FFmpeg
    """
    try:
        import winreg
        
        # Abrir chave do registro para variáveis de ambiente do usuário
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           'Environment', 0, winreg.KEY_ALL_ACCESS)
        
        try:
            # Obter PATH atual
            current_path, _ = winreg.QueryValueEx(key, 'PATH')
        except FileNotFoundError:
            current_path = ''
        
        # Verificar se já está no PATH
        if ffmpeg_dir.lower() not in current_path.lower():
            new_path = f"{current_path};{ffmpeg_dir}" if current_path else ffmpeg_dir
            winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"✅ {ffmpeg_dir} adicionado ao PATH")
            print("⚠️  Reinicie o terminal ou IDE para que as mudanças tenham efeito")
        else:
            print(f"✅ {ffmpeg_dir} já está no PATH")
        
        winreg.CloseKey(key)
        return True
        
    except Exception as e:
        print(f"❌ Erro ao modificar PATH: {e}")
        return False

def download_ffmpeg():
    """
    Instrui o usuário sobre como baixar e instalar FFmpeg.
    """
    print("\n🔽 Como instalar FFmpeg no Windows:")
    print("\n1. MÉTODO AUTOMÁTICO (Recomendado):")
    print("   - Instale Chocolatey: https://chocolatey.org/install")
    print("   - Execute: choco install ffmpeg")
    print("\n2. MÉTODO MANUAL:")
    print("   - Acesse: https://ffmpeg.org/download.html#build-windows")
    print("   - Baixe 'Windows builds by BtbN'")
    print("   - Extraia para C:\\ffmpeg")
    print("   - Adicione C:\\ffmpeg\\bin ao PATH do sistema")
    print("\n3. MÉTODO VIA SCOOP:")
    print("   - Instale Scoop: https://scoop.sh/")
    print("   - Execute: scoop install ffmpeg")

def create_django_helper():
    """
    Cria um helper para Django usar FFmpeg.
    """
    helper_code = '''
# ffmpeg_helper.py - Adicione ao seu app Django
import os
import shutil
import subprocess
from django.conf import settings

class FFmpegHelper:
    """Helper para trabalhar com FFmpeg no Django."""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_ffmpeg(self):
        """Encontra o executável do FFmpeg."""
        # Verificar se está configurado no settings
        if hasattr(settings, 'FFMPEG_PATH'):
            if os.path.exists(settings.FFMPEG_PATH):
                return settings.FFMPEG_PATH
        
        # Verificar PATH do sistema
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
        
        # Verificar locais comuns no Windows
        common_paths = [
            r'C:\\ffmpeg\\bin\\ffmpeg.exe',
            r'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe',
            r'C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe',
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def is_available(self):
        """Verifica se FFmpeg está disponível."""
        if not self.ffmpeg_path:
            return False
        
        try:
            subprocess.run([self.ffmpeg_path, '-version'], 
                         capture_output=True, check=True, timeout=5)
            return True
        except:
            return False
    
    def convert_audio(self, input_file, output_file, bitrate='320k'):
        """
        Converte arquivo de áudio usando FFmpeg.
        
        Args:
            input_file (str): Caminho do arquivo de entrada
            output_file (str): Caminho do arquivo de saída
            bitrate (str): Bitrate do áudio (padrão: 320k)
            
        Returns:
            bool: True se conversão foi bem-sucedida
        """
        if not self.is_available():
            raise Exception("FFmpeg não está disponível")
        
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', input_file,
                '-codec:a', 'libmp3lame',
                '-b:a', bitrate,
                '-y',  # Sobrescrever arquivo se existir
                output_file
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Erro na conversão: {e}")

# Como usar em suas views:
# ffmpeg = FFmpegHelper()
# if ffmpeg.is_available():
#     ffmpeg.convert_audio('input.wav', 'output.mp3')
'''
    
    with open('ffmpeg_helper.py', 'w', encoding='utf-8') as f:
        f.write(helper_code)
    
    print("✅ Arquivo 'ffmpeg_helper.py' criado!")
    print("   Adicione este helper ao seu projeto Django")

def main():
    """Função principal do diagnóstico."""
    print("🔍 DIAGNÓSTICO DO FFMPEG PARA DJANGO\n")
    print("=" * 50)
    
    # Verificar instalação
    status = check_ffmpeg_installation()
    
    if status['installed']:
        print(f"\n✅ FFmpeg está instalado!")
        print(f"📍 Localização: {status['path']}")
        if status['version']:
            print(f"📋 {status['version']}")
        
        # Testar execução
        print("\n🧪 Testando execução...")
        try:
            result = subprocess.run(['ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=1x1', 
                                   '-f', 'null', '-'], capture_output=True, timeout=10)
            if result.returncode == 0:
                print("✅ FFmpeg funcionando corretamente!")
            else:
                print("⚠️  FFmpeg executou mas retornou erro")
        except Exception as e:
            print(f"❌ Erro ao testar FFmpeg: {e}")
    
    else:
        print("\n❌ FFmpeg NÃO está instalado ou acessível")
        for error in status['errors']:
            print(f"   • {error}")
        
        download_ffmpeg()
        
        # Se encontrado em local não padrão, oferecer para adicionar ao PATH
        if status['path'] and sys.platform.startswith('win'):
            ffmpeg_dir = str(Path(status['path']).parent)
            response = input(f"\n❓ Adicionar {ffmpeg_dir} ao PATH? (s/n): ")
            if response.lower() in ['s', 'sim', 'y', 'yes']:
                add_to_path(ffmpeg_dir)
    
    # Criar helper Django
    print("\n" + "=" * 50)
    response = input("❓ Criar helper Django para FFmpeg? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        create_django_helper()
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Se FFmpeg não estiver instalado, siga as instruções acima")
    print("2. Reinicie seu terminal/IDE após instalar")
    print("3. Adicione o ffmpeg_helper.py ao seu projeto Django")
    print("4. Configure FFMPEG_PATH no settings.py se necessário")
    print("5. Teste novamente sua aplicação")

if __name__ == '__main__':
    main()