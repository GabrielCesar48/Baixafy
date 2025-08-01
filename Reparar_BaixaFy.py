#!/usr/bin/env python3
"""
Reparar BaixaFy - Script para corrigir problemas comuns
Reinstala dependências e corrige configurações.
"""

import os
import sys
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time

class ReparadorBaixaFy:
    """Interface para reparar problemas do BaixaFy."""
    
    def __init__(self):
        self.pasta_base = Path(__file__).parent.absolute()
        self.python_venv = self.pasta_base / "venv_portable" / "Scripts" / "python.exe"
        self.pip_venv = self.pasta_base / "venv_portable" / "Scripts" / "pip.exe"
        
        self.root = tk.Tk()
        self.root.title("🔧 Reparar BaixaFy")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self.reparando = False
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria interface do reparador."""
        # Título
        titulo = tk.Label(
            self.root,
            text="🔧 Reparar BaixaFy",
            font=("Arial", 20, "bold"),
            fg="#1DB954"
        )
        titulo.pack(pady=20)
        
        # Descrição
        desc = tk.Label(
            self.root,
            text="Este utilitário corrige problemas comuns do BaixaFy\n"
                 "reinstalando dependências e verificando configurações.",
            font=("Arial", 11),
            justify="center"
        )
        desc.pack(pady=10)
        
        # Frame de opções
        opcoes_frame = tk.LabelFrame(self.root, text="Opções de Reparo", font=("Arial", 12, "bold"))
        opcoes_frame.pack(pady=20, padx=20, fill="x")
        
        self.opcoes = {
            "verificar": tk.BooleanVar(value=True),
            "reinstalar_deps": tk.BooleanVar(value=True),
            "limpar_cache": tk.BooleanVar(value=True),
            "reconfigurar": tk.BooleanVar(value=True)
        }
        
        opcoes_texto = [
            ("verificar", "🔍 Verificar estrutura de arquivos"),
            ("reinstalar_deps", "📦 Reinstalar dependências Python"),
            ("limpar_cache", "🧹 Limpar cache do Python"),
            ("reconfigurar", "⚙️ Reconfigurar ambiente")
        ]
        
        for key, texto in opcoes_texto:
            cb = tk.Checkbutton(
                opcoes_frame,
                text=texto,
                variable=self.opcoes[key],
                font=("Arial", 10)
            )
            cb.pack(anchor="w", padx=20, pady=5)
        
        # Área de log
        log_frame = tk.LabelFrame(self.root, text="Log de Progresso", font=("Arial", 12, "bold"))
        log_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Text widget com scrollbar
        text_frame = tk.Frame(log_frame)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(
            text_frame,
            height=12,
            font=("Consolas", 9),
            wrap="word"
        )
        
        scrollbar = tk.Scrollbar(text_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Barra de progresso
        self.progresso = ttk.Progressbar(
            self.root,
            mode="indeterminate"
        )
        self.progresso.pack(pady=10, padx=20, fill="x")
        
        # Botões
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=10)
        
        self.btn_reparar = tk.Button(
            buttons_frame,
            text="🔧 Iniciar Reparo",
            font=("Arial", 12, "bold"),
            bg="#1DB954",
            fg="white",
            command=self._iniciar_reparo,
            width=15,
            height=2
        )
        self.btn_reparar.pack(side="left", padx=10)
        
        btn_fechar = tk.Button(
            buttons_frame,
            text="❌ Fechar",
            font=("Arial", 12),
            command=self.root.quit,
            width=10,
            height=2
        )
        btn_fechar.pack(side="left", padx=10)
        
        # Log inicial
        self._log("🔧 Reparador BaixaFy iniciado")
        self._log(f"📁 Pasta base: {self.pasta_base}")
    
    def _log(self, mensagem):
        """Adiciona mensagem ao log."""
        timestamp = time.strftime("%H:%M:%S")
        linha = f"[{timestamp}] {mensagem}\n"
        
        self.log_text.insert("end", linha)
        self.log_text.see("end")
        self.root.update_idletasks()
    
    def _iniciar_reparo(self):
        """Inicia processo de reparo."""
        if self.reparando:
            messagebox.showinfo("Reparo em Andamento", "Aguarde o reparo atual terminar!")
            return
        
        # Confirmar
        resposta = messagebox.askyesno(
            "Confirmar Reparo",
            "Deseja iniciar o reparo do BaixaFy?\n\n"
            "Este processo pode demorar alguns minutos."
        )
        
        if not resposta:
            return
        
        self.reparando = True
        self.btn_reparar.configure(state="disabled", text="🔄 Reparando...")
        self.progresso.start()
        
        # Executar em thread separada
        thread = threading.Thread(target=self._executar_reparo)
        thread.daemon = True
        thread.start()
    
    def _executar_reparo(self):
        """Executa o reparo em thread separada."""
        try:
            self._log("🚀 Iniciando processo de reparo...")
            
            sucesso = True
            
            if self.opcoes["verificar"].get():
                if not self._verificar_estrutura():
                    sucesso = False
            
            if self.opcoes["limpar_cache"].get():
                if not self._limpar_cache():
                    sucesso = False
            
            if self.opcoes["reinstalar_deps"].get():
                if not self._reinstalar_dependencias():
                    sucesso = False
            
            if self.opcoes["reconfigurar"].get():
                if not self._reconfigurar_ambiente():
                    sucesso = False
            
            # Resultado final
            if sucesso:
                self._log("✅ Reparo concluído com sucesso!")
                self.root.after(0, self._reparo_sucesso)
            else:
                self._log("❌ Reparo concluído com alguns problemas")
                self.root.after(0, self._reparo_com_problemas)
                
        except Exception as e:
            self._log(f"❌ Erro crítico no reparo: {e}")
            self.root.after(0, self._reparo_erro, str(e))
        
        finally:
            self.root.after(0, self._finalizar_reparo)
    
    def _verificar_estrutura(self):
        """Verifica estrutura de arquivos."""
        self._log("🔍 Verificando estrutura de arquivos...")
        
        arquivos_criticos = [
            ("Python Portátil", self.python_venv),
            ("Pip Portátil", self.pip_venv),
            ("Interface Principal", self.pasta_base / "baixafy_interface.py"),
            ("FFmpeg", self.pasta_base / "ffmpeg-7.1.1" / "bin" / "ffmpeg.exe")
        ]
        
        problemas = []
        
        for nome, caminho in arquivos_criticos:
            if caminho.exists():
                self._log(f"   ✅ {nome}")
            else:
                self._log(f"   ❌ {nome} - FALTANDO!")
                problemas.append(nome)
        
        if problemas:
            self._log(f"❌ {len(problemas)} arquivo(s) crítico(s) faltando!")
            return False
        
        self._log("✅ Estrutura de arquivos OK")
        return True
    
    def _limpar_cache(self):
        """Limpa cache do Python."""
        self._log("🧹 Limpando cache do Python...")
        
        try:
            # Limpar __pycache__
            import shutil
            
            cache_dirs = list(self.pasta_base.rglob("__pycache__"))
            
            for cache_dir in cache_dirs:
                try:
                    shutil.rmtree(cache_dir)
                    self._log(f"   🗑️ Removido: {cache_dir.relative_to(self.pasta_base)}")
                except Exception as e:
                    self._log(f"   ⚠️ Erro ao remover {cache_dir}: {e}")
            
            self._log("✅ Cache limpo")
            return True
            
        except Exception as e:
            self._log(f"❌ Erro ao limpar cache: {e}")
            return False
    
    def _reinstalar_dependencias(self):
        """Reinstala dependências Python."""
        self._log("📦 Reinstalando dependências Python...")
        
        if not self.python_venv.exists():
            self._log("❌ Python portátil não encontrado!")
            return False
        
        dependencias = [
            "spotdl",
            "customtkinter", 
            "requests",
            "yt-dlp"
        ]
        
        for dep in dependencias:
            self._log(f"   📦 Instalando {dep}...")
            
            try:
                result = subprocess.run([
                    str(self.pip_venv), "install", "--upgrade", dep
                ], capture_output=True, text=True, timeout=180)
                
                if result.returncode == 0:
                    self._log(f"   ✅ {dep} instalado")
                else:
                    self._log(f"   ❌ Erro em {dep}: {result.stderr[:100]}...")
                    return False
                    
            except subprocess.TimeoutExpired:
                self._log(f"   ⚠️ Timeout na instalação de {dep}")
                return False
            except Exception as e:
                self._log(f"   ❌ Exceção em {dep}: {e}")
                return False
        
        self._log("✅ Dependências reinstaladas")
        return True
    
    def _reconfigurar_ambiente(self):
        """Reconfigura ambiente."""
        self._log("⚙️ Reconfigurando ambiente...")
        
        try:
            # Testar SpotDL
            self._log("   🎵 Testando SpotDL...")
            result = subprocess.run([
                str(self.python_venv), "-m", "spotdl", "--version"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                versao = result.stdout.strip()
                self._log(f"   ✅ SpotDL funcionando: {versao}")
            else:
                self._log(f"   ❌ SpotDL com problema: {result.stderr}")
                return False
            
            # Testar CustomTkinter
            self._log("   🖼️ Testando CustomTkinter...")
            result = subprocess.run([
                str(self.python_venv), "-c", "import customtkinter; print('CustomTkinter OK')"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                self._log("   ✅ CustomTkinter funcionando")
            else:
                self._log(f"   ❌ CustomTkinter com problema: {result.stderr}")
                return False
            
            self._log("✅ Ambiente reconfigurado")
            return True
            
        except Exception as e:
            self._log(f"❌ Erro na reconfiguração: {e}")
            return False
    
    def _reparo_sucesso(self):
        """Reparo concluído com sucesso."""
        messagebox.showinfo(
            "Reparo Concluído!",
            "✅ BaixaFy foi reparado com sucesso!\n\n"
            "Agora você pode tentar usar o BaixaFy normalmente.\n"
            "Execute 'BaixaFy.bat' para iniciar."
        )
    
    def _reparo_com_problemas(self):
        """Reparo com alguns problemas."""
        messagebox.showwarning(
            "Reparo Parcial",
            "⚠️ Reparo concluído com alguns problemas.\n\n"
            "Verifique o log acima para detalhes.\n"
            "Alguns recursos podem não funcionar corretamente."
        )
    
    def _reparo_erro(self, erro):
        """Erro no reparo."""
        messagebox.showerror(
            "Erro no Reparo",
            f"❌ Erro durante o reparo:\n\n{erro}\n\n"
            f"Verifique o log para mais detalhes."
        )
    
    def _finalizar_reparo(self):
        """Finaliza processo de reparo."""
        self.reparando = False
        self.btn_reparar.configure(state="normal", text="🔧 Iniciar Reparo")
        self.progresso.stop()
    
    def executar(self):
        """Executa o reparador."""
        self.root.mainloop()

def main():
    """Função principal."""
    try:
        reparador = ReparadorBaixaFy()
        reparador.executar()
    except Exception as e:
        print(f"Erro ao iniciar reparador: {e}")
        input("Pressione ENTER para fechar...")

if __name__ == "__main__":
    main()