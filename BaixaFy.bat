@echo off
REM ===============================================
REM BaixaFy - Baixador de Músicas do Spotify  
REM Launcher Principal para Windows
REM ===============================================

setlocal enabledelayedexpansion

REM Configurar codepage UTF-8 para caracteres especiais
chcp 65001 >nul 2>&1

REM Definir pasta atual como base
set "PASTA_BASE=%~dp0"
cd /d "%PASTA_BASE%"

REM Configurar título da janela
title BaixaFy - Baixador de Músicas do Spotify

echo.
echo ===============================================
echo 🎵 BaixaFy - Baixador de Músicas do Spotify
echo ===============================================
echo.
echo ⏳ Iniciando BaixaFy...
echo 📁 Pasta: %PASTA_BASE%
echo.

REM Verificar se arquivos principais existem
if not exist "BaixaFy_Launcher.py" (
    echo ❌ ERRO: Arquivo BaixaFy_Launcher.py não encontrado!
    echo.
    echo 📋 Certifique-se que todos os arquivos foram extraídos
    echo    na mesma pasta.
    echo.
    pause
    exit /b 1
)

if not exist "venv_portable\Scripts\python.exe" (
    echo ❌ ERRO: Python portátil não encontrado!
    echo.
    echo 📋 Pasta esperada: venv_portable\Scripts\python.exe
    echo.
    echo 💡 Possíveis soluções:
    echo    • Re-extrair todos os arquivos do BaixaFy
    echo    • Verificar se pasta venv_portable existe
    echo.
    pause
    exit /b 1
)

REM Adicionar FFmpeg ao PATH se existir
if exist "ffmpeg-7.1.1\bin" (
    set "PATH=%PASTA_BASE%ffmpeg-7.1.1\bin;%PATH%"
    echo ✅ FFmpeg configurado
)

echo ✅ Arquivos encontrados
echo ⚡ Executando BaixaFy...
echo.

REM Executar launcher Python com tratamento de erro
"%PASTA_BASE%venv_portable\Scripts\python.exe" "%PASTA_BASE%BaixaFy_Launcher.py"

REM Verificar código de saída
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ BaixaFy encerrou com erro (código: %ERRORLEVEL%)
    echo.
    echo 🔍 Deseja executar diagnóstico? (s/n)
    set /p "resposta="
    
    if /i "!resposta!"=="s" (
        if exist "launcher_debug.py" (
            echo.
            echo 🔍 Executando diagnóstico...
            "%PASTA_BASE%venv_portable\Scripts\python.exe" "%PASTA_BASE%launcher_debug.py"
        ) else (
            echo ❌ Arquivo de diagnóstico não encontrado!
        )
    )
    
    echo.
    pause
    exit /b %ERRORLEVEL%
)

REM Sucesso - sair silenciosamente
exit /b 0