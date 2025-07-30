#!/usr/bin/env python3
"""
BaixaFy - Aplicativo Desktop para baixar músicas do Spotify
Versão: 1.0.0
Autor: Seu Nome

Dependências necessárias:
pip install customtkinter spotdl pillow
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
import time

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SpotifyDownloader:
    """Classe responsável por gerenciar downloads do Spotify via spotDL."""
    
    def __init__(self):
        self.is_spotdl_available = self._verificar_spotdl()
    
    def _verificar_spotdl(self) -> bool:
        """
        Verifica se o spotDL está instalado no sistema.
        
        Returns:
            bool: True se spotDL estiver disponível, False caso contrário
        """
        try:
            result = subprocess.run(['spotdl', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def buscar_musicas_playlist(self, url: str) -> List[Dict]:
        """
        Busca informações das músicas de uma playlist ou música individual.
        
        Args:
            url (str): URL do Spotify (playlist ou música)
            
        Returns:
            List[Dict]: Lista com informações das músicas
        """
        try:
            # Comando para listar músicas sem baixar
            cmd = ['spotdl', 'list', url]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception(f"Erro ao buscar playlist: {result.stderr}")
            
            # Processar saída do spotdl
            musicas = []
            linhas = result.stdout.strip().split('\n')
            
            for i, linha in enumerate(linhas):
                linha = linha.strip()
                if linha and not linha.startswith('Found') and not linha.startswith('Processing'):
                    # Extrair informações da linha
                    if ' - ' in linha:
                        musicas.append({
                            'id': i,
                            'nome': linha,
                            'url': url if '/' not in linha else None,
                            'selecionada': True,
                            'status': 'Aguardando'
                        })
            
            # Se não encontrou músicas na saída, pode ser uma música individual
            if not musicas and url:
                nome_musica = url.split('/')[-1].replace('?', ' - ').split('?')[0]
                musicas.append({
                    'id': 0,
                    'nome': f"Música do link: {nome_musica}",
                    'url': url,
                    'selecionada': True,
                    'status': 'Aguardando'
                })
            
            return musicas
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout ao buscar playlist. Tente novamente.")
        except Exception as e:
            raise Exception(f"Erro ao processar playlist: {str(e)}")
    
    def baixar_musica(self, url: str, pasta_destino: str, callback_progresso=None) -> bool:
        """
        Baixa uma música específica do Spotify.
        
        Args:
            url (str): URL da música no Spotify
            pasta_destino (str): Pasta onde salvar o arquivo
            callback_progresso (callable): Função para atualizar progresso
            
        Returns:
            bool: True se download foi bem-sucedido
        """
        try:
            cmd = [
                'spotdl',
                url,
                '--output', pasta_destino,
                '--format', 'mp3',
                '--bitrate', '320k'
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True)
            
            # Simular progresso (spotdl não fornece progresso real facilmente)
            for i in range(0, 101, 10):
                if callback_progresso:
                    callback_progresso(i)
                time.sleep(0.3)
                
                # Verificar se processo ainda está rodando
                if process.poll() is not None:
                    break
            
            process.wait()
            
            if callback_progresso:
                callback_progresso(100)
            
            return process.returncode == 0
            
        except Exception as e:
            print(f"Erro no download: {e}")
            return False

class BaixaFyApp:
    """Aplicativo principal do BaixaFy."""
    
    def __init__(self):
        """Inicializa a aplicação."""
        self.root = ctk.CTk()
        self.downloader = SpotifyDownloader()
        self.musicas_lista = []
        self.pasta_destino = self._obter_pasta_musicas_padrao()
        
        self._configurar_janela()
        self._criar_interface()
        
    def _obter_pasta_musicas_padrao(self) -> str:
        """
        Obtém a pasta padrão de músicas do Windows.
        
        Returns:
            str: Caminho para pasta Música do usuário
        """
        if os.name == 'nt':  # Windows
            return str(Path.home() / "Music")
        else:  # Linux/Mac
            return str(Path.home() / "Music")
    
    def _configurar_janela(self):
        """Configura a janela principal da aplicação."""
        self.root.title("🎵 BaixaFy - Spotify Downloader")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Ícone da janela (se tiver um arquivo de ícone)
        try:
            self.root.iconbitmap("baixafy_icon.ico")
        except:
            pass  # Ignora se não encontrar o ícone
    
    def _criar_interface(self):
        """Cria todos os elementos da interface gráfica."""
        
        # Header com título
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🎵 BaixaFy", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Baixe suas músicas favoritas do Spotify",
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Frame para URL e busca
        url_frame = ctk.CTkFrame(self.root)
        url_frame.pack(fill="x", padx=20, pady=10)
        
        url_label = ctk.CTkLabel(url_frame, text="🔗 Cole a URL do Spotify:")
        url_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Campo de entrada da URL
        self.url_entry = ctk.CTkEntry(
            url_frame,
            placeholder_text="https://open.spotify.com/playlist/...",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.url_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Botão de pesquisa
        self.btn_pesquisar = ctk.CTkButton(
            url_frame,
            text="🔍 Pesquisar Músicas",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._pesquisar_musicas
        )
        self.btn_pesquisar.pack(pady=(0, 15))
        
        # Frame para seleção de pasta
        pasta_frame = ctk.CTkFrame(self.root)
        pasta_frame.pack(fill="x", padx=20, pady=10)
        
        pasta_label = ctk.CTkLabel(pasta_frame, text="📁 Pasta de destino:")
        pasta_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        pasta_row = ctk.CTkFrame(pasta_frame)
        pasta_row.pack(fill="x", padx=15, pady=(0, 15))
        
        self.pasta_entry = ctk.CTkEntry(
            pasta_row,
            height=35,
            font=ctk.CTkFont(size=11)
        )
        self.pasta_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.pasta_entry.insert(0, self.pasta_destino)
        
        btn_selecionar_pasta = ctk.CTkButton(
            pasta_row,
            text="Escolher Pasta",
            width=120,
            height=35,
            command=self._selecionar_pasta
        )
        btn_selecionar_pasta.pack(side="right")
        
        # Frame para lista de músicas
        self.musicas_frame = ctk.CTkFrame(self.root)
        self.musicas_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        musicas_label = ctk.CTkLabel(
            self.musicas_frame, 
            text="🎶 Músicas encontradas:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        musicas_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Scrollable frame para lista de músicas
        self.scroll_frame = ctk.CTkScrollableFrame(self.musicas_frame)
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Frame para botões de ação
        actions_frame = ctk.CTkFrame(self.root)
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Botões de seleção
        select_frame = ctk.CTkFrame(actions_frame)
        select_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        btn_selecionar_todas = ctk.CTkButton(
            select_frame,
            text="✅ Selecionar Todas",
            width=150,
            command=self._selecionar_todas
        )
        btn_selecionar_todas.pack(side="left", padx=(0, 10))
        
        btn_desselecionar_todas = ctk.CTkButton(
            select_frame,
            text="❌ Desselecionar Todas",
            width=150,
            command=self._desselecionar_todas
        )
        btn_desselecionar_todas.pack(side="left")
        
        # Botão principal de download
        self.btn_download = ctk.CTkButton(
            actions_frame,
            text="⬇️ Baixar Músicas Selecionadas",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green",
            hover_color="darkgreen",
            command=self._iniciar_download
        )
        self.btn_download.pack(fill="x", padx=15, pady=(0, 15))
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            self.root,
            text="🔄 Verificando dependências...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Verificar se SpotDL está disponível (mas não bloquear o app)
        if not self.downloader.is_spotdl_available:
            self._mostrar_erro_spotdl()
        else:
            self._atualizar_status("✅ Pronto para usar! SpotDL está funcionando.")
    
    def _instalar_spotdl_automatico(self):
        """Tenta instalar SpotDL automaticamente."""
        self._atualizar_status("📦 Instalando SpotDL... aguarde...")
        
        # Desabilitar interface durante instalação
        self.btn_pesquisar.configure(state="disabled")
        
        def instalar_thread():
            try:
                import subprocess
                import sys
                
                # Tentar instalar spotdl
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 'spotdl'
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    # Verificar se funcionou
                    self.downloader = SpotifyDownloader()
                    if self.downloader.is_spotdl_available:
                        self.root.after(0, self._instalacao_sucesso)
                    else:
                        self.root.after(0, self._instalacao_erro, "SpotDL instalado mas não está funcionando")
                else:
                    self.root.after(0, self._instalacao_erro, result.stderr)
                    
            except subprocess.TimeoutExpired:
                self.root.after(0, self._instalacao_erro, "Timeout na instalação")
            except Exception as e:
                self.root.after(0, self._instalacao_erro, str(e))
        
        # Executar instalação em thread separada
        thread = threading.Thread(target=instalar_thread)
        thread.daemon = True
        thread.start()
    
    def _instalacao_sucesso(self):
        """Callback quando SpotDL é instalado com sucesso."""
        self.btn_pesquisar.configure(state="normal")
        self._atualizar_status("✅ SpotDL instalado com sucesso!")
        messagebox.showinfo(
            "Instalação Concluída",
            "✅ SpotDL foi instalado com sucesso!\n\n"
            "Agora você pode usar todas as funcionalidades do BaixaFy."
        )
    
    def _instalacao_erro(self, erro):
        """Callback quando há erro na instalação do SpotDL."""
        self.btn_pesquisar.configure(state="normal")
        self._atualizar_status("❌ Erro na instalação do SpotDL")
        messagebox.showerror(
            "Erro na Instalação",
            f"❌ Não foi possível instalar o SpotDL automaticamente:\n\n"
            f"{erro}\n\n"
            "Tente instalar manualmente:\n"
            "1. Abra o terminal\n"
            "2. Execute: pip install spotdl"
        )
    
    def _mostrar_erro_spotdl(self):
        """Mostra opções se spotDL não estiver instalado."""
        resposta = messagebox.askyesno(
            "SpotDL não encontrado",
            "O SpotDL não está instalado!\n\n"
            "Para usar o BaixaFy, você precisa instalar o SpotDL.\n\n"
            "Deseja que eu tente instalar automaticamente?\n\n"
            "Clique 'Sim' para instalar automaticamente\n"
            "Clique 'Não' para instruções manuais"
        )
        
        if resposta:
            self._instalar_spotdl_automatico()
        else:
            messagebox.showinfo(
                "Instalação Manual",
                "Para instalar o SpotDL manualmente:\n\n"
                "1. Abra o terminal/prompt de comando\n"
                "2. Execute: pip install spotdl\n"
                "3. Reinicie o BaixaFy\n\n"
                "O aplicativo continuará funcionando, mas os downloads não funcionarão sem o SpotDL."
            )
            self._atualizar_status("⚠️ SpotDL não instalado - use 'Pesquisar' ou 'Baixar' para instalar")
    
    def _pesquisar_musicas(self):
        """Pesquisa músicas da URL fornecida."""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("URL vazia", "Por favor, cole uma URL do Spotify!")
            return
        
        if not url.startswith('https://open.spotify.com/'):
            messagebox.showerror("URL inválida", "Use apenas URLs do Spotify!")
            return
        
        # Verificar se SpotDL está disponível
        if not self.downloader.is_spotdl_available:
            resposta = messagebox.askyesno(
                "SpotDL Necessário",
                "O SpotDL não está instalado!\n\n"
                "Deseja tentar instalar automaticamente?"
            )
            if resposta:
                self._instalar_spotdl_automatico()
            return
        
        self._atualizar_status("🔍 Buscando músicas...")
        self.btn_pesquisar.configure(state="disabled", text="Buscando...")
        
        # Executar busca em thread separada
        thread = threading.Thread(target=self._buscar_musicas_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def _buscar_musicas_thread(self, url: str):
        """
        Thread para buscar músicas sem travar a interface.
        
        Args:
            url (str): URL do Spotify para buscar
        """
        try:
            musicas = self.downloader.buscar_musicas_playlist(url)
            
            # Atualizar interface na thread principal
            self.root.after(0, self._mostrar_musicas, musicas)
            
        except Exception as e:
            self.root.after(0, self._erro_busca, str(e))
    
    def _mostrar_musicas(self, musicas: List[Dict]):
        """
        Mostra a lista de músicas encontradas na interface.
        
        Args:
            musicas (List[Dict]): Lista de músicas para exibir
        """
        self.musicas_lista = musicas
        
        # Limpar lista anterior
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Adicionar cada música com checkbox
        for musica in musicas:
            musica_frame = ctk.CTkFrame(self.scroll_frame)
            musica_frame.pack(fill="x", pady=5)
            
            # Checkbox para seleção
            checkbox_var = tk.BooleanVar(value=musica['selecionada'])
            checkbox = ctk.CTkCheckBox(
                musica_frame,
                text=musica['nome'],
                variable=checkbox_var,
                font=ctk.CTkFont(size=12)
            )
            checkbox.pack(anchor="w", padx=15, pady=10)
            
            # Armazenar referência ao checkbox
            musica['checkbox_var'] = checkbox_var
            
            # Label de status
            status_label = ctk.CTkLabel(
                musica_frame,
                text=musica['status'],
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            status_label.pack(anchor="e", padx=15, pady=(0, 10))
            musica['status_label'] = status_label
        
        self._atualizar_status(f"✅ {len(musicas)} música(s) encontrada(s)!")
        self.btn_pesquisar.configure(state="normal", text="🔍 Pesquisar Músicas")
    
    def _erro_busca(self, erro: str):
        """
        Trata erros na busca de músicas.
        
        Args:
            erro (str): Mensagem de erro
        """
        messagebox.showerror("Erro na busca", f"Erro ao buscar músicas:\n{erro}")
        self._atualizar_status("❌ Erro na busca. Tente novamente.")
        self.btn_pesquisar.configure(state="normal", text="🔍 Pesquisar Músicas")
    
    def _selecionar_pasta(self):
        """Abre diálogo para selecionar pasta de destino."""
        pasta = filedialog.askdirectory(
            title="Escolha a pasta para salvar as músicas",
            initialdir=self.pasta_destino
        )
        
        if pasta:
            self.pasta_destino = pasta
            self.pasta_entry.delete(0, tk.END)
            self.pasta_entry.insert(0, pasta)
    
    def _selecionar_todas(self):
        """Seleciona todas as músicas da lista."""
        for musica in self.musicas_lista:
            if 'checkbox_var' in musica:
                musica['checkbox_var'].set(True)
    
    def _desselecionar_todas(self):
        """Desseleciona todas as músicas da lista."""
        for musica in self.musicas_lista:
            if 'checkbox_var' in musica:
                musica['checkbox_var'].set(False)
    
    def _iniciar_download(self):
        """Inicia o download das músicas selecionadas."""
        if not self.musicas_lista:
            messagebox.showwarning("Nenhuma música", "Primeiro pesquise por músicas!")
            return
        
        # Verificar se SpotDL está disponível
        if not self.downloader.is_spotdl_available:
            resposta = messagebox.askyesno(
                "SpotDL Necessário",
                "O SpotDL não está instalado!\n\n"
                "Deseja tentar instalar automaticamente?"
            )
            if resposta:
                self._instalar_spotdl_automatico()
            return
        
        # Verificar quais músicas estão selecionadas
        musicas_selecionadas = [
            musica for musica in self.musicas_lista
            if 'checkbox_var' in musica and musica['checkbox_var'].get()
        ]
        
        if not musicas_selecionadas:
            messagebox.showwarning("Nenhuma selecionada", "Selecione pelo menos uma música!")
            return
        
        # Verificar pasta de destino
        pasta = self.pasta_entry.get().strip()
        if not pasta:
            messagebox.showwarning("Pasta inválida", "Escolha uma pasta válida!")
            return
        
        # Criar pasta se não existir
        try:
            Path(pasta).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Erro na pasta", f"Erro ao criar pasta:\n{e}")
            return
        
        # Desabilitar botão durante download
        self.btn_download.configure(state="disabled", text="Baixando...")
        
        # Iniciar download em thread separada
        thread = threading.Thread(
            target=self._download_thread, 
            args=(musicas_selecionadas, pasta)
        )
        thread.daemon = True
        thread.start()
    
    def _download_thread(self, musicas: List[Dict], pasta: str):
        """
        Thread para fazer download das músicas.
        
        Args:
            musicas (List[Dict]): Lista de músicas para baixar
            pasta (str): Pasta de destino
        """
        url_original = self.url_entry.get().strip()
        sucessos = 0
        
        for i, musica in enumerate(musicas):
            # Atualizar status na interface
            self.root.after(0, self._atualizar_status_musica, musica, "⏳ Baixando...")
            
            try:
                # Download real com spotDL
                sucesso = self._baixar_musica_real(url_original, pasta, musica)
                
                if sucesso:
                    sucessos += 1
                    self.root.after(0, self._atualizar_status_musica, musica, "✅ Concluído")
                else:
                    self.root.after(0, self._atualizar_status_musica, musica, "❌ Erro")
                    
            except Exception as e:
                print(f"Erro no download: {e}")
                self.root.after(0, self._atualizar_status_musica, musica, f"❌ Erro: {str(e)[:20]}")
        
        # Reabilitar botão
        self.root.after(0, self._finalizar_download, len(musicas), sucessos)
    
    def _baixar_musica_real(self, url: str, pasta: str, musica: Dict) -> bool:
        """
        Faz o download real de uma música usando spotDL.
        
        Args:
            url (str): URL original do Spotify
            pasta (str): Pasta de destino
            musica (Dict): Dados da música
            
        Returns:
            bool: True se sucesso
        """
        try:
            cmd = [
                'spotdl',
                url,
                '--output', pasta,
                '--format', 'mp3',
                '--bitrate', '320k'
            ]
            
            # Executar comando spotDL
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("Timeout no download")
            return False
        except Exception as e:
            print(f"Erro no download: {e}")
            return False
    
    def _atualizar_status_musica(self, musica: Dict, status: str):
        """
        Atualiza o status de uma música específica.
        
        Args:
            musica (Dict): Dados da música
            status (str): Novo status
        """
        if 'status_label' in musica:
            musica['status_label'].configure(text=status)
        musica['status'] = status
    
    def _finalizar_download(self, total: int, sucessos: int):
        """
        Finaliza o processo de download.
        
        Args:
            total (int): Total de músicas processadas
            sucessos (int): Número de downloads bem-sucedidos
        """
        self.btn_download.configure(state="normal", text="⬇️ Baixar Músicas Selecionadas")
        
        if sucessos == total:
            self._atualizar_status(f"🎉 Download concluído! {sucessos} música(s) baixada(s).")
            messagebox.showinfo(
                "Download Concluído",
                f"✅ {sucessos} de {total} música(s) baixada(s) com sucesso!\n\n"
                f"📁 Pasta: {self.pasta_entry.get()}"
            )
        elif sucessos > 0:
            self._atualizar_status(f"⚠️ Parcialmente concluído: {sucessos}/{total} música(s).")
            messagebox.showwarning(
                "Download Parcial",
                f"⚠️ {sucessos} de {total} música(s) baixada(s).\n\n"
                f"Algumas músicas falharam. Verifique sua conexão.\n\n"
                f"📁 Pasta: {self.pasta_entry.get()}"
            )
        else:
            self._atualizar_status("❌ Falha no download. Verifique sua conexão.")
            messagebox.showerror(
                "Falha no Download",
                "❌ Nenhuma música foi baixada com sucesso.\n\n"
                "Possíveis causas:\n"
                "• Problemas de conexão\n"
                "• Músicas não disponíveis\n"
                "• SpotDL com problemas"
            )
    
    def _atualizar_status(self, mensagem: str):
        """
        Atualiza a barra de status.
        
        Args:
            mensagem (str): Nova mensagem de status
        """
        self.status_label.configure(text=mensagem)
    
    def executar(self):
        """Inicia a aplicação."""
        self.root.mainloop()

def main():
    """Função principal do programa."""
    try:
        app = BaixaFyApp()
        app.executar()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Erro ao iniciar aplicação:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()