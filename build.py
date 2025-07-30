"""
Build Script Simplificado para BaixaFy Desktop
Gera executável único com PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def log(message):
    print(f"[BUILD] {message}")


def run_command(command, cwd=None):
    """Executa comando e retorna sucesso"""
    log(f"Executando: {command}")
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        log(f"ERRO: {e}")
        return False


def clean_build():
    """Limpa builds anteriores"""
    log("Limpando builds anteriores...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for d in dirs_to_clean:
        if Path(d).exists():
            shutil.rmtree(d)
            log(f"Removido: {d}")
    
    # Limpar .pyc
    for pyc in Path('.').rglob('*.pyc'):
        pyc.unlink()


def check_dependencies():
    """Verifica dependências"""
    log("Verificando dependências...")
    
    try:
        import django
        log(f"✓ Django {django.get_version()}")
    except ImportError:
        log("✗ Django não encontrado. Instale: pip install django")
        return False
    
    try:
        import spotdl
        log("✓ SpotDL encontrado")
    except ImportError:
        log("✗ SpotDL não encontrado. Instale: pip install spotdl")
        return False
    
    # Verificar PyInstaller
    if not run_command("pyinstaller --version"):
        log("✗ PyInstaller não encontrado. Instale: pip install pyinstaller")
        return False
    
    log("✓ Todas dependências OK")
    return True


def prepare_django():
    """Prepara Django"""
    log("Preparando Django...")
    
    django_dir = Path('django_app')
    if not django_dir.exists():
        log("✗ Pasta django_app não encontrada!")
        return False
    
    # Executar collectstatic
    if not run_command('python manage.py collectstatic --noinput', cwd=django_dir):
        log("✗ Erro no collectstatic")
        return False
    
    log("✓ Django preparado")
    return True


def create_spec_file():
    """Cria arquivo .spec do PyInstaller"""
    log("Criando arquivo spec...")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('django_app', 'django_app'),
    ],
    hiddenimports=[
        'django',
        'django.contrib.admin',
        'django.contrib.auth', 
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'spotdl',
        'yt_dlp',
        'mutagen',
        'cryptography',
        'tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BaixaFy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open('BaixaFy.spec', 'w') as f:
        f.write(spec_content)
    
    log("✓ Arquivo spec criado")
    return True


def build_executable():
    """Cria executável"""
    log("Criando executável...")
    
    if not run_command("pyinstaller --clean --noconfirm BaixaFy.spec"):
        log("✗ Erro ao criar executável")
        return False
    
    exe_path = Path('dist/BaixaFy.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        log(f"✓ Executável criado: {exe_path} ({size_mb:.1f} MB)")
        return True
    else:
        log("✗ Executável não encontrado")
        return False


def main():
    log("=== BUILD BAIXAFY DESKTOP ===")
    
    steps = [
        ("Verificar dependências", check_dependencies),
        ("Limpar builds anteriores", clean_build),
        ("Preparar Django", prepare_django),
        ("Criar arquivo spec", create_spec_file),
        ("Criar executável", build_executable),
    ]
    
    for step_name, step_func in steps:
        log(f"--- {step_name} ---")
        if not step_func():
            log(f"✗ FALHA: {step_name}")
            return False
        log(f"✓ OK: {step_name}")
    
    log("=== BUILD CONCLUÍDO COM SUCESSO! ===")
    log(f"Executável: {Path('dist/BaixaFy.exe').absolute()}")
    return True


if __name__ == "__main__":
    if main():
        print("\n🎉 Build concluído! Teste o executável em dist/BaixaFy.exe")
        sys.exit(0)
    else:
        print("\n❌ Build falhou!")
        sys.exit(1)