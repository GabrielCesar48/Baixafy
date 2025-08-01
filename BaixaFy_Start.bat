@echo off
title BaixaFy - Baixador do Spotify
cd /d "%~dp0"

echo.
echo ================================================
echo            🎵 BaixaFy Iniciando... 🎵
echo ================================================
echo.

REM Verificar se arquivos existem
if not exist "venv_portable\Scripts\python.exe" (
    echo ❌ Venv não encontrado! Certifique-se que está na pasta correta.
    pause
    exit /b 1
)

if not exist "baixafy_interface.py" (
    echo ❌ Interface não encontrada! Certifique-se que baixafy_interface.py existe.
    pause
    exit /b 1
)

if not exist "ffmpeg-7.1.1\bin\ffmpeg.exe" (
    echo ❌ FFmpeg não encontrado! Certifique-se que ffmpeg-7.1.1\bin\ffmpeg.exe existe.
    pause
    exit /b 1
)

echo ✅ Arquivos encontrados!
echo 🔧 Configurando ambiente...

REM Adicionar FFmpeg ao PATH
set PATH=%~dp0ffmpeg-7.1.1\bin;%PATH%

REM Configurar variáveis TCL/TK (caso necessário)
set TCL_LIBRARY=%~dp0python\tcl\tcl8.6
set TK_LIBRARY=%~dp0python\tcl\tk8.6

echo 🐍 Ativando venv...
call venv_portable\Scripts\activate.bat

echo 🚀 Iniciando BaixaFy...
echo.

REM Executar interface
python baixafy_interface.py

echo.
echo 👋 BaixaFy encerrado!
pause