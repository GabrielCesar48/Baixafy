#!/usr/bin/env python3
"""
Script de diagnóstico para verificar se o SpotDL está funcionando corretamente.
Execute este script na raiz do projeto para diagnosticar problemas.

Usage:
    python diagnose_spotdl.py
"""

import sys
import os
import subprocess
import json
from pathlib import Path


def print_header(text):
    """Imprime cabeçalho formatado."""
    print("\n" + "="*60)
    print(f"🔍 {text}")
    print("="*60)


def print_success(text):
    """Imprime mensagem de sucesso."""
    print(f"✅ {text}")


def print_warning(text):
    """Imprime mensagem de aviso."""
    print(f"⚠️ {text}")


def print_error(text):
    """Imprime mensagem de erro."""
    print(f"❌ {text}")


def check_python_version():
    """Verifica a versão do Python."""
    print_header("VERIFICANDO PYTHON")
    
    version = sys.version_info
    print(f"Versão do Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print_success("Versão do Python adequada")
        return True
    else:
        print_error("Python 3.8+ é necessário")
        return False


def check_spotdl_installation():
    """Verifica se SpotDL está instalado."""
    print_header("VERIFICANDO INSTALAÇÃO DO SPOTDL")
    
    try:
        # Verificar se está instalado
        result = subprocess.run(
            [sys.executable, '-c', 'import spotdl; print(spotdl.__version__)'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"SpotDL instalado: versão {version}")
            return True
        else:
            print_error("SpotDL não está instalado")
            print("Execute: pip install spotdl")
            return False
            
    except Exception as e:
        print_error(f"Erro ao verificar SpotDL: {e}")
        return False


def check_spotdl_command():
    """Verifica se o comando spotdl funciona."""
    print_header("VERIFICANDO COMANDO SPOTDL")
    
    try:
        result = subprocess.run(
            ['spotdl', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"Comando spotdl funcionando: {version}")
            return True
        else:
            print_error("Comando spotdl não está funcionando")
            return False
            
    except FileNotFoundError:
        print_error("Comando spotdl não encontrado no PATH")
        return False
    except Exception as e:
        print_error(f"Erro ao executar spotdl: {e}")
        return False


def check_ffmpeg():
    """Verifica se FFmpeg está instalado."""
    print_header("VERIFICANDO FFMPEG")
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Extrair versão
            lines = result.stdout.split('\n')
            version_line = lines[0] if lines else "Versão desconhecida"
            print_success(f"FFmpeg instalado: {version_line}")
            return True
        else:
            print_error("FFmpeg não está funcionando")
            return False
            
    except FileNotFoundError:
        print_error("FFmpeg não está instalado")
        print("Instale o FFmpeg:")
        print("- Windows: https://ffmpeg.org/download.html")
        print("- Ubuntu/Debian: sudo apt install ffmpeg")
        print("- macOS: brew install ffmpeg")
        return False
    except Exception as e:
        print_error(f"Erro ao verificar FFmpeg: {e}")
        return False


def check_config_file():
    """Verifica o arquivo de configuração do SpotDL."""
    print_header("VERIFICANDO CONFIGURAÇÃO DO SPOTDL")
    
    config_dir = Path.home() / '.spotdl'
    config_file = config_dir / 'config.json'
    
    if config_file.exists():
        print_success(f"Arquivo de configuração encontrado: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Verificar configurações importantes
            important_settings = ['output', 'format', 'bitrate']
            for setting in important_settings:
                value = config.get(setting, 'NÃO DEFINIDO')
                print(f"  {setting}: {value}")
            
            return True
            
        except Exception as e:
            print_error(f"Erro ao ler configuração: {e}")
            return False
    else:
        print_warning("Arquivo de configuração não encontrado")
        print("Execute: spotdl --generate-config")
        return False


def test_spotdl_import():
    """Testa a importação do SpotDL."""
    print_header("TESTANDO IMPORTAÇÃO DO SPOTDL")
    
    try:
        # Teste de importação
        from spotdl import Spotdl
        from spotdl.utils.config import get_config
        print_success("Importações do SpotDL funcionando")
        
        # Teste de inicialização simples
        try:
            spotdl_instance = Spotdl()
            print_success("Inicialização básica do SpotDL funcionando")
            return True
        except Exception as init_error:
            print_error(f"Erro na inicialização: {init_error}")
            return False
            
    except ImportError as e:
        print_error(f"Erro na importação: {e}")
        return False


def check_environment_variables():
    """Verifica variáveis de ambiente do Spotify."""
    print_header("VERIFICANDO CREDENCIAIS DO SPOTIFY")
    
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if client_id and client_secret:
        print_success("Credenciais do Spotify configuradas")
        print(f"  Client ID: {client_id[:10]}...")
        return True
    else:
        print_warning("Credenciais do Spotify não configuradas")
        print("Para melhor performance, configure:")
        print("  SPOTIFY_CLIENT_ID=seu_client_id")
        print("  SPOTIFY_CLIENT_SECRET=seu_client_secret")
        print("Obtenha em: https://developer.spotify.com/")
        return False


def main():
    """Função principal do diagnóstico."""
    print("🎵 DIAGNÓSTICO DO SPOTDL PARA BAIXAFY")
    print("Este script verificará se tudo está funcionando corretamente")
    
    checks = [
        ("Python", check_python_version),
        ("SpotDL Instalação", check_spotdl_installation),
        ("SpotDL Comando", check_spotdl_command),
        ("FFmpeg", check_ffmpeg),
        ("Configuração", check_config_file),
        ("Importação", test_spotdl_import),
        ("Credenciais", check_environment_variables),
    ]
    
    results = []
    
    # Executar todos os testes
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Erro inesperado em {name}: {e}")
            results.append((name, False))
    
    # Resumo final
    print_header("RESUMO DO DIAGNÓSTICO")
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}: OK")
            passed += 1
        else:
            print_error(f"{name}: FALHOU")
    
    print(f"\n📊 Resultado: {passed}/{total} verificações passaram")
    
    if passed == total:
        print_success("🎉 Tudo está funcionando! SpotDL pronto para uso no BaixaFy")
    elif passed >= total - 1:
        print_warning("⚠️ Quase tudo funcionando - verifique os itens que falharam")
    else:
        print_error("❌ Vários problemas detectados - corrija antes de usar")
    
    print("\n💡 Após corrigir os problemas, execute:")
    print("   python manage.py test_spotdl")


if __name__ == "__main__":
    main()