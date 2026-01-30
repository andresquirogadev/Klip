# build_exe.py - Script para compilar a ejecutable con PyInstaller

import subprocess
import sys
import os
import shutil

def install_pyinstaller():
    """Instalar PyInstaller si no está disponible."""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
        return True
    except ImportError:
        print("📦 Instalando PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller instalado correctamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error instalando PyInstaller")
            return False

def create_spec_file():
    """Crear archivo .spec personalizado para PyInstaller."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui/*.py', 'ui'),
        ('core/*.py', 'core'),
        ('config.json', '.'),
        ('sql_snippets.json', '.'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets', 
        'PyQt6.QtGui',
        'supabase',
        'keyboard',
        'pyperclip',
        'pyautogui',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SQLSnippetDock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
'''
    
    with open('SQLSnippetDock.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Archivo .spec creado")

def create_version_info():
    """Crear información de versión para el ejecutable."""
    version_info = '''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'SQL Snippet Dock'),
        StringStruct(u'FileDescription', u'Administrador de Snippets SQL'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'SQLSnippetDock'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025'),
        StringStruct(u'OriginalFilename', u'SQLSnippetDock.exe'),
        StringStruct(u'ProductName', u'SQL Snippet Dock'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("✅ Información de versión creada")

def create_icon():
    """Crear un icono simple si no existe."""
    if not os.path.exists('icon.ico'):
        print("⚠️  No se encontró icon.ico - el ejecutable no tendrá icono personalizado")
        return False
    else:
        print("✅ Icono encontrado")
        return True

def build_executable():
    """Compilar el ejecutable."""
    print("🔨 Compilando ejecutable...")
    
    try:
        # Limpiar build anterior
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        # Compilar usando el archivo .spec
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "SQLSnippetDock.spec"]
        
        print("📝 Ejecutando:", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Compilación exitosa")
            
            # Verificar que el ejecutable se creó
            exe_path = os.path.join('dist', 'SQLSnippetDock.exe')
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"📦 Ejecutable creado: {exe_path}")
                print(f"📏 Tamaño: {size_mb:.1f} MB")
                return exe_path
            else:
                print("❌ Ejecutable no encontrado después de la compilación")
                return None
        else:
            print("❌ Error en la compilación:")
            print(result.stdout)
            print(result.stderr)
            return None
            
    except Exception as e:
        print(f"❌ Error durante la compilación: {e}")
        return None

def create_silent_installer():
    """Crear instalador silencioso para el ejecutable."""
    installer_content = '''@echo off
REM Instalador silencioso de SQL Snippet Dock

echo Instalando SQL Snippet Dock en modo silencioso...

REM Crear directorio en Program Files
set "INSTALL_DIR=%LOCALAPPDATA%\\SQLSnippetDock"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copiar ejecutable
copy /Y "SQLSnippetDock.exe" "%INSTALL_DIR%\\"
if errorlevel 1 (
    echo Error copiando ejecutable
    exit /b 1
)

REM Agregar al registro para inicio automático
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "SQLSnippetDock" /t REG_SZ /d "\\"%INSTALL_DIR%\\SQLSnippetDock.exe\\" --service --auto" /f >nul 2>&1

if errorlevel 1 (
    echo Error agregando al inicio automatico
    exit /b 1
)

echo SQL Snippet Dock instalado correctamente
echo Se iniciara automaticamente con Windows
echo.
echo Presiona cualquier tecla para iniciar ahora...
pause >nul

REM Iniciar en modo servicio
start "" "%INSTALL_DIR%\\SQLSnippetDock.exe" --service --auto

echo Servicio iniciado en segundo plano
echo Usa F12 para abrir el selector de snippets
'''
    
    with open('install_silent.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("✅ Instalador silencioso creado: install_silent.bat")

def main():
    """Función principal de compilación."""
    print("🚀 Preparando compilación de SQL Snippet Dock")
    print("=" * 50)
    
    # Verificar Python environment
    if not sys.executable:
        print("❌ No se pudo detectar el intérprete de Python")
        return False
    
    print(f"🐍 Python: {sys.executable}")
    print(f"📁 Directorio: {os.getcwd()}")
    
    # Instalar PyInstaller
    if not install_pyinstaller():
        return False
    
    # Crear archivos necesarios
    create_spec_file()
    create_version_info()
    create_icon()
    
    # Compilar
    exe_path = build_executable()
    if not exe_path:
        return False
    
    # Crear instalador
    create_silent_installer()
    
    print("\n" + "=" * 50)
    print("✅ COMPILACIÓN COMPLETADA")
    print("=" * 50)
    print(f"📦 Ejecutable: {exe_path}")
    print("📋 Archivos generados:")
    print("   - SQLSnippetDock.exe (ejecutable principal)")
    print("   - install_silent.bat (instalador automático)")
    print()
    print("🎯 INSTRUCCIONES DE USO:")
    print("1. Ejecutar install_silent.bat como administrador")
    print("2. El programa se instalará y configurará automáticamente")
    print("3. Se iniciará en modo servicio sin notificaciones")
    print("4. Usar F12 para abrir selector de snippets")
    print()
    print("💡 El ejecutable se inicia automáticamente con Windows")
    print("   y funciona completamente en segundo plano")
    
    return True

if __name__ == "__main__":
    main()