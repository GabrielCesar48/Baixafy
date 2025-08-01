#!/usr/bin/env python3
"""
BaixaFy Launcher - Executável Portátil Inteligente
Ativa venv, configura FFmpeg e executa interface automaticamente.

Estrutura esperada:
📂 BaixaFy_Portavel/
├── 📂 python/           # Python embeddable
├── 📂 ffmpeg-7.1.1/     # FFmpeg
├── 📂 venv_portable/    # Venv com dependências
├── 📄 BaixaFy_Launcher.py (este arquivo)
├── 📄 baixafy_interface.py (interface)
└── 📄 baixar_core.py (seu baixar.py adaptado)
"""

import os
import sys
import subprocess
from pathlib import Path
import time

# ===== CONFIGURAR TCL/TK ANTES DE QUALQUER IMPORT TKINTER =====
def configurar_tcl_tk():
    """Configura variáveis TCL/TK ANTES de importar tkinter."""
    base_dir = Path(__file__).parent.absolute()
    python_dir = base_dir / "python"
    
    # Definir variáveis de ambiente TCL/TK
    tcl_library = str(python_dir / "tcl" / "tcl8.6")
    tk_library = str(python_dir / "tcl" / "tk8.6")
    python_dlls = str(python_dir / "DLLs")
    
    os.environ["TCL_LIBRARY"] = tcl_library
    os.environ["TK_LIBRARY"] = tk_library
    
    # Adicionar DLLs ao PATH
    current_path = os.environ.get("PATH", "")
    if python_dlls not in current_path:
        os.environ["PATH"] = f"{python_dlls};{current_path}"
    
    print(f"🔧 TCL_LIBRARY: {tcl_library}")
    print(f"🔧 TK_LIBRARY: {tk_library}")
    print(f"🔧 Python DLLs: {python_dlls}")

# CONFIGURAR ANTES DE IMPORTAR TKINTER!
configurar_tcl_tk()

# Agora sim importar tkinter
import tkinter as tk
from tkinter import messagebox

