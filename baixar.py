#!/usr/bin/env python3
"""
Script simples para baixar playlists do Spotify via terminal.
Uso: python baixar_playlist.py
"""

import os
import subprocess
import sys
from pathlib import Path

def verificar_spotdl():
    """Verifica se spotdl está instalado."""
    try:
        result = subprocess.run(['spotdl', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ SpotDL instalado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("❌ SpotDL não instalado!")
        print("Execute: pip install spotdl")
        return False
    return False

def verificar_ffmpeg():
    """Verifica se FFmpeg está instalado."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg instalado")
            return True
    except FileNotFoundError:
        print("❌ FFmpeg não instalado!")
        print("Instale do chocolatey: choco install ffmpeg")
        return False
    return False

def baixar_playlist(url, pasta_destino="downloads"):
    """
    Baixa playlist do Spotify.
    
    Args:
        url (str): URL da playlist/música do Spotify
        pasta_destino (str): Pasta onde salvar os arquivos
    """
    # Criar pasta se não existir
    Path(pasta_destino).mkdir(exist_ok=True)
    
    print(f"\n🎵 Baixando: {url}")
    print(f"📁 Pasta: {pasta_destino}")
    
    # Comando spotdl simples
    cmd = [
        'spotdl',
        url,
        '--output', pasta_destino,
        '--format', 'mp3',
        '--bitrate', '320k'
    ]
    
    try:
        # Executar download
        print("\n⏳ Iniciando download...")
        result = subprocess.run(cmd, text=True)
        
        if result.returncode == 0:
            print("✅ Download concluído!")
            print(f"📁 Arquivos salvos em: {os.path.abspath(pasta_destino)}")
        else:
            print("❌ Erro no download")
            
    except KeyboardInterrupt:
        print("\n⚠️ Download cancelado pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal."""
    print("🎵 BAIXADOR SIMPLES DE PLAYLIST SPOTIFY")
    print("=" * 45)
    
    # Verificar dependências
    if not verificar_spotdl():
        return
    
    if not verificar_ffmpeg():
        return
    
    print("\n✅ Tudo pronto para download!")
    
    # Loop principal
    while True:
        print("\n" + "-" * 45)
        print("Cole a URL da música/playlist do Spotify:")
        print("(ou digite 'sair' para encerrar)")
        
        url = input("🔗 URL: ").strip()
        
        if url.lower() in ['sair', 'exit', 'quit', '']:
            print("👋 Tchau!")
            break
        
        # Verificar se é URL válida do Spotify
        if not url.startswith('https://open.spotify.com/'):
            print("❌ URL inválida! Use URLs do Spotify.")
            continue
        
        # Perguntar pasta (opcional)
        pasta = input("📁 Pasta (Enter = 'downloads'): ").strip()
        if not pasta:
            pasta = "downloads"
        
        # Fazer download
        baixar_playlist(url, pasta)
        
        # Perguntar se quer continuar
        continuar = input("\n❓ Baixar outra? (s/n): ").strip().lower()
        if continuar not in ['s', 'sim', 'y', 'yes']:
            print("👋 Tchau!")
            break

if __name__ == '__main__':
    main()