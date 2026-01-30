# notification.py - Toast notifications for Klip

import sys
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QIcon
import os


class ToastNotification(QLabel):
    """Toast notification that appears briefly and fades away."""
    
    def __init__(self, title, message, duration=3000):
        super().__init__()
        self.duration = duration
        
        # Window properties
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Set icon if available
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Style
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(30, 30, 30, 240);
                border: 2px solid #3b82f6;
                border-radius: 12px;
                padding: 20px;
                color: #ffffff;
            }
        """)
        
        # Content
        content = f"""
        <div style='text-align: center;'>
            <p style='font-size: 16px; font-weight: bold; margin: 0 0 10px 0; color: #3b82f6;'>{title}</p>
            <p style='font-size: 14px; margin: 0; color: #e5e5e5;'>{message}</p>
        </div>
        """
        self.setText(content)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Size
        self.setMinimumSize(300, 100)
        self.adjustSize()
        
        # Position in bottom-right corner
        self.position_bottom_right()
        
    def position_bottom_right(self):
        """Position the notification in the bottom-right corner."""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = screen_geometry.right() - self.width() - 20
            y = screen_geometry.bottom() - self.height() - 20
            self.move(x, y)
    
    def show_notification(self):
        """Show the notification with fade-in and auto-close."""
        self.show()
        self.setWindowOpacity(0.0)
        
        # Fade in animation
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_in.start()
        
        # Auto-close timer
        QTimer.singleShot(self.duration, self.close_notification)
    
    def close_notification(self):
        """Close the notification with fade-out."""
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_out.finished.connect(self.close)
        self.fade_out.start()


def show_startup_notification():
    """Show notification when Klip starts."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    notification = ToastNotification(
        "🚀 Klip Started",
        "Press F12 to access your snippets"
    )
    notification.show_notification()
    
    # Keep notification alive
    QTimer.singleShot(3500, app.quit)
    app.exec()


def show_shutdown_notification():
    """Show notification when Klip stops."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    notification = ToastNotification(
        "⏹️ Klip Stopped",
        "Application closed successfully",
        duration=2000
    )
    notification.show_notification()
    
    # Keep notification alive
    QTimer.singleShot(2500, app.quit)
    app.exec()


if __name__ == "__main__":
    # Test the notification
    show_startup_notification()
