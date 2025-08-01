#!/usr/bin/env python3
"""
BaixaFy Interface - Baseada no baixar.py original
Interface gráfica completa com CustomTkinter para baixar músicas do Spotify.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import sys
import subprocess
from pathlib import Path
import time

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class BaixaFyInterface:
    """Interface principal do BaixaFy baseada no baixar.py original."""
    
    def __init__(self):
        """Inicializa interface."""
        self.root = ctk.CTk()
        self.pasta_destino = self._obter_pasta_musicas()
        self.baixando = False
        self.processo_atual = None
        
        self._configurar_janela()
        self._criar_interface()
        self._verificar_spotdl()
    
    def _obter_pasta_musicas(self) -> str:
        """Obtém pasta padrão de música."""
        try:
            # Tentar pasta padrão do Windows
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                              r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                return winreg.QueryValueEx(key, "My Music")[0]
        except:
            # Fallback para pasta Music do usuário
            music_folder = Path.home() / "Music" / "BaixaFy"
            music_folder.mkdir(parents=True, exist_ok=True)
            return str(music_folder)
    
    def _configurar_janela(self):
        """Configura janela principal."""
        self.root.title("🎵 BaixaFy - Baixador de Músicas do Spotify")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
    
    def _criar_interface(self):
        """Cria interface completa estilo Spotify."""
        
        # Header com gradiente
        header_frame = ctk.CTkFrame(self.root, height=120, fg_color=["#1DB954", "#1ed760"])
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Título e logo
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.pack(expand=True, fill="both")
        
        logo_title = ctk.CTkLabel(
            title_container,
            text="🎵 BaixaFy",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="white"
        )
        logo_title.pack(pady=(25, 5))
        
        subtitle = ctk.CTkLabel(
            title_container,
            text="Baixador de Músicas e Playlists do Spotify • Versão Portátil",
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        subtitle.pack()
        
        # Área principal
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Seção URL
        url_section = ctk.CTkFrame(main_frame)
        url_section.pack(fill="x", pady=(0, 20))
        
        url_label = ctk.CTkLabel(
            url_section,
            text="🔗 Cole o link da música ou playlist do Spotify:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        url_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Campo URL
        self.url_entry = ctk.CTkEntry(
            url_section,
            placeholder_text="https://open.spotify.com/track/... ou /playlist/...",
            height=45,
            font=ctk.CTkFont(size=13),
            corner_radius=10
        )
        self.url_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Seção pasta
        pasta_section = ctk.CTkFrame(main_frame)
        pasta_section.pack(fill="x", pady=(0, 20))
        
        pasta_label = ctk.CTkLabel(
            pasta_section,
            text="📁 Pasta onde salvar as músicas:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        pasta_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        pasta_frame = ctk.CTkFrame(pasta_section, fg_color="transparent")
        pasta_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.pasta_entry = ctk.CTkEntry(
            pasta_frame,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.pasta_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.pasta_entry.insert(0, self.pasta_destino)
        
        btn_pasta = ctk.CTkButton(
            pasta_frame,
            text="Escolher Pasta",
            width=130,
            height=40,
            font=ctk.CTkFont(size=12),
            command=self._selecionar_pasta
        )
        btn_pasta.pack(side="right")
        
        # Área de log/progresso
        log_section = ctk.CTkFrame(main_frame)
        log_section.pack(fill="both", expand=True, pady=(0, 20))
        
        log_label = ctk.CTkLabel(
            log_section,
            text="📋 Log de atividades:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        log_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # TextBox para log
        self.log_textbox = ctk.CTkTextbox(
            log_section,
            height=200,
            font=ctk.CTkFont(size=11)
        )
        self.log_textbox.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 10))
        
        self.btn_download = ctk.CTkButton(
            buttons_frame,
            text="⬇️ Baixar",
            height=55,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#1DB954",
            hover_color="#1ed760",
            corner_radius=30,
            command=self._iniciar_download
        )
        self.btn_download.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_parar = ctk.CTkButton(
            buttons_frame,
            text="⏹️ Parar",
            height=55,
            width=120,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#dc3545",
            hover_color="#c82333",
            corner_radius=30,
            command=self._parar_download,
            state="disabled"
        )
        self.btn_parar.pack(side="right")
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            self.root,
            text="✅ BaixaFy pronto para usar!",
            font=ctk.CTkFont(size=12),
            text_color="#1DB954"
        )
        self.status_label.pack(pady=10)
    
    def _verificar_spotdl(self):
        """Verifica se SpotDL está funcionando."""
        def verificar():
            try:
                result = subprocess.run(['spotdl', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    versao = result.stdout.strip()
                    self.root.after(0, self._spotdl_ok, versao)
                else:
                    self.root.after(0, self._spotdl_erro, "SpotDL não encontrado")
            except Exception as e:
                self.root.after(0, self._spotdl_erro, str(e))
        
        thread = threading.Thread(target=verificar)
        thread.daemon = True
        thread.start()
    
    def _spotdl_ok(self, versao: str):
        """SpotDL funcionando."""
        self._log(f"✅ SpotDL instalado: {versao}")
        self._atualizar_status("✅ SpotDL funcionando! Pronto para baixar.")
    
    def _spotdl_erro(self, erro: str):
        """Erro no SpotDL."""
        self._log(f"❌ Erro no SpotDL: {erro}")
        self._atualizar_status("❌ Erro no SpotDL. Verifique instalação.")
        
        messagebox.showerror(
            "SpotDL não encontrado",
            "❌ SpotDL não está funcionando!\n\n"
            "Possíveis soluções:\n"
            "• Verifique se está no venv correto\n"
            "• Execute: pip install spotdl\n"
            "• Reinicie o BaixaFy"
        )
    
    def _selecionar_pasta(self):
        """Seleciona pasta de destino."""
        pasta = filedialog.askdirectory(
            title="Escolha onde salvar as músicas",
            initialdir=self.pasta_destino
        )
        if pasta:
            self.pasta_destino = pasta
            self.pasta_entry.delete(0, tk.END)
            self.pasta_entry.insert(0, pasta)
            self._log(f"📁 Pasta alterada para: {pasta}")
    
    def _iniciar_download(self):
        """Inicia processo de download."""
        if self.baixando:
            messagebox.showinfo("Download em andamento", "Aguarde o download atual terminar!")
            return
        
        url = self.url_entry.get().strip()
        pasta = self.pasta_entry.get().strip()
        
        # Validações
        if not url:
            messagebox.showwarning("URL vazia", "Cole um link do Spotify!")
            return
        
        if not self._validar_url_spotify(url):
            messagebox.showerror(
                "URL inválida",
                "Use apenas links do Spotify!\n\n"
                "Exemplos válidos:\n"
                "• https://open.spotify.com/track/...\n"
                "• https://open.spotify.com/playlist/..."
            )
            return
        
        if not pasta:
            messagebox.showwarning("Pasta inválida", "Escolha uma pasta válida!")
            return
        
        # Criar pasta se necessário
        try:
            Path(pasta).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Erro na pasta", f"Erro ao criar pasta:\n{e}")
            return
        
        # Iniciar download
        self.baixando = True
        self.btn_download.configure(state="disabled", text="⏳ Baixando...")
        self.btn_parar.configure(state="normal")
        self._log(f"🎵 Iniciando download: {url}")
        self._log(f"📁 Destino: {pasta}")
        self._atualizar_status("🔄 Download em andamento...")
        
        # Thread de download
        thread = threading.Thread(target=self._download_thread, args=(url, pasta))
        thread.daemon = True
        thread.start()
    
    def _validar_url_spotify(self, url: str) -> bool:
        """Valida URL do Spotify."""
        patterns = [
            "https://open.spotify.com/track/",
            "https://open.spotify.com/playlist/",
            "https://open.spotify.com/album/",
            "https://spotify.link/"
        ]
        return any(url.startswith(pattern) for pattern in patterns)
    
    def _download_thread(self, url: str, pasta: str):
        """Thread de download."""
        try:
            # Comando SpotDL
            cmd = [
                'spotdl',
                url,
                '--output', pasta,
                '--format', 'mp3',
                '--bitrate', '320k'
            ]
            
            self.root.after(0, self._log, f"💻 Comando: {' '.join(cmd)}")
            
            # Executar com output em tempo real
            self.processo_atual = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True,
                bufsize=1
            )
            
            # Ler output em tempo real
            for line in iter(self.processo_atual.stdout.readline, ''):
                if line.strip():
                    self.root.after(0, self._log, f"🔄 {line.strip()}")
            
            # Aguardar conclusão
            return_code = self.processo_atual.wait()
            
            if return_code == 0:
                self.root.after(0, self._download_sucesso, pasta)
            else:
                self.root.after(0, self._download_erro, f"Código de saída: {return_code}")
                
        except Exception as e:
            self.root.after(0, self._download_erro, str(e))
        finally:
            self.processo_atual = None
    
    def _parar_download(self):
        """Para download atual."""
        if self.processo_atual:
            try:
                self.processo_atual.terminate()
                self._log("⏹️ Download cancelado pelo usuário")
                self._atualizar_status("⏹️ Download cancelado")
            except:
                pass
        
        self._finalizar_download()
    
    def _download_sucesso(self, pasta: str):
        """Download concluído com sucesso."""
        self._log("✅ Download concluído com sucesso!")
        self._atualizar_status("✅ Download concluído!")
        
        messagebox.showinfo(
            "Download Concluído!",
            f"🎉 Suas músicas foram baixadas!\n\n"
            f"📁 Pasta: {pasta}\n\n"
            f"🎵 Agora é só curtir!"
        )
        
        self._finalizar_download()
    
    def _download_erro(self, erro: str):
        """Erro no download."""
        self._log(f"❌ Erro no download: {erro}")
        self._atualizar_status("❌ Erro no download")
        
        messagebox.showerror(
            "Erro no Download",
            f"❌ Erro ao baixar música:\n\n{erro}\n\n"
            f"Possíveis causas:\n"
            f"• Música não disponível no YouTube\n"
            f"• Problemas de conexão\n"
            f"• URL inválida ou expirada"
        )
        
        self._finalizar_download()
    
    def _finalizar_download(self):
        """Finaliza processo de download."""
        self.baixando = False
        self.btn_download.configure(state="normal", text="⬇️ Baixar")
        self.btn_parar.configure(state="disabled")
    
    def _log(self, mensagem: str):
        """Adiciona mensagem ao log."""
        timestamp = time.strftime("%H:%M:%S")
        linha = f"[{timestamp}] {mensagem}\n"
        
        self.log_textbox.insert("end", linha)
        self.log_textbox.see("end")  # Scroll para o fim
    
    def _atualizar_status(self, mensagem: str):
        """Atualiza status bar."""
        self.status_label.configure(text=mensagem)
        
        # Cores baseadas no ícone
        if "✅" in mensagem or "🎉" in mensagem:
            self.status_label.configure(text_color="#1DB954")
        elif "❌" in mensagem:
            self.status_label.configure(text_color="#dc3545")
        elif "⚠️" in mensagem:
            self.status_label.configure(text_color="#ffc107")
        elif "🔄" in mensagem or "⏳" in mensagem:
            self.status_label.configure(text_color="#17a2b8")
    
    def executar(self):
        """Executa aplicação."""
        # Log inicial
        self._log("🎵 BaixaFy iniciado!")
        self._log("📋 Versão portátil com Python embeddable")
        self._log("🔍 Verificando SpotDL...")
        
        # Executar
        self.root.mainloop()

def main():
    """Função principal."""
    try:
        app = BaixaFyInterface()
        app.executar()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Erro ao iniciar BaixaFy:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()