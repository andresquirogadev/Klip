# ui/overlay.py

from typing import List, Tuple
import os

from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QRect, QPoint, QEasingCurve
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QPushButton,
    QDialog,
    QTextEdit,
    QMessageBox,
    QApplication,
    QMenu,
    QGridLayout,
    QCheckBox,
    QComboBox,
    QFrame,
)
from PyQt6.QtGui import QAction

from core.manager import search_snippets, add_snippet, update_snippet, delete_snippet


# Función auxiliar para agregar icono a QMessageBox
def _add_app_icon_to_msgbox(msgbox):
    """Agrega el icono de la app a un QMessageBox."""
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
    if os.path.exists(icon_path):
        msgbox.setWindowIcon(QIcon(icon_path))


class LoginDialog(QDialog):
    def __init__(self, supabase_client):
        super().__init__()
        self.supabase = supabase_client
        self.setWindowTitle("Login - Klip")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.resize(300, 200)
        
        # Cargar ícono de la aplicación
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet("""
        QDialog {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
        QLineEdit {
            background-color: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 4px;
            color: #ffffff;
        }
        QPushButton {
            background-color: #3b82f6;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #2563eb;
        }
        """)

        layout = QVBoxLayout(self)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_edit)

        self.remember_checkbox = QCheckBox("Remember me")
        layout.addWidget(self.remember_checkbox)

        buttons_layout = QHBoxLayout()
        self.register_button = QPushButton("Register")
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.clicked.connect(self.register)
        self.login_button = QPushButton("Login")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self.login)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.register_button)
        buttons_layout.addWidget(self.login_button)
        layout.addLayout(buttons_layout)

        # Cargar credenciales guardadas
        self.load_credentials()

    def login(self):
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        if not email or not password:
            msg = QMessageBox(self)
            _add_app_icon_to_msgbox(msg)
            msg.warning(self, "Error", "Email and password are required.")
            return
        try:
            response = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            if response.user:
                if self.remember_checkbox.isChecked():
                    self.save_credentials(email, password)
                    self.save_session_data(response.session)
                self.accept()
            else:
                msg = QMessageBox(self)
                _add_app_icon_to_msgbox(msg)
                msg.warning(self, "Error", "Login failed.")
        except Exception as e:
            msg = QMessageBox(self)
            _add_app_icon_to_msgbox(msg)
            msg.warning(self, "Error", f"Login error: {str(e)}")

    def save_credentials(self, email, password):
        import json
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}
        config["email"] = email
        config["password"] = password
        with open("config.json", "w") as f:
            json.dump(config, f)

    def save_session_data(self, session):
        import json
        session_data = {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
        }
        with open("session.json", "w") as f:
            json.dump(session_data, f)

    def load_session_data(self):
        import json
        try:
            with open("session.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def load_credentials(self):
        import json
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.email_edit.setText(config.get("email", ""))
                self.password_edit.setText(config.get("password", ""))
                self.remember_checkbox.setChecked(True)
        except FileNotFoundError:
            pass

    def register(self):
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        if not email or not password:
            msg = QMessageBox(self)
            _add_app_icon_to_msgbox(msg)
            msg.warning(self, "Error", "Email and password are required.")
            return
        try:
            response = self.supabase.auth.sign_up({"email": email, "password": password})
            if response.user:
                msg = QMessageBox(self)
                _add_app_icon_to_msgbox(msg)
                msg.information(self, "Success", "Registration successful! Please check your email to confirm your account.")
            else:
                msg = QMessageBox(self)
                _add_app_icon_to_msgbox(msg)
                msg.warning(self, "Error", "Registration failed.")
        except Exception as e:
            msg = QMessageBox(self)
            _add_app_icon_to_msgbox(msg)
            msg.warning(self, "Error", f"Registration error: {str(e)}")


class FloatingIcon(QWidget):
    def __init__(self, on_config, on_snippet, on_logout, on_close):
        super().__init__()
        self.on_config = on_config
        self.on_snippet = on_snippet
        self.on_logout = on_logout
        self.on_close = on_close
        
        # Variables para movimiento del widget
        self.dragging = False
        self.drag_position = None
        self.drag_start_pos = None
        
        self.setWindowTitle("SQL Dock")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(70, 70)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # Solo el botón principal
        self.main_button = QPushButton("SQL")
        self.main_button.setFixedSize(60, 60)
        self.main_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                border-radius: 30px;
                color: white;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        
        # Crear menú contextual
        self.context_menu = QMenu(self)
        
        # Añadir acciones al menú
        config_action = QAction("⚙️ Configuración", self)
        config_action.triggered.connect(self.on_config)
        self.context_menu.addAction(config_action)
        
        snippet_action = QAction("📄 Snippets", self)
        snippet_action.triggered.connect(self.on_snippet)
        self.context_menu.addAction(snippet_action)
        
        self.context_menu.addSeparator()
        
        logout_action = QAction("🚪 Cerrar Sesión", self)
        logout_action.triggered.connect(self.on_logout)
        self.context_menu.addAction(logout_action)
        
        close_action = QAction("❌ Salir", self)
        close_action.triggered.connect(self.on_close)
        self.context_menu.addAction(close_action)
        
        # Añadir el botón al layout
        self.layout.addWidget(self.main_button)

        # Posicionar en esquina inferior izquierda
        self.position_in_corner()

    def position_in_corner(self):
        screen = self.screen() or QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            x = 10  # Esquina inferior IZQUIERDA
            y = geometry.height() - self.height() - 10
            self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            # Mostrar menú contextual
            self.context_menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_start_pos:
            if not self.dragging:
                # Iniciar arrastre si se movió lo suficiente
                if (event.globalPosition().toPoint() - self.drag_start_pos).manhattanLength() > 5:
                    self.dragging = True
                    self.drag_position = self.drag_start_pos - self.pos()
            
            if self.dragging:
                self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.drag_start_pos = None
            self.drag_position = None

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.drag_start_pos = None
            self.drag_position = None


class ConfigDialog(QDialog):
    def __init__(self, parent=None, current_supabase_url="", current_supabase_key="", snippets=None):
        super().__init__(parent)
        self.current_supabase_url = current_supabase_url
        self.current_supabase_key = current_supabase_key
        self.snippets = snippets or []
        self.hotkey_combos = {}  # Almacenar los combos para hotkeys
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        # Cargar ícono de la aplicación
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        self.resize(450, 350)
        self.setStyleSheet("""
        QDialog {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
        QLineEdit {
            background-color: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 4px;
            color: #ffffff;
        }
        QPushButton {
            background-color: #3b82f6;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #2563eb;
        }
        QFrame#upgradeBanner {
            background-color: #3b82f6;
            border-radius: 8px;
            padding: 12px;
        }
        QLabel#upgradeText {
            color: #ffffff;
            font-weight: bold;
        }
        QLabel#limitInfo {
            color: #60a5fa;
            font-size: 11px;
        }
        """)

        layout = QVBoxLayout(self)
        
        # FREE Version Banner
        from core.manager import get_snippets_limit_info, MAX_SNIPPETS_FREE
        
        banner_frame = QFrame()
        banner_frame.setObjectName("upgradeBanner")
        banner_layout = QVBoxLayout(banner_frame)
        banner_layout.setSpacing(4)
        
        upgrade_label = QLabel("⭐ Klip FREE Version")
        upgrade_label.setObjectName("upgradeText")
        
        limit_label = QLabel(f"📊 Snippets: {get_snippets_limit_info()} • Upgrade to Premium for unlimited snippets!")
        limit_label.setObjectName("limitInfo")
        limit_label.setWordWrap(True)
        
        banner_layout.addWidget(upgrade_label)
        banner_layout.addWidget(limit_label)
        
        layout.addWidget(banner_frame)

        # Hotkeys - Info para FREE version
        hotkeys_header = QHBoxLayout()
        hotkeys_label = QLabel("Snippet Quick Access (F12 + number):")
        hotkeys_info = QLabel("🔓 Premium: Custom hotkeys")
        hotkeys_info.setStyleSheet("color: #60a5fa; font-size: 10px;")
        hotkeys_header.addWidget(hotkeys_label)
        hotkeys_header.addStretch()
        hotkeys_header.addWidget(hotkeys_info)
        layout.addLayout(hotkeys_header)

        self.hotkey_combos = {}
        snippet_names = [snippet[0] for snippet in self.snippets] + ["None"]
        
        for i in range(1, 11):  # F12 + 1 to F12 + 0 (0 is 10)
            combo = QComboBox()
            combo.addItems(snippet_names)
            combo.setCurrentText("None")
            self.hotkey_combos[f"shift_{i if i < 10 else 0}"] = combo
            layout.addWidget(QLabel(f"Number {i if i < 10 else 0}:"))
            layout.addWidget(combo)

        # Botones
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_config)
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        layout.addLayout(buttons_layout)

        # Cargar configuración
        self.load_config()

    def load_config(self):
        import json
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                # Cargar hotkeys (compatibilidad con configuraciones antiguas y nuevas)
                hotkeys = config.get("hotkeys", {})
                for key, combo in self.hotkey_combos.items():
                    # Intentar primero la nueva clave (shift_)
                    value = hotkeys.get(key, None)
                    # Si no existe, intentar ctrl_
                    if value is None and key.startswith("shift_"):
                        ctrl_key = key.replace("shift_", "ctrl_")
                        value = hotkeys.get(ctrl_key, None)
                    # Si tampoco existe, intentar alt_gr_
                    if value is None and key.startswith("shift_"):
                        alt_gr_key = key.replace("shift_", "alt_gr_")
                        value = hotkeys.get(alt_gr_key, None)
                    # Si tampoco existe, intentar alt_shift_
                    if value is None and key.startswith("shift_"):
                        alt_shift_key = key.replace("shift_", "alt_shift_")
                        value = hotkeys.get(alt_shift_key, None)
                    # Si tampoco existe, intentar scroll_
                    if value is None and key.startswith("shift_"):
                        scroll_key = key.replace("shift_", "scroll_")
                        value = hotkeys.get(scroll_key, None)
                    # Si tampoco existe, intentar ctrl_alt_
                    if value is None and key.startswith("shift_"):
                        ctrl_alt_key = key.replace("shift_", "ctrl_alt_")
                        value = hotkeys.get(ctrl_alt_key, None)
                    # Si tampoco existe, intentar ctrl_shift_
                    if value is None and key.startswith("shift_"):
                        ctrl_shift_key = key.replace("shift_", "ctrl_shift_")
                        value = hotkeys.get(ctrl_shift_key, None)
                    # Si tampoco existe, intentar alt_
                    if value is None and key.startswith("shift_"):
                        alt_key = key.replace("shift_", "alt_")
                        value = hotkeys.get(alt_key, "None")
                    combo.setCurrentText(value if value is not None else "None")
        except FileNotFoundError:
            # No config file exists yet
            pass

    def save_config(self):
        import json
        hotkeys = {}
        for key, combo in self.hotkey_combos.items():
            hotkeys[key] = combo.currentText()
        
        config = {
            "hotkeys": hotkeys,
        }
        
        # Preservar valores existentes en config.json que no se editan en FREE
        try:
            with open("config.json", "r") as f:
                old_config = json.load(f)
                # Preservar email y password si existen
                if "email" in old_config:
                    config["email"] = old_config["email"]
                if "password" in old_config:
                    config["password"] = old_config["password"]
                # Preservar supabase_url y supabase_key
                if "supabase_url" in old_config:
                    config["supabase_url"] = old_config["supabase_url"]
                if "supabase_key" in old_config:
                    config["supabase_key"] = old_config["supabase_key"]
        except FileNotFoundError:
            pass
        
        with open("config.json", "w") as f:
            json.dump(config, f)
        msg = QMessageBox(self)
        _add_app_icon_to_msgbox(msg)
        msg.information(self, "Saved", "Configuration saved.")
        self.accept()


