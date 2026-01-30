# install_service.py - Instalador para inicio automático con Windows

import os
import sys
import winreg
import subprocess

def add_to_startup():
    """Agregar SQL Snippet Dock al inicio automático de Windows."""
    
    try:
        # Obtener ruta del script de inicio
        current_dir = os.path.dirname(os.path.abspath(__file__))
        start_script = os.path.join(current_dir, "start_service.py")
        
        # Crear comando para ejecutar en modo servicio automáticamente
        command = f'"{sys.executable}" "{start_script}" --auto'
        
        # Agregar al registro de Windows para inicio automático
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.SetValueEx(
            key,
            "SQLSnippetDock",
            0,
            winreg.REG_SZ,
            command
        )
        
        winreg.CloseKey(key)
        
        print("✅ SQL Snippet Dock agregado al inicio automático de Windows")
        print("   Se iniciará automáticamente cuando arranque el sistema")
        print("   Para quitar del inicio, ejecute: python install_service.py --remove")
        
        return True
        
    except Exception as e:
        print(f"❌ Error agregando al inicio: {e}")
        return False

def remove_from_startup():
    """Quitar SQL Snippet Dock del inicio automático."""
    
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        winreg.DeleteValue(key, "SQLSnippetDock")
        winreg.CloseKey(key)
        
        print("✅ SQL Snippet Dock quitado del inicio automático")
        return True
        
    except FileNotFoundError:
        print("ℹ️  SQL Snippet Dock no estaba en el inicio automático")
        return True
    except Exception as e:
        print(f"❌ Error quitando del inicio: {e}")
        return False

def main():
    """Función principal del instalador."""
    
    if len(sys.argv) > 1 and sys.argv[1] == "--remove":
        print("🗑️  Quitando del inicio automático...")
        remove_from_startup()
    else:
        print("⚙️  Instalando en inicio automático...")
        
        # Verificar que existe session.json (usuario ya hizo login)
        if not os.path.exists("session.json"):
            print("❌ Error: Debe hacer login primero")
            print("   Ejecute: python main.py")
            print("   Luego ejecute este instalador nuevamente")
            return
        
        if add_to_startup():
            print("\n🚀 ¿Quiere iniciar el servicio ahora? (y/n): ", end="")
            respuesta = input().lower()
            
            if respuesta in ['y', 'yes', 's', 'si', '']:
                print("Iniciando servicio...")
                from start_service import start_background_service
                start_background_service()

if __name__ == "__main__":
    main()