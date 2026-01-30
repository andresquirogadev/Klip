# run_as_admin.bat - Ejecuta Klip como Administrador

@echo off
echo ================================================
echo Ejecutando Klip como Administrador
echo ================================================
echo.
echo Esto permite que Ctrl+1 funcione en SSMS y otras
echo aplicaciones que requieren privilegios elevados.
echo.

cd /d "%~dp0"

REM Verificar si Python está en el PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado en PATH
    echo.
    echo Intenta con la ruta completa de Python:
    echo D:\rEPOS\sql_snippet_dock\venv\Scripts\python.exe main.py
    pause
    exit /b 1
)

REM Ejecutar main.py como administrador
echo Iniciando Klip...
python main.py

pause