class SnippetDialog(QDialog):
    def __init__(self, parent=None, name="", code=""):
        super().__init__(parent)
        self.setWindowTitle("Edit Snippet" if name else "New Snippet")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.resize(400, 300)
        
        # Cargar ícono de la aplicación
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet("""
        QDialog {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
        QLineEdit, QTextEdit {
            background-color: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 4px;
            color: #ffffff;
        }
        QPushButton {
            background-color: #3b82f6;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #2563eb;
        }
        """)

        layout = QVBoxLayout(self)

        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("Snippet name")
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(self.name_edit)

        self.code_edit = QTextEdit(code)
        self.code_edit.setPlaceholderText("SQL code...")
        layout.addWidget(QLabel("Code:"))
        layout.addWidget(self.code_edit)

        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._on_ok_clicked)
        self.ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.ok_button)
        layout.addLayout(buttons_layout)

    def _on_ok_clicked(self):
        """Manejar click en OK con animación de éxito."""
        # Validar que hay datos
        name = self.name_edit.text().strip()
        code = self.code_edit.toPlainText().strip()
        
        if not name or not code:
            msg = QMessageBox(self)
            _add_app_icon_to_msgbox(msg)
            msg.warning(self, "Error", "Name and code are required.")
            return
        
        # Mostrar mensaje de éxito simple
        msg = QMessageBox(self)
        _add_app_icon_to_msgbox(msg)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
        msg.setText(f"Snippet '{name}' saved successfully and assigned to next available number!")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        msg.exec()
        
        # Aceptar el diálogo
        self.accept()

    def get_data(self):
        return self.name_edit.text().strip(), self.code_edit.toPlainText().strip()


