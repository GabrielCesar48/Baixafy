#!/usr/bin/env python3
"""
BaixaFy Launcher Robusto - Versão para Distribuição
Configura ambiente e executa BaixaFy com tratamento de erros completo.
"""

import os
import sys
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import traceback

class BaixaFyLauncher:
    """Launcher robusto para BaixaFy."""
    
    def __init__(self):
        self.pasta_base = Path(__file__).parent.absolute()
        self.python_venv = self.pasta_base / "venv_portable" / "Scripts" / "python.exe"
        self.ffmpeg_path = self.pasta_base / "ffmpeg-7.1.1" / "bin"
        self.interface_script = self.pasta_base / "baixafy_interface.py"
        
    def mostrar_erro(self, titulo, mensagem):
        """Mostra erro usando messagebox se possível."""
        try:
            root = tk.Tk()
            root.withdraw()  # Esconder janela principal
            messagebox.showerror(titulo, mensagem)
            root.destroy()
        except:
            # Fallback para print se GUI não funcionar
            print(f"\n❌ {titulo}")
            print("="*50)
            print(mensagem)
            print("="*50)
            input("Pressione ENTER para fechar...")
    
    def mostrar_info(self, titulo, mensagem):
        """Mostra informação usando messagebox se possível."""
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(titulo, mensagem)
            root.destroy()
        except:
            print(f"\n✅ {titulo}")
            print(mensagem)
    
    def verificar_estrutura(self):
        """Verifica se estrutura de arquivos está correta."""
        arquivos_necessarios = [
            ("Python Portátil", self.python_venv),
            ("Interface BaixaFy", self.interface_script),
            ("FFmpeg", self.ffmpeg_path / "ffmpeg.exe")
        ]
        
        for nome, caminho in arquivos_necessarios:
            if not caminho.exists():
                self.mostrar_erro(
                    "Arquivos Faltando",
                    f"❌ {nome} não encontrado!\n\n"
                    f"Arquivo esperado:\n{caminho}\n\n"
                    f"Certifique-se que todas as pastas do BaixaFy\n"
                    f"foram extraídas corretamente na mesma pasta."
                )
                return False
        
        return True
    
    def configurar_ambiente(self):
        """Configura variáveis de ambiente necessárias."""
        try:
            # Adicionar FFmpeg ao PATH
            current_path = os.environ.get('PATH', '')
            ffmpeg_path_str = str(self.ffmpeg_path)
            
            if ffmpeg_path_str not in current_path:
                os.environ['PATH'] = f"{ffmpeg_path_str}{os.pathsep}{current_path}"
            
            # Configurar pasta de trabalho
            os.chdir(str(self.pasta_base))
            
            return True
            
        except Exception as e:
            self.mostrar_erro(
                "Erro de Configuração",
                f"❌ Erro ao configurar ambiente:\n\n{str(e)}\n\n"
                f"Tente executar como Administrador."
            )
            return False
    
    def testar_python_venv(self):
        """Testa se Python virtual funciona."""
        try:
            result = subprocess.run(
                [str(self.python_venv), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.mostrar_erro(
                    "Python Virtual Env com Problema",
                    f"❌ Python portátil não está funcionando!\n\n"
                    f"Erro: {result.stderr}\n\n"
                    f"Possíveis soluções:\n"
                    f"• Re-extrair o BaixaFy em nova pasta\n"
                    f"• Executar como Administrador\n"
                    f"• Verificar antivírus"
                )
                return False
            
            return True
            
        except Exception as e:
            self.mostrar_erro(
                "Erro no Python",
                f"❌ Erro ao testar Python portátil:\n\n{str(e)}\n\n"
                f"O Python pode estar corrompido ou bloqueado.\n"
                f"Tente re-extrair o BaixaFy."
            )
            return False
    
    def testar_dependencias(self):
        """Testa dependências críticas."""
        dependencias = ["customtkinter", "spotdl"]
        
        for dep in dependencias:
            try:
                result = subprocess.run([
                    str(self.python_venv), "-c", f"import {dep}"
                ], capture_output=True, text=True, timeout=15)
                
                if result.returncode != 0:
                    self.mostrar_erro(
                        f"Dependência {dep} com Problema",
                        f"❌ A biblioteca {dep} não está funcionando!\n\n"
                        f"Erro: {result.stderr}\n\n"
                        f"O ambiente Python pode estar incompleto.\n"
                        f"Re-baixe o BaixaFy completo."
                    )
                    return False
                    
            except Exception as e:
                self.mostrar_erro(
                    f"Erro ao testar {dep}",
                    f"❌ Erro ao verificar {dep}:\n\n{str(e)}"
                )
                return False
        
        return True
    
    def executar_baixafy(self):
        """Executa a interface do BaixaFy."""
        try:
            # Executar BaixaFy
            processo = subprocess.Popen([
                str(self.python_venv),
                str(self.interface_script)
            ])
            
            # Aguardar um pouco para ver se inicia sem erro
            import time
            time.sleep(2)
            
            # Verificar se processo ainda está rodando
            if processo.poll() is None:
                # Processo ainda rodando = sucesso
                return True
            else:
                # Processo morreu rapidamente = erro
                self.mostrar_erro(
                    "BaixaFy Falhou ao Iniciar",
                    f"❌ BaixaFy fechou inesperadamente!\n\n"
                    f"Código de saída: {processo.returncode}\n\n"
                    f"Possíveis causas:\n"
                    f"• Erro no código Python\n"
                    f"• Dependência faltando\n"
                    f"• Problema de permissões\n\n"
                    f"Execute 'launcher_debug.py' para mais detalhes."
                )
                return False
                
        except Exception as e:
            self.mostrar_erro(
                "Erro ao Executar BaixaFy",
                f"❌ Erro ao iniciar BaixaFy:\n\n{str(e)}\n\n"
                f"Stack trace:\n{traceback.format_exc()}"
            )
            return False
    
    def executar(self):
        """Execução principal do launcher."""
        try:
            # Verificações em sequência
            if not self.verificar_estrutura():
                return False
            
            if not self.configurar_ambiente():
                return False
            
            if not self.testar_python_venv():
                return False
            
            if not self.testar_dependencias():
                return False
            
            # Tudo OK, executar BaixaFy
            if self.executar_baixafy():
                return True
            
            return False
            
        except Exception as e:
            self.mostrar_erro(
                "Erro Crítico do Launcher",
                f"❌ Erro inesperado no launcher:\n\n{str(e)}\n\n"
                f"Stack trace:\n{traceback.format_exc()}"
            )
            return False

def main():
    """Ponto de entrada principal."""
    launcher = BaixaFyLauncher()
    
    # Mostrar splash de início
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "BaixaFy Iniciando",
            "🎵 BaixaFy está iniciando...\n\n"
            "Verificando componentes...\n"
            "Aguarde alguns segundos."
        )
        root.destroy()
    except:
        print("🎵 BaixaFy iniciando...")
    
    # Executar launcher
    sucesso = launcher.executar()
    
    if not sucesso:
        # Se falhou, oferecer diagnóstico
        try:
            root = tk.Tk() 
            root.withdraw()
            resposta = messagebox.askyesno(
                "BaixaFy - Problema Detectado",
                "❌ BaixaFy não conseguiu iniciar corretamente.\n\n"
                "Deseja executar o diagnóstico automático\n"
                "para identificar o problema?"
            )
            root.destroy()
            
            if resposta:
                # Executar diagnóstico
                launcher_debug = launcher.pasta_base / "launcher_debug.py"
                if launcher_debug.exists():
                    subprocess.run([sys.executable, str(launcher_debug)])
                else:
                    messagebox.showerror(
                        "Diagnóstico não encontrado",
                        "Arquivo launcher_debug.py não encontrado.\n\n"
                        "Execute manualmente para diagnosticar problemas."
                    )
        except:
            print("❌ BaixaFy falhou ao iniciar. Execute launcher_debug.py para diagnosticar.")

if __name__ == "__main__":
    main()