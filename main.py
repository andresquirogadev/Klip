# main.py

import sys
import pyperclip
import keyboard
import pyautogui
import threading
import os
import subprocess
import time
from supabase import create_client, Client
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QShortcut, QKeySequence, QIcon, QPixmap, QAction
from ui.overlay import SnippetOverlay, FloatingIcon, SnippetDialog, LoginDialog, NumberSelector
from simple_selector import SimpleSelector
from core.manager import add_snippet, search_snippets

# Import security module
try:
    from security import _security_manager, detect_debugger, verify_environment
    SECURITY_ENABLED = True
except ImportError:
    print("⚠ Security module not available. Running in development mode.")
    SECURITY_ENABLED = False


# Configuración de Supabase (cargar desde config.json si existe)
SUPABASE_URL = "https://riuailqsymlzpheojjps.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpdWFpbHFzeW1senBoZW9qanBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI2MDc0MjUsImV4cCI6MjA3ODE4MzQyNX0.p2yHf7blyfdU6CUhGIA9Y66LGDBnn4wBP1uRVcgojjE"

import json
try:
    with open("config.json", "r") as f:
        config = json.load(f)
        SUPABASE_URL = config.get("supabase_url", SUPABASE_URL)
        SUPABASE_KEY = config.get("supabase_key", SUPABASE_KEY)
except FileNotFoundError:
    pass

# Variables globales para detección de doble Ctrl
last_ctrl_time = 0
DOUBLE_CLICK_TIME = 0.3  # 300ms para doble click
number_selector = None

# Variables para proteger el proceso de guardado
saving_in_progress = False
original_clipboard_content = ""

# Cargar configuración de hotkeys
HOTKEY_CONFIG = {}
try:
    with open("config.json", "r") as f:
        config = json.load(f)
        HOTKEY_CONFIG = config.get("hotkeys", {})
except FileNotFoundError:
    pass


class SignalEmitter(QObject):
    save_selection_signal = pyqtSignal()
    show_selector_signal = pyqtSignal()


class SystemTrayManager:
    def __init__(self, app, on_config, on_snippet, on_selector, on_logout, on_close):
        self.app = app
        self.on_config = on_config
        self.on_snippet = on_snippet  
        self.on_selector = on_selector
        self.on_logout = on_logout
        self.on_close = on_close
        
        # Crear ícono para el system tray
        self.tray_icon = QSystemTrayIcon()
        
        # Cargar ícono personalizado o usar uno por defecto
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            # Fallback: crear un ícono simple (azul para SQL)
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.GlobalColor.blue)
            icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
        
        # Guardar el ícono para uso en ventanas
        self.app_icon = icon
        
        # Crear menú contextual
        self.tray_menu = QMenu()
        
        # Agregar acciones al menú
        selector_action = QAction("🔢 Quick Selector (F12)", self.tray_menu)
        selector_action.triggered.connect(self.on_selector)
        self.tray_menu.addAction(selector_action)
        
        self.tray_menu.addSeparator()
        
        config_action = QAction("⚙️ Settings", self.tray_menu)
        config_action.triggered.connect(self.on_config)
        self.tray_menu.addAction(config_action)
        
        snippet_action = QAction("📄 Snippets", self.tray_menu)
        snippet_action.triggered.connect(self.on_snippet)
        self.tray_menu.addAction(snippet_action)
        
        self.tray_menu.addSeparator()
        
        logout_action = QAction("🚪 Logout", self.tray_menu)
        logout_action.triggered.connect(self.on_logout)
        self.tray_menu.addAction(logout_action)
        
        close_action = QAction("❌ Exit", self.tray_menu)
        close_action.triggered.connect(self.on_close)
        self.tray_menu.addAction(close_action)
        
        # Asignar el menú al ícono
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Configurar tooltip
        self.tray_icon.setToolTip("Klip")
        
        # Mostrar el ícono en el system tray
        self.tray_icon.show()
        
    def hide(self):
        self.tray_icon.hide()
        
    def show(self):
        self.tray_icon.show()


