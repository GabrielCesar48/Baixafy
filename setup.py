#!/usr/bin/env python3
"""
Setup script para instalar e configurar o BaixaFy.
Este script instala todas as dependências necessárias.
"""

import subprocess
import sys
import os
from pathlib import Path

def instalar_dependencias():
    """Instala todas as dependências necessárias."""
    print("🔧 Instalando dependências do BaixaFy...")
    
    dependencias = [
        'customtkinter>=5.2.1',
        'spotdl>=4.2.5', 
        'pillow>=10.0.0',
        'pyinstaller>=6.2.0'
    ]
    
    for dep in dependencias:
        print(f"📦 Instalando {dep}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✅ {dep} instalado com sucesso!")
        except subprocess.CalledProcessError:
            print(f"❌ Erro ao instalar {dep}")
            return False
    
    return True

def verificar_spotdl():
    """Verifica se spotDL foi instalado corretamente."""
    print("\n🔍 Verificando spotDL...")
    try:
        result = subprocess.run(['spotdl', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ SpotDL disponível: {result.stdout.strip()}")
            return True
        else:
            print("❌ SpotDL não está funcionando corretamente")
            return False
    except FileNotFoundError:
        print("❌ SpotDL não encontrado no PATH")
        print("💡 Tente reinstalar com: pip install spotdl")
        return False

def criar_executavel():
    """Cria o arquivo executável usando PyInstaller."""
    print("\n🚀 Criando executável...")
    
    # Verificar se arquivo principal existe
    arquivo_principal = None
    for nome in ['baixafy.py', 'baixar.py']:
        if Path(nome).exists():
            arquivo_principal = nome
            break
    
    if not arquivo_principal:
        print("❌ Arquivo principal não encontrado! (baixafy.py ou baixar.py)")
        return False
    
    print(f"📝 Usando arquivo: {arquivo_principal}")
    
    # Comando básico do PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',           # Arquivo único
        '--windowed',          # Sem console
        '--name', 'BaixaFy',   # Nome do executável
        arquivo_principal      # Arquivo principal
    ]
    
    # Adicionar ícone se existir
    if Path('baixafy_icon.ico').exists():
        cmd.extend(['--icon', 'baixafy_icon.ico'])
        print("🎨 Ícone encontrado, será incluído no executável")
    
    try:
        subprocess.check_call(cmd)
        print("✅ Executável criado com sucesso!")
        
        # Mover executável para pasta atual
        exe_path = Path('dist') / 'BaixaFy.exe'
        if exe_path.exists():
            # Obter tamanho antes de mover
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            
            # Remover arquivo existente se houver
            exe_destino = Path('BaixaFy.exe')
            if exe_destino.exists():
                exe_destino.unlink()
                print("🗑️ Removido executável antigo")
            
            # Mover arquivo
            exe_path.rename('BaixaFy.exe')
            print(f"📁 Executável atualizado: {Path.cwd() / 'BaixaFy.exe'}")
            print(f"📊 Tamanho do executável: {size_mb:.1f} MB")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar executável: {e}")
        return False

def limpar_arquivos_temp():
    """Remove arquivos temporários criados pelo PyInstaller."""
    print("\n🧹 Limpando arquivos temporários...")
    
    import shutil
    
    for pasta in ['build', 'dist', '__pycache__']:
        pasta_path = Path(pasta)
        if pasta_path.exists():
            shutil.rmtree(pasta_path)
            print(f"🗑️ Removido: {pasta}")
    
    # Remover arquivo .spec
    spec_file = Path('BaixaFy.spec')
    if spec_file.exists():
        spec_file.unlink()
        print("🗑️ Removido: BaixaFy.spec")

def criar_arquivo_instrucoes():
    """Cria arquivo com instruções de uso."""
    print("\n📝 Criando arquivo de instruções...")
    
    instrucoes = '''🎵 BAIXAFY - INSTRUÇÕES DE USO
=====================================

🚀 COMO USAR O BAIXAFY:

1. PRIMEIRA VEZ:
   - Execute BaixaFy.exe
   - Se aparecer erro "SpotDL não encontrado":
     • Clique "Sim" para instalar automaticamente
     • OU instale manualmente (veja instruções abaixo)

2. BAIXAR MÚSICAS:
   - Cole o link do Spotify (música ou playlist)
   - Clique "Pesquisar Músicas"
   - Selecione as músicas desejadas
   - Escolha a pasta de destino
   - Clique "Baixar Músicas Selecionadas"

🔧 INSTALAÇÃO MANUAL DO SPOTDL:

Se a instalação automática não funcionar:

1. Abra o Prompt de Comando como ADMINISTRADOR:
   - Pressione Windows + R
   - Digite: cmd
   - Pressione Ctrl + Shift + Enter

2. Execute o comando:
   pip install spotdl

3. Se der erro "pip não reconhecido":
   - Instale Python em: https://python.org
   - Marque "Add to PATH" durante instalação
   - Reinicie o computador
   - Tente novamente o passo 2

4. Teste se funcionou:
   spotdl --version

5. Reinicie o BaixaFy.exe

⚠️ PROBLEMAS COMUNS:

❌ "SpotDL não encontrado"
✅ Instale SpotDL (veja instruções acima)

❌ "Erro ao buscar playlist"
✅ Verifique se o link do Spotify está correto
✅ Teste sua conexão com internet

❌ "Erro no download"
✅ Algumas músicas podem não estar disponíveis
✅ Tente baixar uma música por vez
✅ Verifique se a pasta tem permissão de escrita

🎉 DIVIRTA-SE BAIXANDO SUAS MÚSICAS FAVORITAS!

=====================================
BaixaFy v1.0 - Powered by SpotDL'''
    
    try:
        with open('LEIA-ME - Instruções de Uso.txt', 'w', encoding='utf-8') as f:
            f.write(instrucoes)
        print("✅ Arquivo de instruções criado: LEIA-ME - Instruções de Uso.txt")
    except Exception as e:
        print(f"⚠️ Erro ao criar arquivo de instruções: {e}")

def main():
    """Função principal do setup."""
    print("=" * 50)
    print("   🎵 BAIXAFY - SETUP E INSTALAÇÃO")
    print("=" * 50)
    print()
    
    # Verificar Python
    print(f"🐍 Python {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é obrigatório!")
        sys.exit(1)
    
    # Passo 1: Instalar dependências
    if not instalar_dependencias():
        print("\n❌ Falha na instalação das dependências!")
        sys.exit(1)
    
    # Passo 2: Verificar spotDL
    if not verificar_spotdl():
        print("\n⚠️ SpotDL não está funcionando, mas continuando...")
    
    # Passo 3: Criar executável
    if not criar_executavel():
        print("\n❌ Falha ao criar executável!")
        sys.exit(1)
    
    # Passo 4: Limpeza e instruções
    limpar_arquivos_temp()
    criar_arquivo_instrucoes()
    
    # Sucesso!
    print("\n" + "=" * 50)
    print("   🎉 SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print()
    print("✅ Executável criado: BaixaFy.exe")
    print("✅ Dependências instaladas")
    print("✅ Instruções criadas: LEIA-ME - Instruções de Uso.txt")
    print()
    print("📋 COMO USAR:")
    print("1. Execute BaixaFy.exe")
    print("2. Se der erro SpotDL, clique 'Sim' para instalar")
    print("3. Cole o link do Spotify")
    print("4. Clique em 'Pesquisar Músicas'")
    print("5. Selecione as músicas desejadas")
    print("6. Clique em 'Baixar Músicas Selecionadas'")
    print()
    print("⚠️ IMPORTANTE:")
    print("- Leia o arquivo 'LEIA-ME - Instruções de Uso.txt'")
    print("- Se der problema, o app tentará instalar SpotDL automaticamente")
    print("- Para distribuir: copie apenas o BaixaFy.exe")
    print()
    print("🚀 Divirta-se baixando suas músicas favoritas!")

if __name__ == "__main__":
    main()