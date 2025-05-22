import os
import signal

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QWidget, QApplication

# from PyQt6.QtWebEngineCore import QWebEngineSettings

# Enable Developer Extras (Inspector)

os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9222"  # Enable dev tools on port 9222

class GameOverlay(QWidget):
    def __init__(self, background_opacity: float = 0.5):
        super().__init__()
        # self.chat_url = "https://www.twitch.tv/popout/luality/chat?popout="
        # self.chat_url = "https://www.twitch.tv/popout/swol/chat?popout="
        self.chat_url = "https://www.twitch.tv/popout/zackrawrr/chat?popout="

        self.background_opacity = background_opacity  # 0.0 (fully transparent) to 1.0 (fully opaque)

        # Set overlay window properties
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            # | Qt.WindowType.WindowStaysOnTopHint
            # | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # Enable transparency
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)

        # Initialize chat view
        self.chat_view = QWebEngineView(self)
        self.chat_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.chat_view.loadFinished.connect(self.injectScripts)
        # a.loadFinished.connect(lambda success: print('hello page 2'))
        self.chat_view.setUrl(QUrl(self.chat_url))
        self.chat_view.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.chat_view.setStyleSheet("background: transparent;")

    def resizeEvent(self, event):
        """Resize chat overlay to fit window size."""
        self.chat_view.setGeometry(0, 0, self.width(), self.height())

    def injectScripts(self, success):
        """Loads and injects JS scripts into the page after load."""
        if not success:
            print("Page failed to load!")
            return
        print("Page loaded successfully!")

        self.chat_view.page().setBackgroundColor(Qt.GlobalColor.transparent)

        script_files = ["cleanup.js", "transparent-bg.js"]
        for script_file in script_files:
            script_path = os.path.join(os.getcwd(), script_file)
            print(f"Checking for script: {script_file} at {script_path}")

            if os.path.exists(script_path):
                try:
                    with open(script_path, "r", encoding="utf-8") as script:
                        js_code = script.read()
                        print(f"Injecting script: {script_file}")
                        self.chat_view.page().runJavaScript(js_code, self.scriptInjectCallback)
                except Exception as e:
                    print(f"Error reading {script_file}: {e}")
            else:
                print(f"Warning: {script_file} not found in the current directory.")

    def scriptInjectCallback(self, result):
        """ Callback to check script execution results. """
        print(f"Script executed, result: {result}")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Allow Ctrl+C to close the app
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    overlay = GameOverlay(background_opacity=0.5)
    overlay.resize(800, 600)  # Set initial size
    overlay.show()

    print("Open Chrome and navigate to: http://localhost:9222 to inspect the page.")

    sys.exit(app.exec())
