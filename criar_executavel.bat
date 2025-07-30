@echo off
echo ========================================
echo    BAIXAFY - CRIADOR DE EXECUTAVEL
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale Python em: https://python.org
    pause
    exit /b 1
)

echo.
echo [2/4] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo [3/4] Criando executavel com PyInstaller...
pyinstaller --onefile --windowed --name "BaixaFy" --icon=baixafy_icon.ico baixar.py
if errorlevel 1 (
    echo AVISO: Executavel criado sem icone (baixafy_icon.ico nao encontrado)
    pyinstaller --onefile --windowed --name "BaixaFy" baixar.py
)

echo.
echo [4/4] Organizando arquivos...
if exist "dist\BaixaFy.exe" (
    copy "dist\BaixaFy.exe" "BaixaFy.exe"
    echo.
    echo ========================================
    echo   SUCESSO! EXECUTAVEL CRIADO!
    echo ========================================
    echo.
    echo Arquivo: BaixaFy.exe
    echo Tamanho: 
    dir "BaixaFy.exe" | find "BaixaFy.exe"
    echo.
    echo COMO USAR:
    echo 1. Execute BaixaFy.exe
    echo 2. Cole link do Spotify
    echo 3. Clique em "Pesquisar Musicas"
    echo 4. Selecione as musicas desejadas
    echo 5. Clique em "Baixar Musicas Selecionadas"
    echo.
    echo OBSERVACAO:
    echo - Certifique-se que spotDL esta instalado
    echo - Execute: pip install spotdl
    echo.
) else (
    echo ERRO: Falha ao criar executavel!
    echo Verifique os erros acima.
)

echo.
echo Limpando arquivos temporarios...
rmdir /s /q build 2>nul
rmdir /s /q __pycache__ 2>nul

echo.
echo Pressione qualquer tecla para fechar...
pause >nul