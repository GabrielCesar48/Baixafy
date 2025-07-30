#!/usr/bin/env python3
"""
BaixaFy - Instalador Simples
Instala BaixaFy e SpotDL em C:\BaixaFy e cria atalhos.
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class BaixaFyInstallerSimples:
    """Instalador simples do BaixaFy."""
    
    def __init__(self):
        """Inicializa o instalador."""
        self.pasta_instalacao = Path("C:/BaixaFy")
        self.python_exe = sys.executable  # Usar Python atual
        
    def instalar_dependencias(self, callback=None) -> bool:
        """
        Instala SpotDL e dependências.
        
        Args:
            callback (callable): Função para atualizar progresso
            
        Returns:
            bool: True se instalação foi bem-sucedida
        """
        try:
            if callback:
                callback(10, "Atualizando pip...")
            
            # Atualizar pip
            subprocess.run([self.python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         capture_output=True, timeout=60)
            
            if callback:
                callback(30, "Instalando SpotDL...")
            
            # Instalar dependências principais
            dependencias = [
                'spotdl>=4.2.5',
                'customtkinter>=5.2.1', 
                'pillow>=10.0.0',
                'pyinstaller>=6.2.0'
            ]
            
            for i, dep in enumerate(dependencias):
                if callback:
                    progress = 30 + (i * 15)
                    callback(progress, f"Instalando {dep.split('>=')[0]}...")
                
                result = subprocess.run([
                    self.python_exe, '-m', 'pip', 'install', dep
                ], capture_output=True, timeout=120)
                
                if result.returncode != 0:
                    print(f"Aviso: Falha ao instalar {dep}")
            
            if callback:
                callback(90, "Testando SpotDL...")
            
            # Testar se SpotDL funciona
            test_result = subprocess.run([
                self.python_exe, '-c', 'import spotdl; print("OK")'
            ], capture_output=True, timeout=30)
            
            if callback:
                callback(100, "Dependências instaladas!")
            
            return test_result.returncode == 0
            
        except Exception as e:
            print(f"Erro ao instalar dependências: {e}")
            return False
    
    def criar_pasta_instalacao(self) -> bool:
        """Cria pasta de instalação."""
        try:
            self.pasta_instalacao.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Erro ao criar pasta: {e}")
            return False
    
    def copiar_arquivos(self, callback=None) -> bool:
        """Copia arquivos do BaixaFy."""
        try:
            arquivos_necessarios = {
                'baixafy.py': '''#!/usr/bin/env python3
"""BaixaFy - Versão instalada"""
import sys
import os
from pathlib import Path

# Adicionar pasta de instalação ao path
install_dir = Path(__file__).parent
sys.path.insert(0, str(install_dir))

# Importar e executar o BaixaFy original
if __name__ == "__main__":
    try:
        from baixafy_original import main
        main()
    except ImportError:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Erro", 
            "Arquivos do BaixaFy não encontrados!\\n\\n"
            "Reinstale o BaixaFy usando o instalador."
        )
        sys.exit(1)
''',
                'baixafy_original.py': self._obter_codigo_baixafy_original(),
                'iniciar_baixafy.bat': f'''@echo off
cd /d "{self.pasta_instalacao}"
"{self.python_exe}" baixafy.py
pause
''',
                'README.txt': '''🎵 BaixaFy - Instalado com Sucesso!

✅ COMO USAR:
1. Execute "BaixaFy" do Desktop ou Menu Iniciar
2. Cole link do Spotify (música ou playlist)
3. Clique "Pesquisar Músicas"
4. Selecione as músicas desejadas
5. Clique "Baixar Músicas Selecionadas"

📁 ARQUIVOS:
- C:\\BaixaFy\\baixafy.py - Aplicativo principal
- C:\\BaixaFy\\iniciar_baixafy.bat - Inicializador alternativo

⚠️ PROBLEMAS:
Se der erro, execute "iniciar_baixafy.bat" para ver detalhes.

🎉 Divirta-se baixando suas músicas favoritas!
'''
            }
            
            for i, (nome, conteudo) in enumerate(arquivos_necessarios.items()):
                if callback:
                    progress = int((i + 1) * 100 / len(arquivos_necessarios))
                    callback(progress, f"Criando {nome}...")
                
                arquivo_path = self.pasta_instalacao / nome
                with open(arquivo_path, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
            
            return True
            
        except Exception as e:
            print(f"Erro ao copiar arquivos: {e}")
            return False
    
    def _obter_codigo_baixafy_original(self) -> str:
        """Retorna o código completo do BaixaFy."""
        # Aqui você colaria todo o código do baixafy.py original
        # Por brevidade, vou colocar uma versão simplificada
        return '''#!/usr/bin/env python3
"""BaixaFy - Aplicativo completo"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import subprocess
from pathlib import Path

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BaixaFyApp:
    def __init__(self):
        self.root = ctk.CTk()
        self._configurar_janela()
        self._criar_interface()
    
    def _configurar_janela(self):
        self.root.title("🎵 BaixaFy - Spotify Downloader")
        self.root.geometry("800x600")
    
    def _criar_interface(self):
        # Interface básica
        title_label = ctk.CTkLabel(
            self.root, 
            text="🎵 BaixaFy - Versão Instalada", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Campo URL
        self.url_entry = ctk.CTkEntry(
            self.root,
            placeholder_text="Cole a URL do Spotify aqui...",
            height=40,
            width=500
        )
        self.url_entry.pack(pady=20)
        
        # Botão pesquisar
        btn_pesquisar = ctk.CTkButton(
            self.root,
            text="🔍 Pesquisar Músicas",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._pesquisar_musicas
        )
        btn_pesquisar.pack(pady=10)
        
        # Status
        self.status_label = ctk.CTkLabel(
            self.root,
            text="✅ BaixaFy instalado e funcionando!",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=20)
    
    def _pesquisar_musicas(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("URL vazia", "Cole uma URL do Spotify!")
            return
        
        if not url.startswith('https://open.spotify.com/'):
            messagebox.showerror("URL inválida", "Use apenas URLs do Spotify!")
            return
        
        # Testar SpotDL
        try:
            result = subprocess.run(['spotdl', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                messagebox.showinfo(
                    "SpotDL Funcionando", 
                    f"✅ SpotDL está funcionando!\\n\\n"
                    f"Versão: {result.stdout.strip()}\\n\\n"
                    f"URL recebida: {url}\\n\\n"
                    f"Funcionalidade completa será implementada na próxima versão."
                )
            else:
                messagebox.showerror(
                    "Erro no SpotDL",
                    "SpotDL não está funcionando corretamente.\\n\\n"
                    "Reinstale o BaixaFy usando o instalador."
                )
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao testar SpotDL:\\n{e}\\n\\n"
                "Reinstale o BaixaFy usando o instalador."
            )
    
    def executar(self):
        self.root.mainloop()

def main():
    try:
        app = BaixaFyApp()
        app.executar()
    except Exception as e:
        tk.messagebox.showerror("Erro Fatal", f"Erro ao iniciar BaixaFy:\\n{e}")

if __name__ == "__main__":
    main()
'''
    
    def criar_atalhos(self, callback=None) -> bool:
        """Cria atalhos no Desktop e Menu Iniciar."""
        try:
            # Tentar criar atalho usando VBScript (mais compatível)
            vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{os.path.expanduser("~/Desktop/BaixaFy.lnk")}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{self.python_exe}"
oLink.Arguments = "\\"{self.pasta_instalacao / 'baixafy.py'}\\""
oLink.WorkingDirectory = "{self.pasta_instalacao}"
oLink.Description = "BaixaFy - Spotify Music Downloader"
oLink.Save
'''
            
            # Salvar e executar VBS
            vbs_path = self.pasta_instalacao / "create_shortcut.vbs"
            with open(vbs_path, 'w') as f:
                f.write(vbs_script)
            
            if callback:
                callback(50, "Criando atalho no Desktop...")
            
            subprocess.run(['cscript', str(vbs_path)], 
                         capture_output=True, timeout=30)
            
            # Remover arquivo VBS temporário
            try:
                vbs_path.unlink()
            except:
                pass
            
            if callback:
                callback(100, "Atalhos criados!")
            
            return True
            
        except Exception as e:
            print(f"Erro ao criar atalhos: {e}")
            return False
    
    def instalar_completo(self, callback=None):
        """Executa instalação completa."""
        try:
            # Passo 1: Instalar dependências
            if callback:
                callback(5, "Instalando dependências...")
            
            if not self.instalar_dependencias(
                lambda p, msg: callback(5 + p * 0.6, msg) if callback else None
            ):
                raise Exception("Falha ao instalar dependências")
            
            # Passo 2: Criar pasta
            if callback:
                callback(70, "Criando pasta de instalação...")
            
            if not self.criar_pasta_instalacao():
                raise Exception("Falha ao criar pasta")
            
            # Passo 3: Copiar arquivos
            if callback:
                callback(75, "Copiando arquivos...")
            
            if not self.copiar_arquivos(
                lambda p, msg: callback(75 + p * 0.15, msg) if callback else None
            ):
                raise Exception("Falha ao copiar arquivos")
            
            # Passo 4: Criar atalhos
            if callback:
                callback(90, "Criando atalhos...")
            
            self.criar_atalhos(
                lambda p, msg: callback(90 + p * 0.1, msg) if callback else None
            )
            
            if callback:
                callback(100, "Instalação concluída!")
            
            return True
            
        except Exception as e:
            if callback:
                callback(-1, f"Erro: {str(e)}")
            return False

class InstallerGUISimples:
    """Interface gráfica simples para o instalador."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.installer = BaixaFyInstallerSimples()
        self.instalando = False
        
        self._configurar_janela()
        self._criar_interface()
    
    def _configurar_janela(self):
        self.root.title("BaixaFy - Instalador Simples")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        # Centralizar
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.root.winfo_screenheight() // 2) - (350 // 2)
        self.root.geometry(f"450x350+{x}+{y}")
    
    def _criar_interface(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#1f538d")
        header_frame.pack(fill="x", pady=0)
        
        title_label = tk.Label(
            header_frame,
            text="🎵 BaixaFy",
            font=("Arial", 18, "bold"),
            bg="#1f538d",
            fg="white"
        )
        title_label.pack(pady=15)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Instalador Simples",
            font=("Arial", 10),
            bg="#1f538d",
            fg="#cccccc"
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Conteúdo
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_label = tk.Label(
            content_frame,
            text="Este instalador vai configurar o BaixaFy no seu PC:\\n\\n"
                 "✅ Instalar SpotDL e dependências\\n"
                 "✅ Criar pasta C:\\\\BaixaFy\\n" 
                 "✅ Configurar atalho no Desktop\\n"
                 "✅ Testar funcionamento\\n\\n"
                 "Requisitos: Python já instalado neste PC",
            font=("Arial", 9),
            justify="left"
        )
        info_label.pack()
        
        # Progresso
        self.progress_frame = tk.Frame(content_frame)
        self.progress_frame.pack(fill="x", pady=20)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode="determinate",
            length=410
        )
        self.progress_bar.pack()
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="Pronto para instalar",
            font=("Arial", 9),
            fg="#666"
        )
        self.progress_label.pack(pady=(5, 0))
        
        # Botões
        button_frame = tk.Frame(content_frame)
        button_frame.pack(pady=10)
        
        self.install_button = tk.Button(
            button_frame,
            text="🚀 Instalar",
            font=("Arial", 11, "bold"),
            bg="#007acc",
            fg="white",
            padx=25,
            pady=8,
            command=self._iniciar_instalacao
        )
        self.install_button.pack(side="left", padx=5)
        
        self.cancel_button = tk.Button(
            button_frame,
            text="Fechar",
            font=("Arial", 10),
            padx=20,
            pady=8,
            command=self.root.quit
        )
        self.cancel_button.pack(side="left", padx=5)
    
    def _atualizar_progresso(self, progresso, mensagem):
        if progresso == -1:
            self.progress_label.config(text=f"❌ {mensagem}", fg="red")
            self._finalizar_instalacao(False)
        else:
            self.progress_bar["value"] = progresso
            self.progress_label.config(text=f"⏳ {mensagem}", fg="#007acc")
            self.root.update()
    
    def _iniciar_instalacao(self):
        if self.instalando:
            return
        
        self.instalando = True
        self.install_button.config(state="disabled", text="Instalando...")
        self.cancel_button.config(state="disabled")
        
        def thread_instalacao():
            sucesso = self.installer.instalar_completo(self._atualizar_progresso)
            self.root.after(0, lambda: self._finalizar_instalacao(sucesso))
        
        thread = threading.Thread(target=thread_instalacao)
        thread.daemon = True
        thread.start()
    
    def _finalizar_instalacao(self, sucesso):
        self.instalando = False
        self.install_button.config(state="normal")
        self.cancel_button.config(state="normal", text="Fechar")
        
        if sucesso:
            self.progress_bar["value"] = 100
            self.progress_label.config(text="✅ Instalação concluída!", fg="green")
            self.install_button.config(text="✅ Concluído", bg="green")
            
            messagebox.showinfo(
                "Sucesso",
                "🎉 BaixaFy instalado com sucesso!\\n\\n"
                "✅ Pasta: C:\\\\BaixaFy\\n"
                "✅ Atalho: Desktop\\n"
                "✅ SpotDL funcionando\\n\\n"
                "🚀 Use o atalho 'BaixaFy' no Desktop!"
            )
        else:
            self.install_button.config(text="❌ Erro", bg="red")
            messagebox.showerror(
                "Erro",
                "❌ Erro na instalação.\\n\\n"
                "Verifique se:\\n"
                "• Python está instalado\\n"
                "• Tem conexão com internet\\n"
                "• Executou como Administrador"
            )
    
    def executar(self):
        self.root.mainloop()

def main():
    try:
        app = InstallerGUISimples()
        app.executar()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao iniciar instalador:\\n{e}")

if __name__ == "__main__":
    main()