class BaixaFyLauncher:
    """Launcher inteligente do BaixaFy."""
    
    def __init__(self):
        """Inicializa launcher."""
        self.base_dir = Path(__file__).parent.absolute()
        self.python_dir = self.base_dir / "python"
        self.ffmpeg_dir = self.base_dir / "ffmpeg-7.1.1"
        self.venv_dir = self.base_dir / "venv_portable"
        self.interface_script = self.base_dir / "baixafy_interface.py"
        
    def mostrar_splash(self):
        """Mostra splash screen de carregamento."""
        splash = tk.Tk()
        splash.title("BaixaFy")
        splash.geometry("400x300")
        splash.resizable(False, False)
        
        # Centralizar
        splash.update_idletasks()
        x = (splash.winfo_screenwidth() // 2) - (400 // 2)
        y = (splash.winfo_screenheight() // 2) - (300 // 2)
        splash.geometry(f"400x300+{x}+{y}")
        
        # Remover borda de janela
        splash.overrideredirect(True)
        
        # Frame principal
        frame = tk.Frame(splash, bg="#1DB954", relief="raised", bd=2)
        frame.pack(fill="both", expand=True)
        
        # Logo
        logo = tk.Label(
            frame, 
            text="🎵 BaixaFy", 
            font=("Arial", 24, "bold"),
            bg="#1DB954",
            fg="white"
        )
        logo.pack(pady=(50, 20))
        
        # Versão
        version = tk.Label(
            frame,
            text="Baixador de Músicas do Spotify",
            font=("Arial", 12),
            bg="#1DB954",
            fg="white"
        )
        version.pack(pady=(0, 30))
        
        # Loading
        self.loading_label = tk.Label(
            frame,
            text="🔄 Inicializando...",
            font=("Arial", 11),
            bg="#1DB954",
            fg="white"
        )
        self.loading_label.pack(pady=10)
        
        # Progress bar fake
        progress_frame = tk.Frame(frame, bg="#1DB954")
        progress_frame.pack(pady=20)
        
        self.progress_bar = tk.Frame(progress_frame, bg="#0d7c2d", height=6, width=0)
        self.progress_bar.pack()
        
        # Rodapé
        footer = tk.Label(
            frame,
            text="Versão Portátil • Python + SpotDL + FFmpeg",
            font=("Arial", 8),
            bg="#1DB954",
            fg="#cccccc"
        )
        footer.pack(side="bottom", pady=10)
        
        splash.update()
        return splash
    
    def atualizar_progresso(self, splash, texto: str, progresso: int):
        """Atualiza splash screen."""
        try:
            self.loading_label.config(text=texto)
            
            # Atualizar barra de progresso
            width = int((progresso / 100) * 300)
            self.progress_bar.config(width=width)
            
            splash.update()
            time.sleep(0.5)  # Dar tempo para ver
        except:
            pass  # Splash pode ter sido fechado
    
    def verificar_estrutura(self, splash) -> bool:
        """Verifica se estrutura está correta."""
        self.atualizar_progresso(splash, "🔍 Verificando arquivos...", 20)
        
        verificacoes = [
            (self.python_dir / "python.exe", "Python executável"),
            (self.python_dir / "tcl" / "tcl8.6" / "init.tcl", "TCL init.tcl (crítico!)"),
            (self.python_dir / "tcl" / "tk8.6" / "tk.tcl", "TK tk.tcl"),
            (self.python_dir / "DLLs", "Python DLLs"),
            (self.ffmpeg_dir / "bin" / "ffmpeg.exe", "FFmpeg executável"),
            (self.venv_dir / "Scripts" / "python.exe", "Venv Python"),
            (self.venv_dir / "Scripts" / "activate.bat", "Venv ativador"),
        ]
        
        for arquivo, nome in verificacoes:
            if not arquivo.exists():
                messagebox.showerror(
                    "Arquivo Faltando",
                    f"❌ {nome} não encontrado!\n\n"
                    f"Esperado em: {arquivo}\n\n"
                    f"Certifique-se que copiou as pastas tcl/ e DLLs/ do seu Python original."
                )
                return False
        
        return True
    
    def testar_dependencias(self, splash) -> bool:
        """Testa se dependências estão instaladas no venv."""
        self.atualizar_progresso(splash, "🔍 Verificando dependências...", 40)
        
        python_venv = self.venv_dir / "Scripts" / "python.exe"
        
        # Testar dependências diretamente no venv (que já tem acesso ao tkinter)
        dependencias = [
            ("customtkinter", "CustomTkinter"),
            ("spotdl", "SpotDL"),
            ("requests", "Requests")
        ]
        
        for modulo, nome in dependencias:
            try:
                result = subprocess.run([
                    str(python_venv), "-c", f"import {modulo}"
                ], capture_output=True, timeout=10)
                
                if result.returncode != 0:
                    messagebox.showerror(
                        "Dependência Faltando",
                        f"❌ {nome} não está instalado no venv!\n\n"
                        f"Execute no terminal:\n"
                        f"venv_portable\\Scripts\\activate\n"
                        f"pip install {modulo}"
                    )
                    return False
            except Exception as e:
                messagebox.showerror(
                    "Erro de Verificação",
                    f"❌ Erro ao verificar {nome}:\n{e}"
                )
                return False
        
        return True
    
    def configurar_ambiente(self, splash):
        """Configura ambiente (PATH, etc.)."""
        self.atualizar_progresso(splash, "⚙️ Configurando ambiente...", 60)
        
        # Adicionar FFmpeg ao PATH
        ffmpeg_bin = str(self.ffmpeg_dir / "bin")
        current_path = os.environ.get("PATH", "")
        
        if ffmpeg_bin not in current_path:
            os.environ["PATH"] = f"{ffmpeg_bin};{current_path}"
        
        # Definir variáveis do Python
        os.environ["PYTHONPATH"] = str(self.venv_dir / "Lib" / "site-packages")
        
    def verificar_interface_existe(self) -> bool:
        """Verifica se interface existe, senão cria uma básica."""
        if self.interface_script.exists():
            return True
        
        # Criar interface básica se não existir
        interface_code = '''#!/usr/bin/env python3
"""
BaixaFy Interface - Interface Gráfica Básica
Criada automaticamente pelo launcher.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import subprocess
import os
from pathlib import Path

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class BaixaFyApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🎵 BaixaFy - Baixador do Spotify")
        self.root.geometry("800x600")
        self.pasta_destino = str(Path.home() / "Music" / "BaixaFy")
        Path(self.pasta_destino).mkdir(parents=True, exist_ok=True)
        
        self.criar_interface()
    
    def criar_interface(self):
        # Header
        header = ctk.CTkFrame(self.root, height=80, fg_color="#1DB954")
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header, 
            text="🎵 BaixaFy - Baixador do Spotify", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title.pack(pady=25)
        
        # Main frame
        main = ctk.CTkFrame(self.root)
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # URL input
        ctk.CTkLabel(main, text="🔗 Cole o link do Spotify:", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20,10), anchor="w")
        
        self.url_entry = ctk.CTkEntry(
            main, 
            placeholder_text="https://open.spotify.com/track/...",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.url_entry.pack(fill="x", padx=0, pady=(0,20))
        
        # Pasta
        ctk.CTkLabel(main, text="📁 Pasta de destino:", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0,10), anchor="w")
        
        pasta_frame = ctk.CTkFrame(main, fg_color="transparent")
        pasta_frame.pack(fill="x", pady=(0,20))
        
        self.pasta_entry = ctk.CTkEntry(pasta_frame, height=40)
        self.pasta_entry.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.pasta_entry.insert(0, self.pasta_destino)
        
        ctk.CTkButton(
            pasta_frame, 
            text="Escolher", 
            width=100,
            command=self.escolher_pasta
        ).pack(side="right")
        
        # Botão download
        self.btn_download = ctk.CTkButton(
            main,
            text="⬇️ Baixar Música",
            height=50,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#1DB954",
            hover_color="#1ed760",
            command=self.baixar_musica
        )
        self.btn_download.pack(fill="x", pady=20)
        
        # Status
        self.status_label = ctk.CTkLabel(main, text="✅ Pronto para baixar!", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=10)
    
    def escolher_pasta(self):
        pasta = filedialog.askdirectory(initialdir=self.pasta_destino)
        if pasta:
            self.pasta_destino = pasta
            self.pasta_entry.delete(0, tk.END)
            self.pasta_entry.insert(0, pasta)
    
    def baixar_musica(self):
        url = self.url_entry.get().strip()
        pasta = self.pasta_entry.get().strip()
        
        if not url:
            messagebox.showwarning("URL vazia", "Cole um link do Spotify!")
            return
        
        if not url.startswith('https://open.spotify.com/'):
            messagebox.showerror("URL inválida", "Use apenas links do Spotify!")
            return
        
        self.btn_download.configure(state="disabled", text="⏳ Baixando...")
        self.status_label.configure(text="🔄 Baixando música...")
        
        thread = threading.Thread(target=self.download_thread, args=(url, pasta))
        thread.daemon = True
        thread.start()
    
    def download_thread(self, url, pasta):
        try:
            Path(pasta).mkdir(parents=True, exist_ok=True)
            
            cmd = [
                'spotdl',
                url,
                '--output', pasta,
                '--format', 'mp3',
                '--bitrate', '320k'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.root.after(0, self.download_sucesso, pasta)
            else:
                self.root.after(0, self.download_erro, result.stderr)
                
        except Exception as e:
            self.root.after(0, self.download_erro, str(e))
    
    def download_sucesso(self, pasta):
        self.btn_download.configure(state="normal", text="⬇️ Baixar Música")
        self.status_label.configure(text="✅ Download concluído!")
        messagebox.showinfo(
            "Sucesso!", 
            f"🎉 Música baixada com sucesso!\\n\\n📁 Pasta: {pasta}"
        )
    
    def download_erro(self, erro):
        self.btn_download.configure(state="normal", text="⬇️ Baixar Música")
        self.status_label.configure(text="❌ Erro no download")
        messagebox.showerror("Erro", f"❌ Erro ao baixar:\\n\\n{erro}")
    
    def executar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = BaixaFyApp()
    app.executar()
'''
        
        try:
            with open(self.interface_script, 'w', encoding='utf-8') as f:
                f.write(interface_code)
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar interface:\n{e}")
            return False
    
    def executar_interface(self, splash):
        """Executa interface principal."""
        self.atualizar_progresso(splash, "🚀 Iniciando BaixaFy...", 80)
        
        python_venv = self.venv_dir / "Scripts" / "python.exe"
        
        try:
            # Fechar splash
            splash.destroy()
            
            # Configurar variáveis de ambiente TCL/TK
            env = os.environ.copy()
            
            # Apontar para onde você copiou as pastas tcl
            tcl_library = str(self.python_dir / "tcl" / "tcl8.6")
            tk_library = str(self.python_dir / "tcl" / "tk8.6")
            
            env["TCL_LIBRARY"] = tcl_library
            env["TK_LIBRARY"] = tk_library
            
            # Adicionar DLLs ao PATH
            python_dlls = str(self.python_dir / "DLLs")
            if "PATH" in env:
                env["PATH"] = f"{python_dlls};{env['PATH']}"
            else:
                env["PATH"] = python_dlls
            
            print(f"🔧 TCL_LIBRARY: {tcl_library}")
            print(f"🔧 TK_LIBRARY: {tk_library}")
            
            # Executar interface com ambiente configurado
            subprocess.run([
                str(python_venv), 
                str(self.interface_script)
            ], cwd=str(self.base_dir), env=env)
            
        except Exception as e:
            messagebox.showerror(
                "Erro na Execução",
                f"❌ Erro ao executar interface:\n{e}\n\n"
                f"Comando: {python_venv} {self.interface_script}\n"
                f"TCL_LIBRARY: {env.get('TCL_LIBRARY', 'Não definido')}\n"
                f"TK_LIBRARY: {env.get('TK_LIBRARY', 'Não definido')}"
            )
    
    def executar(self):
        """Executa launcher completo."""
        splash = self.mostrar_splash()
        
        try:
            # Verificações
            if not self.verificar_estrutura(splash):
                splash.destroy()
                return False
            
            if not self.testar_dependencias(splash):
                splash.destroy()
                return False
            
            # Configurar ambiente
            self.configurar_ambiente(splash)
            
            # Verificar/criar interface
            self.atualizar_progresso(splash, "📱 Preparando interface...", 70)
            if not self.verificar_interface_existe():
                splash.destroy()
                return False
            
            # Executar
            self.executar_interface(splash)
            return True
            
        except Exception as e:
            splash.destroy()
            messagebox.showerror("Erro Fatal", f"❌ Erro no launcher:\n{e}")
            return False

def main():
    """Função principal."""
    try:
        launcher = BaixaFyLauncher()
        launcher.executar()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"❌ Erro fatal:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()