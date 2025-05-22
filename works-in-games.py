import sys
from PyQt5.QtWidgets import QWidget, QApplication, QAction, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QFontDatabase


class GameOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("X11GameOverlay")
        self.setAttribute(Qt.WA_TranslucentBackground)

        # X11-specific window type settings
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_X11NetWmWindowTypeNotification, True)

        # Setup UI
        self.setup_ui()

        # Setup periodic activation
        self.activation_timer = QTimer(self)
        self.activation_timer.timeout.connect(self.force_activation)
        self.activation_timer.start(1000)

        # Drag functionality
        self.drag_position = QPoint()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Add a text label
        label = QLabel("GAME OVERLAY\nKDE/X11 VERSION")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                text-shadow: 2px 2px 2px black;
            }
        """)
        layout.addWidget(label)

        # Set initial size and position
        self.resize(400, 200)
        self.move(50, 50)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw semi-transparent red background
        painter.setBrush(QColor(255, 0, 0, 150))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

    def force_activation(self):
        self.raise_()
        self.showNormal()
        self.setAttribute(Qt.WA_UnderMouse, False)
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Important X11 initialization
    if app.platformName() == "xcb":
        app.setAttribute(Qt.AA_X11InitThreads, True)

    overlay = GameOverlay()
    overlay.show()

    sys.exit(app.exec_())