class SnippetOverlay(QWidget):
    # Señal que emitirá el snippet seleccionado (nombre, código)
    snippet_selected = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Klip")
        
        # Cargar ícono de la aplicación
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        # self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._build_ui()
        self._load_initial_data()

    def _build_ui(self):
        # Fondo "caja" interna
        self.container = QWidget(self)
        self.container.setObjectName("container")

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header with title and snippet count
        header_layout = QHBoxLayout()
        
        # Label título
        self.title_label = QLabel("SQL Snippets")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        # Snippet counter label
        from core.manager import get_snippets_limit_info
        self.counter_label = QLabel(get_snippets_limit_info())
        counter_font = QFont()
        counter_font.setPointSize(10)
        self.counter_label.setFont(counter_font)
        self.counter_label.setStyleSheet("color: #60a5fa;")
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.counter_label)
        
        layout.addLayout(header_layout)

        # Cuadro de búsqueda
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search snippet by name or code...")
        self.search_box.textChanged.connect(self._on_search_changed)
        
        layout.addWidget(self.search_box)

        # Lista de resultados
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_item_activated)
        self.list_widget.itemActivated.connect(self._on_item_activated)  # Enter
        self.list_widget.setCursor(Qt.CursorShape.PointingHandCursor)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self._on_add)
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self._on_edit)
        self.edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._on_delete)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.hide)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.close_button)

        layout.addWidget(self.list_widget)
        layout.addLayout(buttons_layout)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(self.container)

        self._apply_styles()

        # Tamaño y posición inicial
        self.resize(500, 400)

    def _apply_styles(self):
        # Estilo simple pero moderno (luego metemos más "glow" y blur)
        self.setStyleSheet("""
        #container {
            background-color: #1e1e1e;
            border-radius: 16px;
        }
        QLabel {
            color: #ffffff;
        }
        QLineEdit {
            background-color: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            padding: 6px 8px;
            color: #ffffff;
            selection-background-color: #3b82f6;
        }
        QListWidget {
            background-color: #222222;
            border: 1px solid #3a3a3a;
            border-radius: 8px;
            color: #e5e5e5;
        }
        QListWidget::item {
            padding: 6px 8px;
        }
        QListWidget::item:selected {
            background-color: #3b82f6;
            color: #ffffff;
        }
        QPushButton {
            background-color: #3b82f6;
            border: none;
            border-radius: 6px;
            padding: 8px 12px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #2563eb;
        }
        QPushButton:pressed {
            background-color: #1d4ed8;
        }
        """)

    def _load_initial_data(self):
        self._refresh_list(search_snippets(""))
        self._update_counter()

    def _refresh_list(self, data: List[Tuple[str, str]]):
        # Cargar hotkeys para saber qué número tiene cada snippet
        import json
        hotkey_map = {}  # snippet_name -> number
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                hotkeys = config.get("hotkeys", {})
                # Invertir el diccionario: de shift_1 -> snippet a snippet -> 1
                for key, snippet_name in hotkeys.items():
                    if key.startswith("shift_") and snippet_name:
                        number = key.replace("shift_", "")
                        if number == "0":
                            hotkey_map[snippet_name] = "0"
                        else:
                            hotkey_map[snippet_name] = number
        except:
            pass
        
        self.list_widget.clear()
        for name, code in data:
            preview = code.replace("\n", " ")
            if len(preview) > 80:
                preview = preview[:77] + "..."
            
            # Agregar el número si está asignado
            number_prefix = ""
            if name in hotkey_map:
                number_prefix = f"[F12+{hotkey_map[name]}] "
            
            item = QListWidgetItem(f"{number_prefix}{name}  —  {preview}")
            # Guardamos el código completo en el item
            item.setData(Qt.ItemDataRole.UserRole, (name, code))
            self.list_widget.addItem(item)
        self._update_counter()
    
    def _update_counter(self):
        """Update the snippet counter display."""
        from core.manager import get_snippets_limit_info, can_add_more_snippets
        self.counter_label.setText(get_snippets_limit_info())
        
        # Disable Add button if limit reached
        if not can_add_more_snippets():
            self.add_button.setEnabled(False)
            self.add_button.setToolTip("Snippet limit reached. Upgrade to Premium for unlimited snippets!")
        else:
            self.add_button.setEnabled(True)
            self.add_button.setToolTip("")

    def _on_search_changed(self, text: str):
        results = search_snippets(text)
        self._refresh_list(results)

    def _on_item_activated(self, item: QListWidgetItem):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            name, code = data
            # Emitimos la señal para que main.py decida qué hacer
            self.snippet_selected.emit(name, code)
            # No cerramos la ventana, para permitir gestión

    def _on_add(self):
        dialog = SnippetDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, code = dialog.get_data()
            if name and code:
                try:
                    add_snippet(name, code)
                    self._refresh_list(search_snippets(self.search_box.text()))
                except ValueError as e:
                    msg = QMessageBox(self)
                    _add_app_icon_to_msgbox(msg)
                    msg.warning(self, "Error", str(e))
            else:
                msg = QMessageBox(self)
                _add_app_icon_to_msgbox(msg)
                msg.warning(self, "Error", "Name and code are required.")

    def _on_edit(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            msg = QMessageBox(self)
            _add_app_icon_to_msgbox(msg)
            msg.information(self, "Edit", "Select a snippet to edit.")
            return
        name, code = current_item.data(Qt.ItemDataRole.UserRole)
        dialog = SnippetDialog(self, name, code)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name, new_code = dialog.get_data()
            if new_name and new_code:
                try:
                    update_snippet(name, new_name, new_code)
                    self._refresh_list(search_snippets(self.search_box.text()))
                except ValueError as e:
                    msg = QMessageBox(self)
                    _add_app_icon_to_msgbox(msg)
                    msg.warning(self, "Error", str(e))
            else:
                msg = QMessageBox(self)
                _add_app_icon_to_msgbox(msg)
                msg.warning(self, "Error", "Select a snippet to edit.")

    def _on_delete(self):
        current_item = self.list_widget.currentItem()
        if not current_item:
            msg = QMessageBox(self)
            _add_app_icon_to_msgbox(msg)
            msg.information(self, "Delete", "Select a snippet to delete.")
            return
        name, _ = current_item.data(Qt.ItemDataRole.UserRole)
        msg = QMessageBox(self)
        _add_app_icon_to_msgbox(msg)
        reply = msg.question(
            self, "Confirm", f"Are you sure you want to delete the snippet '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                delete_snippet(name)
                self._refresh_list(search_snippets(self.search_box.text()))
            except ValueError as e:
                msg2 = QMessageBox(self)
                _add_app_icon_to_msgbox(msg2)
                msg2.warning(self, "Error", str(e))

    def show_centered(self):
        """Muestra la ventana centrada en la pantalla."""
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            x = geometry.center().x() - self.width() // 2
            y = geometry.center().y() - self.height() // 2
            self.move(x, y)
        self.show()
        self.search_box.setFocus()


class NumberSelector(QDialog):
    """Modal window to select number after double Ctrl."""
    
    def __init__(self, hotkey_config, on_snippet_selected_callback):
        super().__init__()
        self.hotkey_config = hotkey_config
        self.on_snippet_selected = on_snippet_selected_callback
        
        self.setWindowTitle("Snippet Selector")
        
        # Cargar ícono de la aplicación
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QIcon
            self.setWindowIcon(QIcon(icon_path))
        
        # Quitar modal para system tray
        self.setModal(False)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowType.Tool)  # Hacer que sea una ventana tool para mejor visibilidad
        self.resize(300, 200)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Centrar en pantalla
        self.center_on_screen()
        
        self.setStyleSheet("""
        QDialog {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 2px solid #3a3a3a;
            border-radius: 8px;
        }
        QLabel {
            color: #ffffff;
            font-size: 12px;
        }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Título
        title = QLabel("Press a number (1-9, 0) to paste snippet:")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; margin-bottom: 10px; font-size: 12px;")
        layout.addWidget(title)

        # Mostrar snippets asignados
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)
        
        # Crear botones para números 1-9, 0
        positions = [(i, j) for i in range(3) for j in range(3)] + [(3, 1)]  # 3x3 grid + 0 en el centro abajo
        
        number = 1
        for pos in positions:
            if number <= 9:
                snippet_name = self.hotkey_config.get(f"shift_{number}", "None")
                if snippet_name != "None":
                    label_text = f"{number}: {snippet_name[:15]}{'...' if len(snippet_name) > 15 else ''}"
                else:
                    label_text = f"{number}: (not assigned)"
                number += 1
            else:  # número 0
                snippet_name = self.hotkey_config.get("shift_0", "None")
                if snippet_name != "None":
                    label_text = f"0: {snippet_name[:15]}{'...' if len(snippet_name) > 15 else ''}"
                else:
                    label_text = f"0: (not assigned)"
            
            label = QLabel(label_text)
            label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                padding: 5px;
                font-size: 10px;
            }
            """)
            grid_layout.addWidget(label, pos[0], pos[1])

        layout.addLayout(grid_layout)

        # Instrucción
        instruction = QLabel("Press ESC to cancel")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setStyleSheet("color: #888888; font-size: 10px; margin-top: 10px;")
        layout.addWidget(instruction)

        # Centrar la ventana
        self.center_on_screen()

    def center_on_screen(self):
        """Centrar la ventana en la pantalla."""
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        # Activar foco después de centrar
        self.activateWindow()
        self.setFocus()

    def keyPressEvent(self, event):
        """Manejar pulsaciones de teclas."""
        key = event.key()
        
        # Números 0-9 (teclado principal y keypad)
        if key >= Qt.Key.Key_0 and key <= Qt.Key.Key_9:
            number = key - Qt.Key.Key_0
            self.select_snippet(number)
        # ESC para cancelar
        elif key == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def select_snippet(self, number):
        """Seleccionar y pegar el snippet correspondiente al número."""
        print(f"🔧 [SELECTOR] select_snippet llamado con número: {number}")
        config_key = f"shift_{number}"
        snippet_name = self.hotkey_config.get(config_key, "None")
        print(f"🔧 [SELECTOR] Config key: {config_key}, Snippet name: '{snippet_name}'")
        
        if snippet_name != "None":
            print(f"🔧 [SELECTOR] Llamando callback con snippet: '{snippet_name}'")
            self.on_snippet_selected(snippet_name)
        else:
            # Si no hay snippet asignado, mostrar mensaje breve
            print(f"⚠️ [SELECTOR] No hay snippet asignado para el número {number}")
            self.show_message(f"Number {number}: No snippet assigned")
    
    def show_message(self, message):
        """Show temporary message."""
        msg_box = QMessageBox(self)
        _add_app_icon_to_msgbox(msg_box)
        msg_box.setWindowTitle("Notice")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        msg_box.exec()

    def show_centered(self):
        """Muestra la ventana centrada en la pantalla actual."""
        screen = self.screen() or self.windowHandle().screen()
        if screen:
            geometry = screen.geometry()
            x = geometry.center().x() - self.width() // 2
            y = geometry.center().y() - self.height() // 2
            self.move(x, y)
        self.show()
        self.search_box.setFocus()

    def center_on_screen(self):
        """Centra la ventana en la pantalla."""
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            x = geometry.center().x() - self.width() // 2
            y = geometry.center().y() - self.height() // 2
            self.move(x, y)



