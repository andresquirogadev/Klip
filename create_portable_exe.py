# create_portable_exe.py - Script completo para crear ejecutable portable

import os
import sys
import subprocess
import shutil
import json

def create_portable_config():
    """Crear configuración embebida para el ejecutable."""
    
    # Leer configuración actual
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró config.json")
        return False
    
    # Crear configuración embebida (sin credenciales sensibles)
    portable_config = {
        "supabase_url": config.get("supabase_url", ""),
        "supabase_key": config.get("supabase_key", ""),
        "hotkeys": config.get("hotkeys", {}),
        "is_portable": True,
        "auto_start": True
    }
    
    # Guardar configuración embebida
    with open('portable_config.json', 'w') as f:
        json.dump(portable_config, f, indent=2)
    
    print("✅ Configuración portable creada")
    return True

def install_dependencies():
    """Instalar todas las dependencias necesarias."""
    print("📦 Instalando dependencias...")
    
    try:
        # Instalar desde requirements.txt
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependencias instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def create_startup_script():
    """Crear script de inicio para el ejecutable."""
    
    startup_content = '''# startup_embedded.py - Script de inicio embebido para ejecutable

import os
import sys
import json
import winreg
from pathlib import Path

def setup_portable_environment():
    """Configurar entorno portable al primer inicio."""
    
    # Obtener directorio del ejecutable
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
    else:
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Crear directorio de datos de usuario
    user_data_dir = os.path.join(os.environ['APPDATA'], 'SQLSnippetDock')
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Copiar configuración embebida si no existe
    user_config = os.path.join(user_data_dir, 'config.json')
    if not os.path.exists(user_config):
        embedded_config = os.path.join(exe_dir, 'portable_config.json')
        if os.path.exists(embedded_config):
            with open(embedded_config, 'r') as f:
                config = json.load(f)
            
            with open(user_config, 'w') as f:
                json.dump(config, f, indent=2)
    
    return user_data_dir

def add_to_startup():
    """Agregar ejecutable al inicio automático de Windows."""
    
    try:
        # Obtener ruta del ejecutable
        exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
        
        # Agregar al registro
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(
            key,
            "SQLSnippetDock",
            0,
            winreg.REG_SZ,
            f'"{exe_path}"'
        )
        
        winreg.CloseKey(key)
        return True
        
    except Exception:
        return False

def main():
    """Configuración inicial del ejecutable portable."""
    
    # Configurar entorno
    user_data_dir = setup_portable_environment()
    
    # Agregar al inicio automático
    add_to_startup()
    
    # Cambiar directorio de trabajo
    os.chdir(user_data_dir)
    
    return True

if __name__ == "__main__":
    main()
'''
    
    with open('startup_embedded.py', 'w', encoding='utf-8') as f:
        f.write(startup_content)
    
    print("✅ Script de inicio embebido creado")

def build_portable_exe():
    """Compilar ejecutable portable con PyInstaller."""
    
    print("🔨 Compilando ejecutable portable...")
    
    # Crear archivo .spec personalizado para portable
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['{os.getcwd()}'],
    binaries=[],
    datas=[
        ('ui', 'ui'),
        ('core', 'core'),
        ('portable_config.json', '.'),
        ('startup_embedded.py', '.'),
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
        'winreg',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy'],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=False,
)
'''
    
    with open('SQLSnippetDock_Portable.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    try:
        # Limpiar builds anteriores
        for folder in ['build', 'dist']:
            if os.path.exists(folder):
                shutil.rmtree(folder)
        
        # Compilar
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "SQLSnippetDock_Portable.spec"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            exe_path = os.path.join('dist', 'SQLSnippetDock.exe')
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"✅ Ejecutable portable creado: {exe_path}")
                print(f"📏 Tamaño: {size_mb:.1f} MB")
                return exe_path
        
        print("❌ Error en la compilación:")
        print(result.stdout)
        print(result.stderr)
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Función principal."""
    
    print("🚀 CREANDO EJECUTABLE PORTABLE DE SQL SNIPPET DOCK")
    print("=" * 60)
    
    # Verificar archivos necesarios
    required_files = ['main.py', 'config.json']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Archivo requerido no encontrado: {file}")
            return False
    
    # Preparar archivos
    if not create_portable_config():
        return False
    
    create_startup_script()
    
    # Instalar dependencias
    if not install_dependencies():
        return False
    
    # Compilar
    exe_path = build_portable_exe()
    if not exe_path:
        return False
    
    print("\n" + "=" * 60)
    print("✅ EJECUTABLE PORTABLE COMPLETADO")
    print("=" * 60)
    print(f"📦 Archivo: {exe_path}")
    print()
    print("🎯 CARACTERÍSTICAS:")
    print("   ✅ Inicia automáticamente con Windows (sin notificación)")
    print("   ✅ Funciona completamente en segundo plano")
    print("   ✅ Hotkeys globales: F12 y Ctrl+Shift+S")
    print("   ✅ No requiere instalación")
    print("   ✅ Configuración embebida")
    print()
    print("📋 INSTRUCCIONES:")
    print("1. Copiar SQLSnippetDock.exe a cualquier ubicación")
    print("2. Ejecutar una vez para configurar inicio automático")
    print("3. El programa funciona silenciosamente en segundo plano")
    print("4. Usar F12 para abrir selector de snippets")
    
    return True

if __name__ == "__main__":
    main()