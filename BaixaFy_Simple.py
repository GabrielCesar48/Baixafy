#!/usr/bin/env python3
"""
BaixaFy Launcher Simples - Sem GUI de splash
Ativa venv, configura ambiente e executa interface.
"""

import os
import sys
import subprocess
from pathlib import Path

def obter_diretorio_base():
    """Obtém diretório correto tanto para .py quanto para .exe"""
    if getattr(sys, 'frozen', False):
        # Executando como .exe empacotado
        # Usar diretório onde o .exe está localizado
        return Path(sys.executable).parent.absolute()
    else:
        # Executando como .py
        return Path(__file__).parent.absolute()

def verificar_estrutura():
    """Verifica se todos arquivos necessários existem."""
    base_dir = obter_diretorio_base()
    
    arquivos_necessarios = [
        ("venv_portable/Scripts/python.exe", "Venv Python"),
        ("baixafy_interface.py", "Interface BaixaFy"),
        ("ffmpeg-7.1.1/bin/ffmpeg.exe", "FFmpeg executável"),
    ]
    
    print("🔍 Verificando arquivos...")
    print(f"📁 Diretório base: {base_dir}")
    print()
    
    for arquivo, nome in arquivos_necessarios:
        caminho = base_dir / arquivo
        if not caminho.exists():
            print(f"❌ {nome} não encontrado: {caminho}")
            return False
        else:
            print(f"✅ {nome}: OK")
    
    return True

def configurar_ambiente():
    """Configura variáveis de ambiente."""
    base_dir = obter_diretorio_base()
    
    print("🔧 Configurando ambiente...")
    
    # Adicionar FFmpeg ao PATH
    ffmpeg_bin = str(base_dir / "ffmpeg-7.1.1" / "bin")
    current_path = os.environ.get("PATH", "")
    if ffmpeg_bin not in current_path:
        os.environ["PATH"] = f"{ffmpeg_bin};{current_path}"
        print(f"   ✅ FFmpeg adicionado ao PATH")
    
    # Definir TCL/TK (caso necessário)
    python_dir = base_dir / "python"
    if python_dir.exists():
        os.environ["TCL_LIBRARY"] = str(python_dir / "tcl" / "tcl8.6")
        os.environ["TK_LIBRARY"] = str(python_dir / "tcl" / "tk8.6")
        print(f"   ✅ Variáveis TCL/TK definidas")

def executar_interface():
    """Executa a interface BaixaFy."""
    base_dir = obter_diretorio_base()
    python_venv = base_dir / "venv_portable" / "Scripts" / "python.exe"
    interface_script = base_dir / "baixafy_interface.py"
    
    print("🚀 Iniciando BaixaFy...")
    print()
    
    try:
        # Executar interface com venv
        process = subprocess.run([
            str(python_venv),
            str(interface_script)
        ], cwd=str(base_dir))
        
        if process.returncode == 0:
            print("✅ BaixaFy encerrado normalmente")
        else:
            print(f"⚠️ BaixaFy encerrado com código: {process.returncode}")
            
    except KeyboardInterrupt:
        print("\n⏹️ BaixaFy cancelado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar BaixaFy: {e}")
        return False
    
    return True

def main():
    """Função principal."""
    print("=" * 50)
    print("        🎵 BaixaFy - Baixador do Spotify 🎵")
    print("=" * 50)
    print()
    
    try:
        # Verificar estrutura
        if not verificar_estrutura():
            print("\n❌ Estrutura de arquivos incompleta!")
            input("Pressione Enter para sair...")
            return False
        
        # Configurar ambiente
        configurar_ambiente()
        
        # Executar interface
        if not executar_interface():
            input("Pressione Enter para sair...")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        input("Pressione Enter para sair...")
        return False

if __name__ == "__main__":
    main()