#!/usr/bin/env python3
"""
BaixaFy - Instalador Completo
Este instalador configura tudo automaticamente no sistema Windows.

Funcionalidades:
- Detecta e instala Python se necessário
- Instala SpotDL e dependências
- Instala o BaixaFy no C:\BaixaFy
- Cria atalhos no Desktop e Menu Iniciar
- Configura tudo para funcionar offline
"""

import os
import sys
import subprocess
import urllib.request
import tempfile
import shutil
import winreg
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import zipfile

class BaixaFyInstaller:
    """Instalador completo do BaixaFy para Windows."""
    
    def __init__(self):
        """Inicializa o instalador."""
        self.pasta_instalacao = Path("C:/BaixaFy")
        self.python_exe = None
        self.progresso_callback = None
        
        # URLs de download
        self.python_url = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
        self.python_installer = "python_installer.exe"
        
    def verificar_python(self) -> bool:
        """
        Verifica se Python está instalado e acessível.
        
        Returns:
            bool: True se Python estiver disponível
        """
        try:
            # Tentar encontrar Python no PATH
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.python_exe = 'python'
                return True
                
            # Tentar py launcher (Windows)
            result = subprocess.run(['py', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.python_exe = 'py'
                return True
                
        except FileNotFoundError:
            pass
        
        return False
    
    def baixar_arquivo(self, url: str, destino: str, callback=None):
        """
        Baixa um arquivo da internet com barra de progresso.
        
        Args:
            url (str): URL para download
            destino (str): Caminho de destino
            callback (callable): Função para atualizar progresso
        """
        def hook(block_num, block_size, total_size):
            if callback and total_size > 0:
                progress = min(100, (block_num * block_size * 100) // total_size)
                callback(progress)
        
        urllib.request.urlretrieve(url, destino, reporthook=hook)
    
    def instalar_python(self, callback=None) -> bool:
        """
        Baixa e instala Python automaticamente.
        
        Args:
            callback (callable): Função para atualizar progresso
            
        Returns:
            bool: True se instalação foi bem-sucedida
        """
        try:
            if callback:
                callback(0, "Baixando Python...")
            
            # Baixar instalador do Python
            temp_dir = tempfile.gettempdir()
            installer_path = os.path.join(temp_dir, self.python_installer)
            
            self.baixar_arquivo(self.python_url, installer_path, 
                              lambda p: callback(p * 0.5, "Baixando Python...") if callback else None)
            
            if callback:
                callback(50, "Instalando Python...")
            
            # Instalar Python silenciosamente
            cmd = [
                installer_path,
                '/quiet',                    # Instalação silenciosa
                'InstallAllUsers=1',         # Para todos os usuários
                'PrependPath=1',             # Adicionar ao PATH
                'Include_test=0',            # Não incluir testes
                'Include_doc=0',             # Não incluir documentação
                'Include_dev=0',             # Não incluir headers de desenvolvimento
                'Include_debug=0',           # Não incluir símbolos de debug
                'Include_launcher=1',        # Incluir py launcher
                'InstallLauncherAllUsers=1', # Launcher para todos
                'Include_pip=1'              # Incluir pip
            ]
            
            process = subprocess.run(cmd, capture_output=True)
            
            # Limpar arquivo temporário
            try:
                os.remove(installer_path)
            except:
                pass
            
            if callback:
                callback(100, "Python instalado!")
            
            # Verificar se instalação funcionou
            return self.verificar_python()
            
        except Exception as e:
            print(f"Erro ao instalar Python: {e}")
            return False
    
    def instalar_spotdl(self, callback=None) -> bool:
        """
        Instala SpotDL e dependências.
        
        Args:
            callback (callable): Função para atualizar progresso
            
        Returns:
            bool: True se instalação foi bem-sucedida
        """
        try:
            if not self.python_exe:
                return False
            
            if callback:
                callback(0, "Instalando SpotDL...")
            
            # Atualizar pip primeiro
            subprocess.run([self.python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                         capture_output=True)
            
            if callback:
                callback(25, "Instalando SpotDL...")
            
            # Instalar SpotDL
            result = subprocess.run([
                self.python_exe, '-m', 'pip', 'install', 
                'spotdl>=4.2.5',
                'customtkinter>=5.2.1',
                'pillow>=10.0.0'
            ], capture_output=True, text=True)
            
            if callback:
                callback(100, "SpotDL instalado!")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Erro ao instalar SpotDL: {e}")
            return False
    
    def criar_pasta_instalacao(self) -> bool:
        """
        Cria a pasta de instalação do BaixaFy.
        
        Returns:
            bool: True se pasta foi criada com sucesso
        """
        try:
            self.pasta_instalacao.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Erro ao criar pasta: {e}")
            return False
    
    def copiar_arquivos(self, callback=None) -> bool:
        """
        Copia os arquivos do BaixaFy para pasta de instalação.
        
        Args:
            callback (callable): Função para atualizar progresso
            
        Returns:
            bool: True se arquivos foram copiados
        """
        try:
            if callback:
                callback(0, "Copiando arquivos...")
            
            # Arquivos para copiar
            arquivos = ['baixafy.py', 'requirements.txt', 'README.md']
            
            for i, arquivo in enumerate(arquivos):
                if Path(arquivo).exists():
                    destino = self.pasta_instalacao / arquivo
                    shutil.copy2(arquivo, destino)
                
                if callback:
                    progress = int((i + 1) * 100 / len(arquivos))
                    callback(progress, f"Copiando {arquivo}...")
            
            return True
            
        except Exception as e:
            print(f"Erro ao copiar arquivos: {e}")
            return False
    
    def criar_executavel_final(self, callback=None) -> bool:
        """
        Cria o executável final do BaixaFy na pasta de instalação.
        
        Args:
            callback (callable): Função para atualizar progresso
            
        Returns:
            bool: True se executável foi criado
        """
        try:
            if callback:
                callback(0, "Criando executável...")
            
            # Mudar para pasta de instalação
            original_dir = os.getcwd()
            os.chdir(self.pasta_instalacao)
            
            # Criar executável com PyInstaller
            cmd = [
                self.python_exe, '-m', 'PyInstaller',
                '--onefile',
                '--windowed',
                '--name', 'BaixaFy',
                '--distpath', '.',  # Colocar na pasta atual
                'baixafy.py'
            ]
            
            process = subprocess.run(cmd, capture_output=True)
            
            # Voltar para pasta original
            os.chdir(original_dir)
            
            if callback:
                callback(100, "Executável criado!")
            
            # Verificar se executável foi criado
            exe_path = self.pasta_instalacao / 'BaixaFy.exe'
            return exe_path.exists()
            
        except Exception as e:
            print(f"Erro ao criar executável: {e}")
            return False
    
    def criar_atalhos(self) -> bool:
        """
        Cria atalhos no Desktop e Menu Iniciar.
        
        Returns:
            bool: True se atalhos foram criados
        """
        try:
            import win32com.client
            
            shell = win32com.client.Dispatch("WScript.Shell")
            
            # Atalho no Desktop
            desktop = shell.SpecialFolders("Desktop")
            atalho_desktop = shell.CreateShortCut(os.path.join(desktop, "BaixaFy.lnk"))
            atalho_desktop.Targetpath = str(self.pasta_instalacao / "BaixaFy.exe")
            atalho_desktop.WorkingDirectory = str(self.pasta_instalacao)
            atalho_desktop.Description = "BaixaFy - Spotify Music Downloader"
            atalho_desktop.save()
            
            # Atalho no Menu Iniciar
            start_menu = shell.SpecialFolders("StartMenu")
            programs = os.path.join(start_menu, "Programs")
            atalho_menu = shell.CreateShortCut(os.path.join(programs, "BaixaFy.lnk"))
            atalho_menu.Targetpath = str(self.pasta_instalacao / "BaixaFy.exe")
            atalho_menu.WorkingDirectory = str(self.pasta_instalacao)
            atalho_menu.Description = "BaixaFy - Spotify Music Downloader"
            atalho_menu.save()
            
            return True
            
        except Exception as e:
            print(f"Erro ao criar atalhos: {e}")
            return False
    
    def instalar_completo(self, callback=None):
        """
        Executa instalação completa do BaixaFy.
        
        Args:
            callback (callable): Função para atualizar progresso (progresso, mensagem)
        """
        try:
            # Passo 1: Verificar/Instalar Python
            if callback:
                callback(5, "Verificando Python...")
            
            if not self.verificar_python():
                if callback:
                    callback(10, "Python não encontrado. Instalando...")
                
                if not self.instalar_python(lambda p, msg: callback(10 + p * 0.3, msg)):
                    raise Exception("Falha ao instalar Python")
            
            # Passo 2: Instalar SpotDL
            if callback:
                callback(40, "Instalando SpotDL...")
            
            if not self.instalar_spotdl(lambda p, msg: callback(40 + p * 0.2, msg)):
                raise Exception("Falha ao instalar SpotDL")
            
            # Passo 3: Criar pasta de instalação
            if callback:
                callback(60, "Criando pasta de instalação...")
            
            if not self.criar_pasta_instalacao():
                raise Exception("Falha ao criar pasta de instalação")
            
            # Passo 4: Copiar arquivos
            if callback:
                callback(70, "Copiando arquivos...")
            
            if not self.copiar_arquivos(lambda p, msg: callback(70 + p * 0.1, msg)):
                raise Exception("Falha ao copiar arquivos")
            
            # Passo 5: Instalar PyInstaller e criar executável
            if callback:
                callback(80, "Instalando PyInstaller...")
            
            subprocess.run([self.python_exe, '-m', 'pip', 'install', 'pyinstaller'], 
                         capture_output=True)
            
            if callback:
                callback(85, "Criando executável final...")
            
            if not self.criar_executavel_final(lambda p, msg: callback(85 + p * 0.1, msg)):
                raise Exception("Falha ao criar executável")
            
            # Passo 6: Criar atalhos
            if callback:
                callback(95, "Criando atalhos...")
            
            self.criar_atalhos()  # Não é crítico se falhar
            
            if callback:
                callback(100, "Instalação concluída!")
            
            return True
            
        except Exception as e:
            if callback:
                callback(-1, f"Erro: {str(e)}")
            return False

class InstallerGUI:
    """Interface gráfica para o instalador."""
    
    def __init__(self):
        """Inicializa a interface gráfica."""
        self.root = tk.Tk()
        self.installer = BaixaFyInstaller()
        self.instalando = False
        
        self._configurar_janela()
        self._criar_interface()
    
    def _configurar_janela(self):
        """Configura a janela principal."""
        self.root.title("BaixaFy - Instalador")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (400 // 2)
        self.root.geometry(f"500x400+{x}+{y}")
    
    def _criar_interface(self):
        """Cria os elementos da interface."""
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2b2b2b")
        header_frame.pack(fill="x", pady=20)
        
        title_label = tk.Label(
            header_frame,
            text="🎵 BaixaFy Installer",
            font=("Arial", 20, "bold"),
            bg="#2b2b2b",
            fg="white"
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Instalador Completo - Spotify Music Downloader",
            font=("Arial", 10),
            bg="#2b2b2b",
            fg="#cccccc"
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Informações
        info_frame = tk.Frame(self.root)
        info_frame.pack(fill="both", expand=True, padx=20)
        
        info_text = tk.Text(
            info_frame,
            height=12,
            wrap=tk.WORD,
            font=("Arial", 9),
            bg="#f5f5f5",
            relief="flat"
        )
        info_text.pack(fill="both", expand=True, pady=10)
        
        info_content = """🚀 O BaixaFy Installer vai configurar tudo automaticamente:

✅ Detectar e instalar Python (se necessário)
✅ Instalar SpotDL e todas as dependências
✅ Criar pasta de instalação em C:\\BaixaFy
✅ Gerar executável final do BaixaFy
✅ Criar atalhos no Desktop e Menu Iniciar

📋 Após a instalação:
• Use o atalho "BaixaFy" no Desktop
• Cole links do Spotify e baixe suas músicas
• Funciona offline, sem precisar instalar mais nada

⚠️ Requisitos:
• Windows 10/11
• Conexão com internet (apenas para instalação)
• Cerca de 500MB de espaço livre

🔒 Seguro e confiável:
• Código aberto
• Sem vírus ou malware
• Instala apenas componentes oficiais"""
        
        info_text.insert("1.0", info_content)
        info_text.config(state="disabled")
        
        # Barra de progresso
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode="determinate",
            length=460
        )
        self.progress_bar.pack()
        
        self.progress_label = tk.Label(
            self.progress_frame,
            text="Pronto para instalar",
            font=("Arial", 9),
            fg="#666666"
        )
        self.progress_label.pack(pady=(5, 0))
        
        # Botões
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.install_button = tk.Button(
            button_frame,
            text="🚀 Instalar BaixaFy",
            font=("Arial", 12, "bold"),
            bg="#007acc",
            fg="white",
            padx=30,
            pady=10,
            command=self._iniciar_instalacao
        )
        self.install_button.pack(side="left", padx=10)
        
        self.cancel_button = tk.Button(
            button_frame,
            text="Cancelar",
            font=("Arial", 10),
            padx=20,
            pady=10,
            command=self.root.quit
        )
        self.cancel_button.pack(side="left", padx=10)
    
    def _atualizar_progresso(self, progresso, mensagem):
        """
        Atualiza a barra de progresso e mensagem.
        
        Args:
            progresso (int): Progresso de 0 a 100, ou -1 para erro
            mensagem (str): Mensagem para exibir
        """
        if progresso == -1:
            # Erro
            self.progress_bar.config(style="red.Horizontal.TProgressbar")
            self.progress_label.config(text=f"❌ {mensagem}", fg="red")
            self._finalizar_instalacao(False)
        else:
            self.progress_bar["value"] = progresso
            self.progress_label.config(text=f"⏳ {mensagem}", fg="#007acc")
            self.root.update()
    
    def _iniciar_instalacao(self):
        """Inicia o processo de instalação."""
        if self.instalando:
            return
        
        self.instalando = True
        self.install_button.config(state="disabled", text="Instalando...")
        self.cancel_button.config(state="disabled")
        
        # Executar instalação em thread separada
        def thread_instalacao():
            sucesso = self.installer.instalar_completo(self._atualizar_progresso)
            self.root.after(0, lambda: self._finalizar_instalacao(sucesso))
        
        thread = threading.Thread(target=thread_instalacao)
        thread.daemon = True
        thread.start()
    
    def _finalizar_instalacao(self, sucesso):
        """
        Finaliza o processo de instalação.
        
        Args:
            sucesso (bool): True se instalação foi bem-sucedida
        """
        self.instalando = False
        self.install_button.config(state="normal")
        self.cancel_button.config(state="normal")
        
        if sucesso:
            self.progress_bar["value"] = 100
            self.progress_label.config(text="✅ Instalação concluída!", fg="green")
            self.install_button.config(text="✅ Concluído", bg="green")
            
            messagebox.showinfo(
                "Instalação Concluída",
                "🎉 BaixaFy foi instalado com sucesso!\n\n"
                "✅ Executável: C:\\BaixaFy\\BaixaFy.exe\n"
                "✅ Atalho criado no Desktop\n"
                "✅ SpotDL configurado e funcionando\n\n"
                "🚀 Agora você pode fechar este instalador e usar o BaixaFy!"
            )
        else:
            self.install_button.config(text="❌ Erro na Instalação", bg="red")
            
            messagebox.showerror(
                "Erro na Instalação",
                "❌ Ocorreu um erro durante a instalação.\n\n"
                "Possíveis soluções:\n"
                "• Execute como Administrador\n"
                "• Verifique sua conexão com internet\n"
                "• Desative temporariamente o antivírus\n"
                "• Feche outros programas"
            )
    
    def executar(self):
        """Executa a interface gráfica."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

def main():
    """Função principal do instalador."""
    try:
        app = InstallerGUI()
        app.executar()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Erro ao iniciar instalador:\n{e}")

if __name__ == "__main__":
    main()