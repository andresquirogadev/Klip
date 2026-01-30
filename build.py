# build.py - Script para compilar SQL Snippet Dock en un ejecutable portable

import os
import subprocess
import sys

def build_executable():
    """Compila la aplicación en un ejecutable portable usando PyInstaller"""

    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",  # Crear un solo archivo ejecutable
        "--windowed",  # No mostrar consola (aplicación GUI)
        "--name=SQL_Snippet_Dock",  # Nombre del ejecutable
        # "--icon=icon.ico",  # Icono (si existe)
        "--add-data=sql_snippets.json;.",  # Incluir archivo de datos
        "--add-data=config.json;.",  # Incluir configuración
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=supabase",
        "--hidden-import=keyboard",
        "--hidden-import=pyautogui",
        "--hidden-import=pyperclip",
        "--hidden-import=json",
        "main.py"
    ]

    print("Compilando SQL Snippet Dock...")
    print("Comando:", " ".join(cmd))

    try:
        # Ejecutar PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("¡Compilación exitosa!")
        print("El ejecutable se encuentra en: dist/SQL_Snippet_Dock.exe")

        # Crear archivo ZIP portable
        print("\nCreando archivo ZIP portable...")
        import zipfile
        import shutil

        exe_path = "dist/SQL_Snippet_Dock.exe"
        zip_path = "SQL_Snippet_Dock_Portable.zip"

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(exe_path, "SQL_Snippet_Dock.exe")

            # Incluir archivos de datos si existen
            for file in ["sql_snippets.json", "config.json"]:
                if os.path.exists(file):
                    zipf.write(file, file)

        print(f"Archivo portable creado: {zip_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error durante la compilación: {e}")
        print("Salida de error:", e.stderr)
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

    return True

def build_portable_directory():
    """Crea un directorio portable con todos los archivos necesarios"""

    cmd = [
        "pyinstaller",
        "--onedir",  # Crear directorio con archivos separados
        "--windowed",  # No mostrar consola
        "--name=SQL_Snippet_Dock",
        "--add-data=sql_snippets.json;.",
        "--add-data=config.json;.",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=supabase",
        "--hidden-import=keyboard",
        "--hidden-import=pyautogui",
        "--hidden-import=pyperclip",
        "--hidden-import=json",
        "main.py"
    ]

    print("Creando directorio portable...")
    print("Comando:", " ".join(cmd))

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("¡Directorio portable creado exitosamente!")
        print("Los archivos se encuentran en: dist/SQL_Snippet_Dock/")

        # Crear ZIP del directorio
        import shutil
        zip_path = "SQL_Snippet_Dock_Portable_Dir.zip"
        shutil.make_archive("SQL_Snippet_Dock_Portable_Dir", 'zip', "dist/SQL_Snippet_Dock")
        print(f"Archivo ZIP del directorio creado: {zip_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error durante la creación del directorio: {e}")
        print("Salida de error:", e.stderr)
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

    return True

if __name__ == "__main__":
    print("SQL Snippet Dock - Generador de Ejecutable Portable")
    print("=" * 50)

    # Verificar si PyInstaller está instalado
    try:
        import PyInstaller
        print("✓ PyInstaller encontrado")
    except ImportError:
        print("✗ PyInstaller no encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✓ PyInstaller instalado")

    # Preguntar tipo de compilación
    print("\nOpciones de compilación:")
    print("1. Ejecutable único (recomendado)")
    print("2. Directorio portable")

    choice = input("\nSeleccione opción (1 o 2): ").strip()

    if choice == "1":
        success = build_executable()
    elif choice == "2":
        success = build_portable_directory()
    else:
        print("Opción inválida")
        success = False

    if success:
        print("\n🎉 ¡Compilación completada exitosamente!")
        print("\nPara ejecutar la aplicación:")
        print("- Si elegiste opción 1: Ejecuta SQL_Snippet_Dock.exe")
        print("- Si elegiste opción 2: Ejecuta SQL_Snippet_Dock/SQL_Snippet_Dock.exe")
        print("\nLos archivos portables están listos para distribuir.")
    else:
        print("\n❌ Error durante la compilación.")
        print("Verifica que todas las dependencias estén instaladas correctamente.")