def on_snippet_selected(name: str, code: str, overlay: SnippetOverlay, icon=None):
    """Copia el snippet seleccionado al portapapeles y lo pega automáticamente."""
    try:
        pyperclip.copy(code)
        print(f"\n✅ Snippet '{name}' copied to clipboard.\n")
        
        # Pegar automáticamente
        import time
        time.sleep(0.05)  # Pequeño delay para asegurar que el clipboard se actualice
        
        # Simular Ctrl+V para pegar
        pyautogui.keyDown('ctrl')
        time.sleep(0.01)
        pyautogui.press('v')
        time.sleep(0.01)
        pyautogui.keyUp('ctrl')
        
        print(f"✅ Snippet '{name}' pasted automatically.\n")
        
    except Exception as e:
        print(f"❌ Error copying/pasting: {e}")


def on_icon_clicked(overlay: SnippetOverlay):
    """Muestra la ventana de overlay cuando se hace clic en el icono."""
    overlay.show_centered()
    overlay.raise_()
    overlay.activateWindow()


def on_save_selection(overlay: SnippetOverlay):
    """Guarda la selección actual como snippet."""
    global saving_in_progress, original_clipboard_content
    
    # Evitar múltiples ejecuciones simultáneas
    if saving_in_progress:
        print("⚠️ [DEBUG] Guardado ya en progreso, ignorando...")
        return
    
    saving_in_progress = True
    print("🔧 [DEBUG] on_save_selection llamado")
    
    try:
        # Verificar límite de snippets primero
        from core.manager import can_add_more_snippets, get_snippets_limit_info
        
        print(f"🔧 [DEBUG] Verificando límite de snippets...")
        if not can_add_more_snippets():
            print(f"⚠️ [DEBUG] Límite alcanzado: {get_snippets_limit_info()}")
            msg = QMessageBox()
            msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            msg.setIcon(QMessageBox.Icon.Warning)
            # Agregar icono de la app
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
            if os.path.exists(icon_path):
                msg.setWindowIcon(QIcon(icon_path))
            msg.setWindowTitle("Snippet Limit Reached")
            msg.setText(f"You have reached the snippet limit ({get_snippets_limit_info()}).\n\nUpgrade to Premium for unlimited snippets!")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return
        
        # Guardar contenido actual del portapapeles
        original_clipboard_content = pyperclip.paste()
        print(f"🔧 [DEBUG] Contenido original del portapapeles guardado (largo: {len(original_clipboard_content)})")
        
        # Simular Ctrl+C para copiar el texto seleccionado (con reintentos)
        max_retries = 3
        selected_text = None
        
        for attempt in range(max_retries):
            print(f"🔧 [DEBUG] Intento {attempt + 1} de simular Ctrl+C...")
            
            # Simular Ctrl+C
            pyautogui.keyDown('ctrl')
            time.sleep(0.05)  # Aumentar delay
            pyautogui.press('c')
            time.sleep(0.05)
            pyautogui.keyUp('ctrl')
            
            # Esperar a que se copie
            time.sleep(0.2)
            
            # Leer el nuevo contenido
            current_clipboard = pyperclip.paste()
            print(f"🔧 [DEBUG] Contenido actual del portapapeles (largo: {len(current_clipboard)})")
            
            # Verificar si cambió (es decir, se copió algo nuevo)
            if current_clipboard != original_clipboard_content:
                selected_text = current_clipboard.strip()
                print(f"🔧 [DEBUG] Texto seleccionado copiado exitosamente: '{selected_text[:50]}...'")
                break
            else:
                print(f"⚠️ [DEBUG] No se detectó cambio en el portapapeles, reintentando...")
                time.sleep(0.1)  # Esperar antes de reintentar
        
        # Restaurar el portapapeles original
        pyperclip.copy(original_clipboard_content)
        print(f"🔧 [DEBUG] Portapapeles restaurado")
        
        if not selected_text:
            print(f"⚠️ [DEBUG] No se pudo copiar texto seleccionado después de {max_retries} intentos")
            msg = QMessageBox()
            msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            msg.setIcon(QMessageBox.Icon.Information)
            # Agregar icono de la app
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
            if os.path.exists(icon_path):
                msg.setWindowIcon(QIcon(icon_path))
            msg.setWindowTitle("Save Snippet")
            msg.setText("No text selected or unable to copy. Make sure you have text selected in another application.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return
        
        print(f"🔧 [DEBUG] Abriendo diálogo para guardar...")
        dialog = SnippetDialog(None, "", selected_text)
        print(f"🔧 [DEBUG] Diálogo creado, mostrando...")
        result = dialog.exec()
        print(f"🔧 [DEBUG] Diálogo cerrado con resultado: {result}")
        
        if result == QDialog.DialogCode.Accepted:
            name, final_code = dialog.get_data()
            print(f"🔧 [DEBUG] Datos del diálogo: nombre='{name}', código largo={len(final_code) if final_code else 0}")
            if name and final_code:
                try:
                    print(f"🔧 [DEBUG] Guardando snippet '{name}'...")
                    add_snippet(name, final_code)
                    print(f"✅ [DEBUG] Snippet guardado exitosamente")
                    
                    # Refrescar lista
                    overlay._refresh_list(search_snippets(overlay.search_box.text()))
                    print(f"✅ [DEBUG] Lista refrescada")
                    print(f"✅ [DEBUG] Proceso completado exitosamente")
                except ValueError as e:
                    print(f"❌ [DEBUG] Error al guardar: {e}")
                    msg = QMessageBox()
                    msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
                    msg.setIcon(QMessageBox.Icon.Warning)
                    # Agregar icono de la app
                    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
                    if os.path.exists(icon_path):
                        msg.setWindowIcon(QIcon(icon_path))
                    msg.setWindowTitle("Error")
                    msg.setText(str(e))
                    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg.exec()
            else:
                print(f"⚠️ [DEBUG] Nombre o código vacío")
                msg = QMessageBox()
                msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
                msg.setIcon(QMessageBox.Icon.Warning)
                # Agregar icono de la app
                icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
                if os.path.exists(icon_path):
                    msg.setWindowIcon(QIcon(icon_path))
                msg.setWindowTitle("Error")
                msg.setText("Name and code are required.")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
        else:
            print(f"⚠️ [DEBUG] Usuario canceló el diálogo")
    except Exception as e:
        print(f"❌ [DEBUG] Excepción en on_save_selection: {e}")
        import traceback
        traceback.print_exc()
        msg = QMessageBox()
        msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        msg.setIcon(QMessageBox.Icon.Warning)
        # Agregar icono de la app
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            msg.setWindowIcon(QIcon(icon_path))
        msg.setWindowTitle("Error")
        msg.setText(f"Error accessing selection: {e}")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    finally:
        # Asegurar que el flag se resetee
        saving_in_progress = False
        print(f"🔧 [DEBUG] Flag de guardado reseteado")
def on_hotkey_snippet(snippet_name: str, overlay: SnippetOverlay):
    """Maneja las hotkeys para pegar snippets directamente."""
    if snippet_name == "None":
        return
    snippets = search_snippets(snippet_name)
    if snippets:
        code = snippets[0][1]  # snippets is a list of tuples (name, code)
        try:
            # Método más confiable: clipboard + Ctrl+V
            pyperclip.copy(code)
            import time
            time.sleep(0.01)  # Pequeño delay para asegurar que el clipboard se actualice

            # Simular Ctrl+V de manera más confiable
            pyautogui.keyDown('ctrl')
            time.sleep(0.01)
            pyautogui.press('v')
            time.sleep(0.01)
            pyautogui.keyUp('ctrl')

            print(f"✅ Snippet '{snippet_name}' pasted automatically.")

        except Exception as e:
            print(f"❌ Error pasting automatically: {e}")
            # Fallback: intentar escritura directa
            try:
                pyautogui.write(code, interval=0.01)
                print(f"✅ Snippet '{snippet_name}' pasted (alternative method).")
            except Exception as e2:
                print(f"❌ Complete error pasting snippet: {e2}")


def main():
    print("Starting main()...")
    
    # Detectar si se ejecuta como ejecutable compilado
    is_compiled = getattr(sys, 'frozen', False)
    
    # Configurar la aplicación para que inicie en segundo plano
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # No cerrar cuando se cierre la última ventana
    
    if is_compiled:
        # Modo ejecutable: siempre iniciar en modo servicio silencioso
        print("QApplication created (compiled executable mode)")
        
        # Suprimir todas las salidas en modo compilado
        class DevNull:
            def write(self, msg): pass
            def flush(self): pass
        
        sys.stdout = DevNull()
        sys.stderr = DevNull()
        
        # Agregar --service y --auto automáticamente si no están presentes
        if "--service" not in sys.argv:
            sys.argv.append("--service")
        if "--auto" not in sys.argv:
            sys.argv.append("--auto")
    
    else:
        # Modo script Python normal
        print("QApplication created (background mode)")
        
        # Ocultar todas las ventanas de consola y debug en modo servicio
        if "--service" in sys.argv or "--background" in sys.argv:
            # Ocultar ventana de consola en Windows
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.FreeConsole()
            
            # Suprimir prints en modo servicio
            class DevNull:
                def write(self, msg): pass
                def flush(self): pass
            
            sys.stdout = DevNull()
            sys.stderr = DevNull()
        else:
            print("QApplication created")

    # Inicializar Supabase
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Sincronizar hotkeys con snippets existentes
    from core.manager import sync_hotkeys_with_snippets
    sync_hotkeys_with_snippets()

    # Mostrar diálogo de login solo si no está en modo servicio
    if "--service" not in sys.argv and "--background" not in sys.argv:
        login_dialog = LoginDialog(supabase)
        if login_dialog.exec() != QDialog.DialogCode.Accepted:
            return  # Salir si no se logueó
    else:
        # En modo servicio (ejecutable compilado), verificar credenciales guardadas
        try:
            with open("session.json", "r") as f:
                session_data = json.load(f)
                if "--auto" not in sys.argv:  # Solo mostrar mensaje si no es inicio automático
                    print("Sesión encontrada, iniciando en modo servicio...")
        except FileNotFoundError:
            # Si no hay sesión en modo compilado, mostrar login
            if is_compiled:
                login_dialog = LoginDialog(supabase)
                if login_dialog.exec() != QDialog.DialogCode.Accepted:
                    return  # Salir si no se logueó
            else:
                print("Error: No hay sesión guardada. Ejecute primero sin --service para hacer login.")
                return

    print("Creando SnippetOverlay...")
    overlay = SnippetOverlay()
    print("SnippetOverlay creado exitosamente")
    if "--service" not in sys.argv and "--background" not in sys.argv:
        print("SnippetOverlay created")
    
    # En modo servicio, el overlay se mantiene oculto hasta que se necesite

    def on_config():
        """Abrir configuración."""
        from ui.overlay import ConfigDialog
        snippets = search_snippets("")  # Obtener todos los snippets
        dialog = ConfigDialog(current_supabase_url=SUPABASE_URL, current_supabase_key=SUPABASE_KEY, snippets=snippets)
        dialog.exec()

    def on_snippet():
        """Abrir la ventana de snippets."""
        overlay.show_centered()
        overlay.raise_()
        overlay.activateWindow()

    def on_logout():
        """Cerrar sesión."""
        import os
        try:
            os.remove("session.json")
            os.remove("credentials.json")
            msg = QMessageBox()
            msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
            msg.setIcon(QMessageBox.Icon.Information)
            # Agregar icono de la app
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
            if os.path.exists(icon_path):
                msg.setWindowIcon(QIcon(icon_path))
            msg.setWindowTitle("Logout")
            msg.setText("Session closed. The application will exit.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            
            QApplication.quit()
        except FileNotFoundError:
            pass

    def on_close():
        """Cerrar la aplicación."""
        QApplication.quit()

    # Crear controlador para manejar ventanas desde hilos secundarios
    class WindowController(QObject):
        show_selector_signal = pyqtSignal()

        def __init__(self):
            super().__init__()
            self.show_selector_signal.connect(self.show_selector)
            self.number_selector = None

        def show_selector(self):
            """Mostrar selector en el hilo principal de Qt."""
            try:
                print("🔧 Mostrando selector desde hilo principal...")
                
                # Recargar HOTKEY_CONFIG cada vez para obtener cambios recientes
                import json
                try:
                    with open("config.json", "r", encoding="utf-8") as f:
                        config = json.load(f)
                        current_hotkeys = config.get("hotkeys", {})
                except:
                    current_hotkeys = HOTKEY_CONFIG
                
                available_snippets = [k for k,v in current_hotkeys.items() if v != 'None']
                print(f"🔧 [DEBUG] Hotkeys actuales: {current_hotkeys}")
                
                # Callback que busca el código del snippet y lo pega
                def handle_snippet_selection(snippet_name):
                    print(f"🔧 [CALLBACK] handle_snippet_selection llamado con: '{snippet_name}'")
                    
                    # Cerrar el selector
                    if self.number_selector:
                        self.number_selector.close()
                        print(f"🔧 [CALLBACK] Selector cerrado")
                    
                    # Buscar el snippet directamente desde el archivo
                    from core.manager import load_snippets
                    snippets = load_snippets()
                    print(f"🔧 [CALLBACK] Snippets cargados: {list(snippets.keys())}")
                    
                    # Buscar case-insensitive
                    found_snippet = None
                    for key in snippets.keys():
                        if key.lower() == snippet_name.lower():
                            found_snippet = key
                            break
                    
                    if found_snippet:
                        code = snippets[found_snippet]
                        print(f"🔧 [CALLBACK] Código encontrado: {code[:30]}...")
                        # Pegar después de un pequeño delay
                        QTimer.singleShot(100, lambda: paste_snippet_code(found_snippet, code))
                    else:
                        print(f"❌ [CALLBACK] Snippet '{snippet_name}' no encontrado en {list(snippets.keys())}")
                
                def paste_snippet_code(name, code):
                    print(f"🔧 [PASTE] paste_snippet_code llamado para '{name}'")
                    try:
                        pyperclip.copy(code)
                        print(f"✅ Snippet '{name}' copied to clipboard.")
                        
                        # Pegar automáticamente
                        import time
                        time.sleep(0.05)
                        
                        pyautogui.keyDown('ctrl')
                        time.sleep(0.01)
                        pyautogui.press('v')
                        time.sleep(0.01)
                        pyautogui.keyUp('ctrl')
                        
                        print(f"✅ Snippet '{name}' pasted automatically.")
                        
                    except Exception as e:
                        print(f"❌ Error pasting: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Siempre crear un nuevo selector con la configuración actualizada
                if self.number_selector and self.number_selector.isVisible():
                    self.number_selector.close()
                
                self.number_selector = NumberSelector(current_hotkeys, handle_snippet_selection)
                self.number_selector.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
                self.number_selector.show()
                self.number_selector.raise_()
                self.number_selector.activateWindow()
                print(f"✅ Selector mostrado - {len(available_snippets)} snippets")
                    
            except Exception as e:
                print(f"❌ Error mostrando selector: {e}")
                import traceback
                traceback.print_exc()

    window_controller = WindowController()

    def on_selector():
        """Abrir el selector rápido de snippets."""
        window_controller.show_selector_signal.emit()

    # Verificar si el sistema soporta system tray
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "System Tray", 
                           "No se detectó soporte para iconos en la bandeja del sistema.")
        return

    # Crear system tray manager con todas las opciones
    tray_manager = SystemTrayManager(app, on_config, on_snippet, on_selector, on_logout, on_close)

    # Crear emisor de señales para comunicación thread-safe
    emitter = SignalEmitter()
    emitter.save_selection_signal.connect(lambda: on_save_selection(overlay))

    # Conectar la señal del overlay (sin referencia al ícono flotante)
    overlay.snippet_selected.connect(
        lambda name, code: on_snippet_selected(name, code, overlay, None)
    )
    
    def on_double_ctrl():
        """Muestra el selector visual de snippets (llamado desde hilo de keyboard)."""
        print("🔧 F12 pressed - emitting signal...")
        window_controller.show_selector_signal.emit()
        
    # Configurar shortcuts de manera más robusta
    def setup_shortcuts():
        """Configurar shortcuts globales usando threading para evitar bloqueos."""
        shortcuts_configured = False
        
        def setup_keyboard_hotkeys():
            """Configurar hotkeys en un hilo separado."""
            try:
                # NO limpiar hotkeys existentes para evitar el error
                # keyboard.unhook_all_hotkeys()  # Comentado - causa el error
                
                # Registrar hotkeys principales sin suppress
                keyboard.add_hotkey('f12', on_double_ctrl, suppress=False, timeout=1)
                keyboard.add_hotkey('ctrl+shift+s', on_double_ctrl, suppress=False, timeout=1)
                
                # Registrar Alt+1 para guardar selección
                def alt1_handler():
                    print("🔧 [DEBUG] Alt+1 detectado, emitiendo señal...")
                    emitter.save_selection_signal.emit()
                
                keyboard.add_hotkey('alt+1', alt1_handler, suppress=False, timeout=1)
                
                # Registrar hotkeys dinámicos para snippets
                for key, snippet_name in HOTKEY_CONFIG.items():
                    if snippet_name != "None":
                        hotkey_num = key.replace('shift_', '')
                        keyboard.add_hotkey(f'shift+{hotkey_num}', lambda name=snippet_name: on_hotkey_snippet(name, overlay), suppress=False, timeout=1)
                
                print("✅ Global hotkeys configured successfully (F12, Ctrl+Shift+S, Alt+1)")
                
            except Exception as e:
                print(f"❌ Error in hotkey thread: {e}")
                import traceback
                traceback.print_exc()
        
        try:
            # Iniciar hotkeys en hilo separado para no bloquear la aplicación
            import threading
            hotkey_thread = threading.Thread(target=setup_keyboard_hotkeys, daemon=True)
            hotkey_thread.start()
            
            # Dar tiempo a que se configure
            import time
            time.sleep(0.1)
            
            print("✅ Hilo de hotkeys iniciado")
            shortcuts_configured = True
            
        except Exception as e:
            print(f"❌ Error configurando hilo de hotkeys: {e}")
            
            # Fallback: Usar Qt shortcuts
            try:
                selector_shortcut = QShortcut(QKeySequence("F12"), overlay)
                selector_shortcut.activated.connect(on_double_ctrl)
                
                alt_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), overlay)
                alt_shortcut.activated.connect(on_double_ctrl)
                
                print("✅ Fallback: Shortcuts Qt configurados en overlay")
                shortcuts_configured = True
            except Exception as e2:
                print(f"❌ Error con shortcuts Qt fallback: {e2}")
        
        return shortcuts_configured
    
    if setup_shortcuts():
        if "--service" not in sys.argv and "--background" not in sys.argv:
            print("📋 Atajos disponibles:")
            print("   F12 o Ctrl+Shift+S → Abrir selector rápido")
            print("   Alt+1 → Guardar texto seleccionado como snippet")
            print("   Shift+1 a 9 → Pegar snippets asignados")
        # En modo servicio, funciona silenciosamente
    else:
        if "--service" not in sys.argv and "--background" not in sys.argv:
            print("❌ No se pudieron configurar shortcuts")

    # El system tray ya está visible automáticamente
    if "--service" not in sys.argv and "--background" not in sys.argv:
        print("System tray shown, starting event loop...")
    
    # En modo servicio, mostrar notificación de inicio solo si NO es ejecutable compilado
    if "--service" in sys.argv or "--background" in sys.argv:
        # Solo mostrar notificación si es inicio automático Y no es ejecutable compilado
        if "--auto" in sys.argv and not getattr(sys, 'frozen', False):
            try:
                # Importar y mostrar notificación
                import subprocess
                current_dir = os.path.dirname(os.path.abspath(__file__))
                notification_script = os.path.join(current_dir, "startup_notification.py")
                
                # Ejecutar notificación en proceso separado para no bloquear
                QTimer.singleShot(1000, lambda: subprocess.Popen([sys.executable, notification_script]))
            except Exception as e:
                pass  # Error silencioso en modo servicio
        
        # Verificar disponibilidad del system tray
        if QSystemTrayIcon.isSystemTrayAvailable() and "--auto" not in sys.argv and not getattr(sys, 'frozen', False):
            print("SQL Snippet Dock iniciado en segundo plano")

    result = app.exec()
    if "--service" not in sys.argv and "--background" not in sys.argv:
        print(f"App exec returned: {result}")
    sys.exit(result)


if __name__ == "__main__":
    main()
