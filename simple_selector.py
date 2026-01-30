# simple_selector.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SimpleSelector(QDialog):
    """Selector simplificado para testing."""
    
    def __init__(self, hotkey_config, callback):
        super().__init__()
        self.hotkey_config = hotkey_config
        self.callback = callback
        
        self.setWindowTitle("Simple Selector")
        self.setModal(False)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.WindowType.Tool)
        self.resize(200, 150)
        
        # Centrar en pantalla
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            x = geometry.center().x() - self.width() // 2
            y = geometry.center().y() - self.height() // 2
            self.move(x, y)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Snippet Selector")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Mostrar snippets disponibles
        available = [f"{k}: {v}" for k,v in hotkey_config.items() if v != 'Ninguno']
        for item in available[:5]:  # Solo mostrar primeros 5
            label = QLabel(item)
            layout.addWidget(label)
        
        info = QLabel("Press ESC to close")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        self.setStyleSheet("""
        QDialog {
            background-color: #2b2b2b;
            color: white;
            border: 2px solid #555;
        }
        QLabel {
            color: white;
            padding: 2px;
        }
        """)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)