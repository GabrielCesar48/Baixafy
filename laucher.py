"""
BaixaFy Desktop Launcher - Versão Simplificada
Inicia Django e abre navegador automaticamente
"""

import os
import sys
import time
import socket
import webbrowser
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


class BaixaFyLauncher:
    def __init__(self):
        self.django_process = None
        self.port = 8127  # Porta fixa para simplicidade
        
        # Determinar diretório base
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent
        
        self.django_dir = self.base_dir / 'django_app'
        
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baixafy.settings')
        sys.path.insert(0, str(self.django_dir))
        os.chdir(str(self.django_dir))
    
    def show_loading(self):
        """Mostra janela de loading"""
        self.root = tk.Tk()
        self.root.title("BaixaFy Desktop")
        self.root.geometry("350x150")
        self.root.eval('tk::PlaceWindow . center')
        
        # Título
        title = tk.Label(self.root, text="🎵 BaixaFy Desktop", 
                        font=('Arial', 16, 'bold'), fg='#1DB954')
        title.pack(pady=20)
        
        # Status
        self.status_label = tk.Label(self.root, text="Iniciando aplicação...", 
                                   font=('Arial', 10))
        self.status_label.pack(pady=10)
        
        self.root.update()
    
    def update_status(self, message):
        """Atualiza status"""
        self.status_label.config(text=message)
        self.root.update()
    
    def check_port(self):
        """Verifica se porta está livre"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', self.port))
                return True
        except:
            return False
    
    def start_django(self):
        """Inicia servidor Django"""
        try:
            # Executar migrações primeiro
            self.update_status("Configurando banco de dados...")
            subprocess.run([sys.executable, 'manage.py', 'migrate', '--verbosity=0'], 
                         check=True, cwd=str(self.django_dir))
            
            # Iniciar servidor
            self.update_status(f"Iniciando servidor na porta {self.port}...")
            
            self.django_process = subprocess.Popen([
                sys.executable, 'manage.py', 'runserver', f'127.0.0.1:{self.port}', '--noreload'
            ], cwd=str(self.django_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Aguardar servidor iniciar
            self.update_status("Aguardando servidor...")
            for i in range(15):  # 15 segundos máximo
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        if s.connect_ex(('127.0.0.1', self.port)) == 0:
                            return True
                except:
                    pass
                time.sleep(1)
            
            return False
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar Django:\n{str(e)}")
            return False
    
    def open_browser(self):
        """Abre navegador"""
        self.update_status("Abrindo navegador...")
        url = f"http://127.0.0.1:{self.port}"
        
        try:
            webbrowser.open(url)
            time.sleep(2)
            return True
        except:
            messagebox.showerror("Erro", f"Erro ao abrir navegador.\nAcesse manualmente: {url}")
            return False
    
    def show_control_window(self):
        """Mostra janela de controle"""
        # Fechar janela de loading
        self.root.destroy()
        
        # Criar janela de controle
        control = tk.Tk()
        control.title("BaixaFy Desktop - Controle")
        control.geometry("300x120")
        control.eval('tk::PlaceWindow . center')
        
        # Status
        status = tk.Label(control, text=f"🟢 Rodando em localhost:{self.port}", 
                         font=('Arial', 10))
        status.pack(pady=10)
        
        # Botões
        btn_frame = tk.Frame(control)
        btn_frame.pack(pady=10)
        
        open_btn = tk.Button(btn_frame, text="Abrir Navegador", 
                           command=lambda: webbrowser.open(f"http://127.0.0.1:{self.port}"),
                           bg='#1DB954', fg='white')
        open_btn.pack(side='left', padx=5)
        
        close_btn = tk.Button(btn_frame, text="Fechar", 
                            command=control.quit,
                            bg='#ff4444', fg='white')
        close_btn.pack(side='right', padx=5)
        
        control.protocol("WM_DELETE_WINDOW", control.quit)
        control.mainloop()
    
    def cleanup(self):
        """Limpa recursos"""
        if self.django_process:
            try:
                self.django_process.terminate()
                time.sleep(2)
                if self.django_process.poll() is None:
                    self.django_process.kill()
            except:
                pass
    
    def run(self):
        """Executa launcher"""
        try:
            # 1. Mostrar loading
            self.show_loading()
            
            # 2. Verificar porta
            if not self.check_port():
                messagebox.showerror("Erro", f"Porta {self.port} já está em uso.")
                return False
            
            # 3. Iniciar Django
            if not self.start_django():
                messagebox.showerror("Erro", "Falha ao iniciar servidor Django.")
                return False
            
            # 4. Abrir navegador
            self.open_browser()
            
            # 5. Mostrar controle
            messagebox.showinfo("BaixaFy Desktop", 
                              f"✅ BaixaFy iniciado com sucesso!\n\n"
                              f"URL: http://127.0.0.1:{self.port}\n"
                              f"Feche esta janela para encerrar.")
            
            self.show_control_window()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Erro Fatal", f"Erro inesperado:\n{str(e)}")
            return False
        finally:
            self.cleanup()


def main():
    launcher = BaixaFyLauncher()
    
    try:
        launcher.run()
    except KeyboardInterrupt:
        print("\nEncerrando BaixaFy Desktop...")
    finally:
        launcher.cleanup()


if __name__ == "__main__":
    main()