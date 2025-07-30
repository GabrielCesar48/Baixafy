@echo off
echo ========================================
echo    BAIXAFY - CRIADOR DE INSTALADOR
echo ========================================
echo.

echo [INFO] Este script cria um instalador completo do BaixaFy
echo [INFO] O instalador resultante funciona em qualquer PC Windows
echo [INFO] Nao precisa ter Python instalado no PC de destino
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
echo [2/4] Instalando dependencias do instalador...
pip install pyinstaller pywin32
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo [3/4] Criando instalador executavel...
pyinstaller --onefile --windowed --name "BaixaFy-Installer" --icon=installer_icon.ico instalador_baixafy.py
if errorlevel 1 (
    echo AVISO: Instalador criado sem icone
    pyinstaller --onefile --windowed --name "BaixaFy-Installer" instalador_baixafy.py
)

echo.
echo [4/4] Organizando arquivos...
if exist "dist\BaixaFy-Installer.exe" (
    copy "dist\BaixaFy-Installer.exe" "BaixaFy-Installer.exe"
    echo.
    echo ========================================
    echo   INSTALADOR CRIADO COM SUCESSO!
    echo ========================================
    echo.
    echo Arquivo: BaixaFy-Installer.exe
    echo.
    echo COMO USAR:
    echo 1. Copie BaixaFy-Installer.exe para qualquer PC Windows
    echo 2. Execute como Administrador (clique direito - "Executar como administrador")
    echo 3. Clique "Instalar BaixaFy"
    echo 4. Aguarde a instalacao automatica
    echo 5. Use o atalho "BaixaFy" no Desktop
    echo.
    echo OBSERVACOES IMPORTANTES:
    echo - O instalador baixa e instala Python automaticamente
    echo - Funciona mesmo em PCs sem Python
    echo - Instala tudo em C:\BaixaFy
    echo - Cria atalhos automaticamente
    echo - Cerca de 500MB de download durante instalacao
    echo.
) else (
    echo ERRO: Falha ao criar instalador!
    echo Verifique os erros acima.
)

echo.
echo Limpando arquivos temporarios...
rmdir /s /q build 2>nul
rmdir /s /q __pycache__ 2>nul

echo.
echo Pressione qualquer tecla para fechar...
pause >nul