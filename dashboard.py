import signal
import sys
import os

from PyQt6.QtCore import QTimer, QPoint, QSize, QRectF, Qt, QRect, QEvent
from PyQt6.QtGui import QColor, QKeySequence, QPainter, QIcon, QPixmap, QAction, QFont, QActionGroup, QFontMetrics, QTextOption
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QApplication, QWidget, QSystemTrayIcon, QMenu, QFontDialog, QCheckBox,
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QRadioButton,
    QGroupBox, QSlider, QColorDialog, QFileDialog, QKeySequenceEdit, QStackedWidget,
    QTextEdit, QFrame, QSizePolicy
)

# ... (Controller classes remain the same)
# ======================
# Controller Classes
# ======================
class TTSController:
    def __init__(self):
        self._queue_size = 22
        self._autoplay = False
        self._queue_prefix = "🗣️: "
    
    @property
    def queue_size(self): 
        return self._queue_size
    
    @property
    def queue_status(self): 
        return f"{self._queue_prefix}{self._queue_size}"
    
    def play(self): 
        print("TTS: Playing next item")
    
    def stop(self): 
        print("TTS: Stopping playback")
    
    def toggle_autoplay(self, state): 
        self._autoplay = state
        print(f"TTS: Autoplay {'✓' if state else '⨯'}")

class OBSController:
    def __init__(self): 
        self._recording = False
        self._status_prefix = "🎥: "
    
    @property
    def status(self): 
        return f"{self._status_prefix}Rec •" if self._recording else f"{self._status_prefix}Stop ⏹"
    
    def toggle_recording(self): 
        self._recording = not self._recording
        print("OBS: Toggled recording state")

class ViewerController:
    def __init__(self): 
        self._count = 123
        self._count_prefix = "👀: "
    
    @property
    def count(self): 
        return self._count
    
    @property
    def count_status(self): 
        return f"{self._count_prefix}{self._count}"

class AdController:
    def __init__(self):
        self._time_till_next = 30 * 60
        self._double_ad = False
        self._timer = QTimer()
        self._timer.timeout.connect(self._decrement_time)
        self._timer.start(1000)

    def _decrement_time(self):
        if self._time_till_next > 0: 
            self._time_till_next -= 1
            
    @property
    def time_till_next_display(self): 
        minutes = self._time_till_next // 60
        seconds = self._time_till_next % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    @property
    def time_till_next(self): 
        return self._time_till_next // 60
    
    def delay(self, minutes): 
        self._time_till_next += minutes * 60
        print(f"Ad: Delayed by {minutes} minutes")
        
    def run(self): 
        print("Ad: Running ad now")
        if self._double_ad: 
            print("Ad: Running second ad (double mode)")
            
    def toggle_double(self, state): 
        self._double_ad = state
        print(f"Ad: Double mode {'✓' if state else '⨯'}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        self.setMouseTracking(True)
        # ... (Controllers and other initializations as before)
        self.tts_controller = TTSController()
        self.obs_controller = OBSController()
        self.viewer_controller = ViewerController()
        self.ad_controller = AdController()
        self._image_scale_modifier = 0.22
        background_color = '#EBECE9'
        self._background_opacity = 0.5
        self._background_qcolor = QColor(background_color)
        self._background_image_path = "img/bg.svg"
        self._tray_icon_path = "img/tray_icon.svg"
        self._default_window_size = (400, 400)
        self._whiteboard_content_path = os.path.join(os.path.expanduser("~"), ".twitch-panel", "whiteboard.txt")
        os.makedirs(os.path.dirname(self._whiteboard_content_path), exist_ok=True)
        print(f"Whiteboard will be saved to: {self._whiteboard_content_path}")
        self.button_height = 32
        self.button_color = QColor("white")
        self.button_text_color = QColor("navy")
        self.button_font = QFont("Arial", 12)
        self.icon_size = 16
        self.status_bar_internal_margin = 5
        self.actual_status_bar_height = self.button_height + (2 * self.status_bar_internal_margin)
        self.chat_font = QFont("Arial", 12)
        self.tts_font = QFont("Arial", 12)
        self.whiteboard_font = QFont("Arial", 12)
        self.buttons = []
        self.labels = []
        self.checkboxes = []
        self.stream_window = StreamWindow(main_window_ref=self)
        self.stream_window.move(-10000, -10000)
        self.stream_window.show()
        self.header_preview_container = None
        self.header_preview_label = None
        self._original_status_bar_widget = None
        self._status_bar_index_in_layout = -1
        self.setup_ui()
        self.setup_tray()
        self.dragging = False
        self.resizing = False
        self.resize_corner = None
        self.drag_start_pos = QPoint()
        self.start_geometry = QRect()
        self.resize_margin = 40
        self.resize(*self._default_window_size)
        self.move_to_top_right()
        self.installEventFilter(self)
        self.load_whiteboard()
        QApplication.instance().installEventFilter(self)
        self.ad_label_update_timer = QTimer(self)
        self.ad_label_update_timer.timeout.connect(self.update_ad_time_label)
        self.ad_label_update_timer.start(1000)

    def update_ad_time_label(self):
        is_preview_active = self.header_preview_container and self.header_preview_container.isVisible()
        if is_preview_active: 
            return 
        if hasattr(self, 'time_till_next_label'): 
            self.time_till_next_label.setText(f"📢: {self.ad_controller.time_till_next_display}")
        if hasattr(self, 'obs_status_label'): 
            self.obs_status_label.setText(self.obs_controller.status)
        if hasattr(self, 'viewers_label'): 
            self.viewers_label.setText(self.viewer_controller.count_status)
        if hasattr(self, 'tts_queue_label'): 
            self.tts_queue_label.setText(self.tts_controller.queue_status)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if hasattr(self,'profile_settings_window') and self.profile_settings_window and self.profile_settings_window.isVisible():
                header_group = self.profile_settings_window.findChild(QGroupBox, "Whiteboard Header")
                preview_is_active = self.header_preview_container and self.header_preview_container.isVisible()
                global_pos_qpoint = event.globalPosition().toPoint()
                clicked_widget = QApplication.widgetAt(global_pos_qpoint)
                is_click_in_header_group = header_group and clicked_widget and header_group.isAncestorOf(clicked_widget)
                is_click_in_preview_area_main_window = False
                if preview_is_active and self.header_preview_container and clicked_widget:
                    if self.header_preview_container.geometry().contains(self.header_preview_container.mapFromGlobal(global_pos_qpoint)):
                         is_click_in_preview_area_main_window = True
                is_click_in_active_dialog = False
                if self.profile_settings_window._active_dialog and self.profile_settings_window._active_dialog.isVisible():
                    if clicked_widget and self.profile_settings_window._active_dialog.isAncestorOf(clicked_widget):
                        is_click_in_active_dialog = True
                if not (is_click_in_header_group or is_click_in_preview_area_main_window or is_click_in_active_dialog):
                    self.hide_header_preview()
        
        if obj == self:
            if event.type() == QEvent.Type.Move: # Only call update_stream_window on Move
                self.update_stream_window() 
            elif event.type() == QEvent.Type.Resize:
                self.update_stream_window() # Also call on Resize
                if self.header_preview_container and self.header_preview_container.isVisible():
                    self._update_preview_label_text(self.stream_window.header_text) # Recalculate preview label width

        return super().eventFilter(obj, event)
        
    def update_stream_window(self):
        if hasattr(self,'stream_window') and self.stream_window:
            main_pos = self.pos()
            main_size = self.size()
            min_w, min_h = 10, 10 
            effective_size = QSize(max(main_size.width(),min_w), max(main_size.height(),min_h))
            self.stream_window.setGeometry(QRect(main_pos, effective_size))
            # stream_window's resizeEvent will call update_whiteboard_document_width
            self.stream_window.lower()
        
    # ... (load_whiteboard as before)
    def load_whiteboard(self, content_path=None):
        path_to_load = content_path if content_path else self._whiteboard_content_path
        loaded_content = ""
        print(f"Attempting to load whiteboard from: {path_to_load}")
        try:
            if os.path.exists(path_to_load):
                with open(path_to_load, 'r', encoding='utf-8') as f: 
                    loaded_content = f.read()
                self.whiteboard.setPlainText(loaded_content)
                if hasattr(self,'stream_window') and self.stream_window: 
                    self.stream_window.whiteboard.setPlainText(loaded_content)
                if loaded_content: 
                    print(f"Loaded {len(loaded_content)} characters.")
            else: 
                print(f"No existing whiteboard file found.")
        except Exception as e: 
            print(f"Error loading whiteboard: {e}")
    
    # ... (setup_tray as before)
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        if os.path.exists(self._tray_icon_path):
            renderer = QSvgRenderer(self._tray_icon_path)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)
        
        tray_menu = QMenu()
        show_main_action = QAction("Show Main window", self, checkable=True, checked=True)
        show_stream_action = QAction("Show Stream window", self, checkable=True, checked=True)
        show_main_action.triggered.connect(lambda checked: self.toggle_window_visibility(checked, self))
        show_stream_action.triggered.connect(lambda checked: self.toggle_window_visibility(checked, self.stream_window))
        
        tts_menu = QMenu("TTS", self)
        tts_bits_action = QAction("Bits", self, checkable=True, checked=True)
        tts_mentions_action = QAction("Mentions", self, checkable=True)
        tts_group = QActionGroup(self)
        tts_group.setExclusive(True)
        tts_group.addAction(tts_bits_action)
        tts_group.addAction(tts_mentions_action)
        tts_menu.addAction(tts_bits_action)
        tts_menu.addAction(tts_mentions_action)
        
        profiles_menu = QMenu("Profiles", self)
        default_profile_action = QAction("Default", self)
        stored_profile_action = QAction("My stored profile", self)
        new_profile_action = QAction("New profile", self)
        duplicate_profile_action = QAction("Duplicate profile", self)
        profiles_menu.addAction(default_profile_action)
        profiles_menu.addAction(stored_profile_action)
        profiles_menu.addSeparator()
        profiles_menu.addAction(new_profile_action)
        profiles_menu.addAction(duplicate_profile_action)

        current_profile_settings_action = QAction("Profile Settings", self)
        current_profile_settings_action.triggered.connect(self.open_profile_settings)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        
        tray_menu.addAction(show_main_action)
        tray_menu.addAction(show_stream_action)
        tray_menu.addMenu(tts_menu)
        tray_menu.addMenu(profiles_menu)
        tray_menu.addAction(current_profile_settings_action)
        tray_menu.addAction(settings_action)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.show_main_action = show_main_action
        self.show_stream_action = show_stream_action

    # ... (toggle_window_visibility as before)
    def toggle_window_visibility(self, checked, window):
        if checked:
            window.show()
            if self.isVisible() and self.stream_window.isVisible(): 
                self.update_stream_window()
        else: 
            window.hide()
        if window == self: 
            self.show_stream_action.setChecked(self.stream_window.isVisible())
        else: 
            self.show_main_action.setChecked(self.isVisible())
            
    def _update_preview_label_text(self, text):
        if self.header_preview_label and self.header_preview_container:
            self.header_preview_label.setText(text)
            # Get width from container if it's visible and laid out, otherwise use main window width
            container_width = self.width() 
            if self.header_preview_container.isVisible() and self.header_preview_container.layout() is not None and self.header_preview_container.width() > 0 :
                container_width = self.header_preview_container.width()
            
            label_width = max(1, container_width - (2 * self.status_bar_internal_margin))
            self.header_preview_label.setFixedWidth(label_width)
            # Optionally, ensure the label can wrap text if it's too long for the fixed width
            self.header_preview_label.setWordWrap(True) 


    # ... (move_to_top_right, create_button, etc. as before)
    def move_to_top_right(self):
        screen_geo = QApplication.primaryScreen().geometry()
        x = screen_geo.width() - self.width() - 50 
        y = 50
        self.move(x, y)
        self.update_stream_window()
        
    def create_button(self, text):
        button = QPushButton(text)
        button.setFixedHeight(self.button_height)
        button.setFixedWidth(self.button_height)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.button_color.name()}; color: {self.button_text_color.name()};
                border: none; border-radius: 5px; padding: 2px; font-size: {self.icon_size}px;
            }}
            QPushButton:hover {{ background-color: {self.button_color.lighter(110).name()}; }}
            QPushButton:pressed {{ background-color: {self.button_color.darker(110).name()}; }}
            QPushButton:checked {{ background-color: {self.button_color.lighter(120).name()}; }}
        """)
        button.setFont(self.button_font)
        self.buttons.append(button)
        return button
        
    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"color: {self.button_text_color.name()}; font-size: {self.icon_size}px;")
        label.setFont(self.button_font)
        self.labels.append(label)
        return label
        
    def create_checkbox(self, text):
        checkbox = QCheckBox(text)
        checkbox.setFixedHeight(self.button_height)
        checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {self.button_text_color.name()}; background-color: {self.button_color.name()};
                border: none; border-radius: 5px; padding: 12px; font-size: 16px; spacing: 0;
            }}
            QCheckBox::indicator {{ width: 0px; height: 0px; }}
        """)
        checkbox.setFont(self.button_font)
        self.checkboxes.append(checkbox)
        return checkbox
        
    def update_button_styles(self):
        style_sheet = f"""
            QPushButton {{
                background-color: {self.button_color.name()}; color: {self.button_text_color.name()};
                border: none; border-radius: 5px; padding: 5px; 
            }}
            QPushButton:hover {{ background-color: {self.button_color.lighter(110).name()}; }}
            QPushButton:pressed {{ background-color: {self.button_color.darker(110).name()}; }}
            QPushButton:checked {{ background-color: {self.button_color.lighter(120).name()}; }}
        """
        checkbox_style_sheet = f"""
            QCheckBox {{
                color: {self.button_text_color.name()}; background-color: {self.button_color.name()};
                border: none; border-radius: 5px; padding: 0 10px; 
            }}
            QCheckBox::indicator {{ width: 0px; height: 0px; }}
        """
        label_style_sheet = f"color: {self.button_text_color.name()};"
        for button in self.buttons: 
            button.setStyleSheet(style_sheet)
            button.setFont(self.button_font)
        for label in self.labels: 
            label.setStyleSheet(label_style_sheet)
            label.setFont(self.button_font)
        for checkbox in self.checkboxes: 
            checkbox.setStyleSheet(checkbox_style_sheet)
            checkbox.setFont(self.button_font)
        self.update()
        if hasattr(self, 'stream_window') and self.stream_window: 
            self.stream_window.update()

    def setup_ui(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)
        self.status_bar = QWidget()
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(self.status_bar_internal_margin,self.status_bar_internal_margin,self.status_bar_internal_margin,self.status_bar_internal_margin)
        status_layout.setSpacing(5)
        self.view_toggle = self.create_button("🌀")
        self.obs_status_label = self.create_label(self.obs_controller.status)
        self.viewers_label = self.create_label(self.viewer_controller.count_status)
        self.tts_queue_label = self.create_label(self.tts_controller.queue_status)
        self.time_till_next_label = self.create_label(f"📢: {self.ad_controller.time_till_next_display}")
        status_layout.addWidget(self.view_toggle)
        status_layout.addSpacing(10)
        status_layout.addWidget(self.obs_status_label)
        status_layout.addWidget(self.create_separator())
        status_layout.addWidget(self.viewers_label)
        status_layout.addWidget(self.create_separator())
        status_layout.addWidget(self.tts_queue_label)
        status_layout.addWidget(self.create_separator())
        status_layout.addWidget(self.time_till_next_label)
        status_layout.addSpacing(10)
        self.status_bar.setLayout(status_layout)
        self.status_bar.setFixedHeight(self.actual_status_bar_height)
        self.controls_bar = QWidget()
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(5,5,5,5)
        controls_layout.setSpacing(5)
        ads_group = QWidget()
        ads_layout = QHBoxLayout()
        ads_layout.setContentsMargins(0,0,0,0)
        ads_layout.setSpacing(5)
        ads_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        tts_group = QWidget()
        tts_layout = QHBoxLayout()
        tts_layout.setContentsMargins(0,0,0,0)
        tts_layout.setSpacing(5)
        tts_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        ads_label = self.create_label("📢")
        run_button = self.create_button("▶")
        delay_button = self.create_button("⏳N")
        delay_5min_button = self.create_button("⏳5")
        double_toggle = self.create_checkbox("✖️2")
        tts_label = self.create_label("🗣️")
        play_button = self.create_button("▶")
        stop_button = self.create_button("⏹")
        autoplay_toggle = self.create_checkbox("📜")
        ads_layout.addWidget(ads_label)
        ads_layout.addWidget(run_button)
        ads_layout.addWidget(delay_button)
        ads_layout.addWidget(delay_5min_button)
        ads_layout.addWidget(double_toggle)
        ads_group.setLayout(ads_layout)
        tts_layout.addWidget(tts_label)
        tts_layout.addWidget(play_button)
        tts_layout.addWidget(stop_button)
        tts_layout.addWidget(autoplay_toggle)
        tts_group.setLayout(tts_layout)
        controls_layout.addWidget(ads_group,0,Qt.AlignmentFlag.AlignLeft)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.create_separator())
        controls_layout.addSpacing(10)
        controls_layout.addWidget(tts_group,0,Qt.AlignmentFlag.AlignLeft)
        controls_layout.addStretch()
        self.controls_bar.setLayout(controls_layout)
        self.controls_bar.setFixedHeight(self.button_height + 10)
        self.view_stack = QStackedWidget()
        self.whiteboard = QTextEdit()
        self.whiteboard.setStyleSheet(f"QTextEdit {{ background: transparent; border: none; font-size: {self.whiteboard_font.pointSize()}px; font-family: \"{self.whiteboard_font.family()}\"; padding-top: 10px; }}")
        self.whiteboard.setReadOnly(False)
        self.whiteboard.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.whiteboard.textChanged.connect(self.sync_whiteboard)
        self.whiteboard.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.whiteboard.focusInEvent = lambda e: print("Whiteboard: Focus IN")
        self.whiteboard.focusOutEvent = lambda e: print("Whiteboard: Focus OUT")
        def whiteboard_mouse_press(event): 
            self.whiteboard.setFocus()
            self.activateWindow()
            self.raise_()
            event.accept()
        self.whiteboard.mousePressEvent = whiteboard_mouse_press
        self.view_stack.addWidget(QWidget())
        self.view_stack.addWidget(self.whiteboard)
        self.main_layout.addWidget(self.status_bar)
        self.main_layout.addWidget(self.controls_bar)
        self.main_layout.addWidget(self.view_stack,1)
        self.setLayout(self.main_layout)
        self.view_toggle.clicked.connect(self.toggle_view)
        delay_button.clicked.connect(lambda: self.ad_controller.delay(5))
        delay_5min_button.clicked.connect(lambda: self.ad_controller.delay(5))
        run_button.clicked.connect(self.ad_controller.run)
        double_toggle.stateChanged.connect(self.ad_controller.toggle_double)
        play_button.clicked.connect(self.tts_controller.play)
        stop_button.clicked.connect(self.tts_controller.stop)
        autoplay_toggle.stateChanged.connect(self.tts_controller.toggle_autoplay)

    def toggle_view(self):
        current_index = self.view_stack.currentIndex()
        new_index = 1 - current_index
        self.view_stack.setCurrentIndex(new_index)
        is_chat_view = (new_index == 0)
        self.controls_bar.setVisible(is_chat_view)
        if not is_chat_view: 
            self.whiteboard.setFocus()
            self.activateWindow()
            self.raise_()

    def get_resize_corner(self, pos):
        margin = self.resize_margin
        if pos.x() < margin and pos.y() < margin: 
            return "top_left"
        if pos.x() > self.width() - margin and pos.y() < margin: 
            return "top_right"
        if pos.x() < margin and pos.y() > self.height() - margin: 
            return "bottom_left"
        if pos.x() > self.width() - margin and pos.y() > self.height() - margin: 
            return "bottom_right"
        return None
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.resize_corner = self.get_resize_corner(event.position().toPoint())
            is_on_draggable_bar = False
            if self.header_preview_container and self.header_preview_container.isVisible():
                if self.header_preview_container.geometry().contains(event.position().toPoint()): 
                    is_on_draggable_bar = True
            elif self.status_bar.geometry().contains(event.position().toPoint()): 
                is_on_draggable_bar = True
            if self.resize_corner: 
                self.resizing = True
                self.start_geometry = self.geometry()
                self.drag_start_pos = event.globalPosition().toPoint()
            elif is_on_draggable_bar: 
                self.dragging = True
                self.drag_start_pos = event.globalPosition().toPoint() - self.pos()
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            elif self.view_stack.currentIndex() == 1: 
                self.whiteboard.setFocus()


    def mouseMoveEvent(self, event):
        if self.dragging: 
            self.move(event.globalPosition().toPoint() - self.drag_start_pos)
        elif self.resizing and self.resize_corner:
            dx=event.globalPosition().toPoint().x()-self.drag_start_pos.x()
            dy=event.globalPosition().toPoint().y()-self.drag_start_pos.y()
            new_geo=QRect(self.start_geometry)
            if self.resize_corner=="top_left": 
                new_geo.setTopLeft(new_geo.topLeft()+QPoint(dx,dy))
            elif self.resize_corner=="top_right": 
                new_geo.setTopRight(new_geo.topRight()+QPoint(dx,dy))
            elif self.resize_corner=="bottom_left": 
                new_geo.setBottomLeft(new_geo.bottomLeft()+QPoint(dx,dy))
            elif self.resize_corner=="bottom_right": 
                new_geo.setBottomRight(new_geo.bottomRight()+QPoint(dx,dy))
            
            # Enforce minimum size during resize
            min_w, min_h = 100, 100 # Example minimums
            if new_geo.width() < min_w: new_geo.setWidth(min_w)
            if new_geo.height() < min_h: new_geo.setHeight(min_h)
            
            self.setGeometry(new_geo.normalized())
        else:
            corner = self.get_resize_corner(event.position().toPoint())
            if corner: 
                self.setCursor(Qt.CursorShape.SizeFDiagCursor if corner in ["top_left","bottom_right"] else Qt.CursorShape.SizeBDiagCursor)
            else: 
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: 
            self.dragging=False
            self.resizing=False
            self.resize_corner=None
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def sync_whiteboard(self):
        if hasattr(self,'stream_window') and self.stream_window: 
            content=self.whiteboard.toPlainText()
            self.stream_window.whiteboard.setPlainText(content)
            self.autosave_whiteboard()

    def autosave_whiteboard(self):
        if self._whiteboard_content_path:
            try:
                with open(self._whiteboard_content_path,'w',encoding='utf-8') as f: 
                    f.write(self.whiteboard.toPlainText())
            except Exception as e: 
                print(f"Error saving whiteboard: {e}")

    def open_settings(self):
        if not hasattr(self,"settings_window") or not self.settings_window: 
            self.settings_window=SettingsWindow(self)
        self.center_window(self.settings_window)
        self.settings_window.show()
        self.settings_window.activateWindow()

    def exit_app(self): 
        self.tray_icon.hide()
        QApplication.quit()

    def open_profile_settings(self):
        if not hasattr(self,"profile_settings_window") or not self.profile_settings_window: 
            self.profile_settings_window=ProfileSettingsWindow(self)
        self.center_window(self.profile_settings_window)
        self.profile_settings_window.show()
        self.profile_settings_window.activateWindow()

    def center_window(self,window):
        screen_geo=QApplication.primaryScreen().geometry()
        x=(screen_geo.width()-window.width())//2
        y=(screen_geo.height()-window.height())//2
        window.move(x,y)
        
    def paintEvent(self,event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(),self._background_qcolor)
        if os.path.exists(self._background_image_path):
            renderer=QSvgRenderer(self._background_image_path)
            if renderer.isValid():
                original_size=renderer.defaultSize()
                scaled_width=int(original_size.width()*self._image_scale_modifier)
                scaled_height=int(original_size.height()*self._image_scale_modifier)
                scaled_size=QSize(scaled_width,scaled_height)
                x=(self.width()-scaled_size.width())//2
                y=(self.height()-scaled_size.height())//2
                renderer.render(painter,QRectF(x,y,scaled_size.width(),scaled_size.height()))
                overlay_color_img=QColor(self._background_qcolor)
                overlay_color_img.setAlpha(int(self._background_opacity*255))
                painter.fillRect(QRectF(x,y,scaled_size.width(),scaled_size.height()),overlay_color_img)
        overlay_color_bar=QColor(255,255,255,128)
        is_preview_active = self.header_preview_container and self.header_preview_container.isVisible()
        if self.status_bar.isVisible() and not is_preview_active: 
            task_bar_rect=QRectF(0,0,self.width(),self.actual_status_bar_height)
            painter.fillRect(task_bar_rect,overlay_color_bar)
        if self.controls_bar.isVisible(): 
            controls_y=self.actual_status_bar_height
            controls_rect=QRectF(0,controls_y,self.width(),self.controls_bar.height())
            painter.fillRect(controls_rect,overlay_color_bar)

    def create_separator(self): 
        separator=QLabel("|")
        separator.setStyleSheet(f"color: {self.button_text_color.name()}; font-size: {self.icon_size}px;")
        return separator

    def _get_font_style_css(self,font:QFont):
        weight_map={QFont.Weight.Thin:"100",QFont.Weight.ExtraLight:"200",QFont.Weight.Light:"300",QFont.Weight.Normal:"normal",QFont.Weight.Medium:"500",QFont.Weight.DemiBold:"600",QFont.Weight.Bold:"bold",QFont.Weight.ExtraBold:"800",QFont.Weight.Black:"900"}
        css_weight=f"font-weight: {weight_map.get(font.weight(),'normal')};"
        style_map={QFont.Style.StyleNormal:"normal",QFont.Style.StyleItalic:"italic",QFont.Style.StyleOblique:"oblique"}
        css_style=f"font-style: {style_map.get(font.style(),'normal')};"
        return css_weight,css_style

    def _update_preview_label_style(self):
        if self.header_preview_label and self.stream_window:
            stream_font=self.stream_window.header_font
            stream_color=self.stream_window.header_color
            css_weight,css_style=self._get_font_style_css(stream_font)
            self.header_preview_label.setStyleSheet(f"""QLabel {{color: {stream_color.name()}; font-size: {stream_font.pointSize()}px; font-family: \"{stream_font.family()}\"; {css_weight} {css_style} padding: 0; margin: 0; background: transparent; height: {self.button_height}px; line-height: {self.button_height}px;}}""")
            self.header_preview_label.setAlignment(self.stream_window.header_alignment)

    def show_header_preview(self):
        if not self.header_preview_container:
            self.header_preview_container=QWidget()
            self.header_preview_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.header_preview_container.setFixedHeight(self.actual_status_bar_height)
            
            preview_layout=QHBoxLayout(self.header_preview_container)
            preview_layout.setContentsMargins(self.status_bar_internal_margin,self.status_bar_internal_margin,self.status_bar_internal_margin,self.status_bar_internal_margin)
            preview_layout.setSpacing(0)
            self.header_preview_container.setStyleSheet("QWidget { background-color: rgba(255,255,255,128); }")
            
            self.header_preview_label=QLabel("",self.header_preview_container)
            self.header_preview_label.setFixedHeight(self.button_height)
            self.header_preview_label.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed) 
            self.header_preview_label.setTextFormat(Qt.TextFormat.PlainText)
            self.header_preview_label.setWordWrap(True) # Allow label to wrap if text is too long for its fixed width
            preview_layout.addWidget(self.header_preview_label)

        if self._original_status_bar_widget is None: 
            self._original_status_bar_widget=self.status_bar
            self._status_bar_index_in_layout=self.main_layout.indexOf(self.status_bar)
        if self.status_bar.isVisible(): 
            self.main_layout.removeWidget(self.status_bar)
            self.status_bar.hide()
        if self.main_layout.indexOf(self.header_preview_container)==-1: 
            self.main_layout.insertWidget(self._status_bar_index_in_layout,self.header_preview_container)
        
        self.header_preview_container.show() 
        self.header_preview_container.raise_()
        QApplication.processEvents() 

        self._update_preview_label_text(self.stream_window.header_text) 
        self._update_preview_label_style()
        QApplication.processEvents()

    def hide_header_preview(self):
        if self.header_preview_container and self.header_preview_container.isVisible():
            self.main_layout.removeWidget(self.header_preview_container)
            self.header_preview_container.hide()
            if self._original_status_bar_widget:
                if self.main_layout.indexOf(self._original_status_bar_widget)==-1: 
                    self.main_layout.insertWidget(self._status_bar_index_in_layout,self._original_status_bar_widget)
                self._original_status_bar_widget.show()
            QApplication.processEvents()
            self.update()

class StreamWindow(QWidget):
    def __init__(self, main_window_ref=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self._image_scale_modifier = 0.22
        self._background_opacity = 0.5
        self._background_qcolor = QColor('#EBECE9')
        self._background_image_path = "img/bg.svg"
        self.main_window_ref = main_window_ref
        if self.main_window_ref:
            self.header_content_height = self.main_window_ref.button_height
            self.header_margin = self.main_window_ref.status_bar_internal_margin
            self.actual_header_height = self.main_window_ref.actual_status_bar_height
            self._default_window_size = self.main_window_ref._default_window_size
        else:
            self.header_content_height = 32
            self.header_margin = 5
            self.actual_header_height = 42
            self._default_window_size = (400, 400)
        self.header_text = "📝 Whiteboard"
        self.header_font = QFont("Arial", 12)
        self.header_font.setBold(True)
        self.header_color = QColor("navy")
        self.header_alignment = Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        self.setup_ui()
        self.resize(*self._default_window_size)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(self.actual_header_height)
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(self.header_margin, self.header_margin, self.header_margin, self.header_margin)
        header_layout.setSpacing(0)
        self.status_label = QLabel(self.header_text)
        self.status_label.setFixedHeight(self.header_content_height)
        self.status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.status_label.setTextFormat(Qt.TextFormat.PlainText)
        header_layout.addWidget(self.status_label)
        self.whiteboard = QTextEdit()
        self.whiteboard.setStyleSheet(f"QTextEdit {{ background: transparent; border: none; font-size: 14px; padding-top: 10px; }}")
        self.whiteboard.setReadOnly(True)
        self.whiteboard.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.whiteboard.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        # Set a minimum width for the QTextEdit to prevent it from collapsing too much
        # This can be adjusted, but ensures it has *some* width for document layout.
        self.whiteboard.setMinimumWidth(10) 
        layout.addWidget(self.header_widget)
        layout.addWidget(self.whiteboard, 1)
        self.setLayout(layout)
        self.update_header_font(self.header_font)
        self.update_header_color(self.header_color)
        self.update_header_alignment(self.header_alignment)

    def update_whiteboard_document_width(self):
        if hasattr(self, 'whiteboard') and self.whiteboard and self.whiteboard.viewport():
            # Use viewport width for text area; it excludes scrollbars if any
            doc_width = self.whiteboard.viewport().width() 
            # Only set if positive, -1 means no constraint / auto
            self.whiteboard.document().setTextWidth(doc_width if doc_width > 0 else -1) 

    def _get_font_style_css_for_stream(self, font:QFont):
        weight_map={QFont.Weight.Thin:"100",QFont.Weight.ExtraLight:"200",QFont.Weight.Light:"300",QFont.Weight.Normal:"normal",QFont.Weight.Medium:"500",QFont.Weight.DemiBold:"600",QFont.Weight.Bold:"bold",QFont.Weight.ExtraBold:"800",QFont.Weight.Black:"900"}
        css_weight=f"font-weight: {weight_map.get(font.weight(),'normal')};"
        style_map={QFont.Style.StyleNormal:"normal",QFont.Style.StyleItalic:"italic",QFont.Style.StyleOblique:"oblique"}
        css_style=f"font-style: {style_map.get(font.style(),'normal')};"
        return css_weight,css_style
        
    def update_header_alignment(self, alignment): 
        self.header_alignment=alignment|Qt.AlignmentFlag.AlignVCenter
        self.status_label.setAlignment(self.header_alignment)

    def update_header(self, text): 
        self.header_text=text
        self.status_label.setText(text)

    def _apply_header_style(self):
        css_weight,css_style=self._get_font_style_css_for_stream(self.header_font)
        self.status_label.setStyleSheet(f"""QLabel {{color: {self.header_color.name()}; font-size: {self.header_font.pointSize()}px; font-family: \"{self.header_font.family()}\"; {css_weight} {css_style} padding:0; margin:0; background:transparent; height:{self.header_content_height}px; line-height:{self.header_content_height}px;}}""")
        self.status_label.setAlignment(self.header_alignment)

    def update_header_font(self, font): 
        self.header_font=font
        self._apply_header_style()

    def update_header_color(self, color): 
        self.header_color=color
        self._apply_header_style()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self,'status_label') and hasattr(self,'header_margin'): 
            self.status_label.setFixedWidth(max(1,self.width()-(2*self.header_margin)))
        self.update_whiteboard_document_width() # Key call

    def paintEvent(self, event):
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(),self._background_qcolor)
        if os.path.exists(self._background_image_path):
            renderer=QSvgRenderer(self._background_image_path)
            if renderer.isValid():
                original_size=renderer.defaultSize()
                scaled_width=int(original_size.width()*self._image_scale_modifier)
                scaled_height=int(original_size.height()*self._image_scale_modifier)
                scaled_size=QSize(scaled_width,scaled_height)
                x=(self.width()-scaled_size.width())//2
                y=(self.height()-scaled_size.height())//2
                renderer.render(painter,QRectF(x,y,scaled_size.width(),scaled_size.height()))
                overlay_color_img=QColor(self._background_qcolor)
                overlay_color_img.setAlpha(int(self._background_opacity*255))
                painter.fillRect(QRectF(x,y,scaled_size.width(),scaled_size.height()),overlay_color_img)
        header_rect=QRectF(0,0,self.width(),self.actual_header_height)
        overlay_color_bar=QColor(255,255,255,128)
        painter.fillRect(header_rect,overlay_color_bar)

class SettingsWindow(QDialog): # Assumed correct from previous, no changes needed for reported issues
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(550,450)
        layout=QVBoxLayout(self)
        layout.setSpacing(15)
        self.chat_overlay_group=self.create_chat_overlay_group()
        layout.addWidget(self.chat_overlay_group)
        self.account_group=self.create_account_group()
        layout.addWidget(self.account_group)
        button_layout=QHBoxLayout()
        button_layout.addStretch()
        close_button=QPushButton("Close")
        close_button.setFixedHeight(35)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
    def create_chat_overlay_group(self):
        group=QGroupBox("Chat Overlay"); layout=QVBoxLayout(group)
        self.chat_font_button=QPushButton("Change Chat Font"); self.chat_font_button.setFixedSize(200,30); self.chat_font_button.clicked.connect(self.change_chat_font)
        layout.addWidget(self.chat_font_button,alignment=Qt.AlignmentFlag.AlignCenter)
        self.tts_font_button=QPushButton("Change TTS Font"); self.tts_font_button.setFixedSize(200,30); self.tts_font_button.clicked.connect(self.change_tts_font)
        layout.addWidget(self.tts_font_button,alignment=Qt.AlignmentFlag.AlignCenter); return group
    def change_chat_font(self):
        font,ok=QFontDialog.getFont(self.parent().chat_font,self,"Select Chat Font")
        if ok: self.parent().chat_font=font; print(f"Chat font changed to: {font.family()}, size: {font.pointSize()}")
    def change_tts_font(self):
        font,ok=QFontDialog.getFont(self.parent().tts_font,self,"Select TTS Font")
        if ok: self.parent().tts_font=font; print(f"TTS font changed to: {font.family()}, size: {font.pointSize()}")
    def create_account_group(self):
        group=QGroupBox("Account Setup"); layout=QVBoxLayout(group)
        self.twitch_url_input=QLineEdit(); self.twitch_url_input.setPlaceholderText("Twitch Channel URL"); self.twitch_url_input.setFixedHeight(30); layout.addWidget(self.twitch_url_input)
        self.twitch_auth_input=QLineEdit(); self.twitch_auth_input.setPlaceholderText("Twitch Authentication Token"); self.twitch_auth_input.setFixedHeight(30)
        self.twitch_auth_input.setEchoMode(QLineEdit.EchoMode.Password); layout.addWidget(self.twitch_auth_input); return group

class ProfileSettingsWindow(QDialog): # Minor adjustments to _check_hide_preview logic
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Profile Settings"); self.setMinimumSize(550, 650)
        self.main_win = parent
        self._original_button_color = self.main_win.button_color if self.main_win else QColor("white")
        self._active_dialog = None; self._last_focused_control = None
        if self.main_win and hasattr(self.main_win,'stream_window'):
            self.header_font = self.main_win.stream_window.header_font; self.header_color = self.main_win.stream_window.header_color
            self.header_alignment = self.main_win.stream_window.header_alignment
        else:
            self.header_font = QFont("Arial",12); self.header_font.setBold(True); self.header_color = QColor("navy")
            self.header_alignment = Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter
        main_layout=QVBoxLayout(self);main_layout.setSpacing(15)
        name_layout=QHBoxLayout();name_layout.addWidget(QLabel("Name:"));self.name_input=QLineEdit();self.name_input.setPlaceholderText("Profile Name");self.name_input.setFixedHeight(30);name_layout.addWidget(self.name_input);main_layout.addLayout(name_layout)
        header_group=QGroupBox("Whiteboard Header");header_group.setObjectName("Whiteboard Header");header_layout=QVBoxLayout(header_group)
        self.header_text_input=QTextEdit();self.header_text_input.setPlaceholderText("Enter header text (up to 200 characters)");self.header_text_input.setMaximumHeight(60)
        self.header_text_input.focusInEvent=self.handle_header_control_focus_in;self.header_text_input.focusOutEvent=self.handle_header_control_focus_out;header_layout.addWidget(self.header_text_input)
        font_layout=QHBoxLayout();self.header_font_button=QPushButton("Change Header Font");self.header_font_button.setFixedSize(200,30);self.header_font_button.clicked.connect(self.change_header_font)
        self.header_font_button.focusInEvent=self.handle_header_control_focus_in;self.header_font_button.focusOutEvent=self.handle_header_control_focus_out;font_layout.addWidget(self.header_font_button)
        self.header_color_button=QPushButton("Pick Header Color");self.header_color_button.setFixedSize(200,30);self.header_color_button.clicked.connect(self.pick_header_color)
        self.header_color_button.focusInEvent=self.handle_header_control_focus_in;self.header_color_button.focusOutEvent=self.handle_header_control_focus_out;font_layout.addWidget(self.header_color_button);font_layout.addStretch();header_layout.addLayout(font_layout)
        align_layout=QHBoxLayout();align_layout.addWidget(QLabel("Alignment:"));self.align_left=QRadioButton("Left");self.align_center=QRadioButton("Center");self.align_right=QRadioButton("Right")
        if self.header_alignment&Qt.AlignmentFlag.AlignLeft:self.align_left.setChecked(True)
        elif self.header_alignment&Qt.AlignmentFlag.AlignRight:self.align_right.setChecked(True)
        else:self.align_center.setChecked(True)
        for btn in[self.align_left,self.align_center,self.align_right]:btn.toggled.connect(self.on_alignment_changed);btn.focusInEvent=self.handle_header_control_focus_in;btn.focusOutEvent=self.handle_header_control_focus_out;align_layout.addWidget(btn)
        align_layout.addStretch();header_layout.addLayout(align_layout);main_layout.addWidget(header_group)
        if self.main_win and hasattr(self.main_win,'stream_window'):self.header_text_input.setPlainText(self.main_win.stream_window.header_text)
        self.header_text_input.textChanged.connect(self.on_header_text_changed)
        button_style_group=QGroupBox("Button Styling");button_style_layout=QVBoxLayout(button_style_group);button_color_layout=QHBoxLayout()
        self.button_color_button=QPushButton("Pick Button Color");self.button_color_button.setFixedSize(220,30);self.button_color_button.clicked.connect(self.pick_button_color)
        self.sync_with_bg_checkbox=QCheckBox("Same as background");self.sync_with_bg_checkbox.stateChanged.connect(self.toggle_sync_with_bg)
        button_color_layout.addWidget(self.button_color_button);button_color_layout.addWidget(self.sync_with_bg_checkbox);button_color_layout.addStretch();button_style_layout.addLayout(button_color_layout)
        self.text_color_button=QPushButton("Pick Text Color");self.text_color_button.setFixedSize(220,30);self.text_color_button.clicked.connect(self.pick_text_color);button_style_layout.addWidget(self.text_color_button)
        self.font_button=QPushButton("Change Button Font");self.font_button.setFixedSize(220,30);self.font_button.clicked.connect(self.change_button_font);button_style_layout.addWidget(self.font_button);main_layout.addWidget(button_style_group)
        self.background_group=self.create_background_group();main_layout.addWidget(self.background_group)
        self.whiteboard_font_button=QPushButton("Change Whiteboard Font");self.whiteboard_font_button.setFixedSize(220,30);self.whiteboard_font_button.clicked.connect(self.change_whiteboard_font);main_layout.addWidget(self.whiteboard_font_button,alignment=Qt.AlignmentFlag.AlignLeft)
        close_button_layout=QHBoxLayout();close_button_layout.addStretch();close_button=QPushButton("Close");close_button.setFixedHeight(35);close_button.clicked.connect(self.accept);close_button_layout.addWidget(close_button);close_button_layout.addStretch();main_layout.addLayout(close_button_layout)

    def handle_header_control_focus_in(self,event):
        sender_widget=self.sender()
        if sender_widget:
            self._last_focused_control=sender_widget
        QApplication.processEvents() # Ensure UI is up-to-date before showing preview
        if self.main_win:
            self.main_win.show_header_preview()

    def handle_header_control_focus_out(self,event):
        QTimer.singleShot(10,self._check_hide_preview) 
        
    def _check_hide_preview(self):
        # If a dialog initiated by this window is active, don't hide the preview.
        if self._active_dialog and self._active_dialog.isVisible():
            return

        focused_widget = QApplication.focusWidget()
        header_group = self.findChild(QGroupBox,"Whiteboard Header")

        # If focus is still within any control of the header group, keep the preview.
        if header_group and focused_widget and header_group.isAncestorOf(focused_widget):
            return
        
        # If focus is somewhere else, hide the preview.
        if self.main_win:
            # A more direct check: if current focus is NOT a child of ProfileSettingsWindow's header group,
            # AND not the active dialog, then hide.
            # The main_window's eventFilter handles clicks completely outside.
            # This _check_hide_preview is more about focus *leaving* the header group *within* ProfileSettings.
            if not (header_group and focused_widget and header_group.isAncestorOf(focused_widget)):
                 self.main_win.hide_header_preview()


    def on_header_text_changed(self):
        text=self.header_text_input.toPlainText()
        if len(text)>200:
            text=text[:200]
            cursor=self.header_text_input.textCursor()
            cursor.beginEditBlock()
            self.header_text_input.setPlainText(text)
            cursor.setPosition(len(text))
            cursor.endEditBlock()
        if self.main_win and hasattr(self.main_win,'stream_window') and self.main_win.stream_window:
            self.main_win.stream_window.update_header(text)
        if self.main_win and self.main_win.header_preview_container and self.main_win.header_preview_container.isVisible():
            self.main_win._update_preview_label_text(text)

    def on_alignment_changed(self,checked):
        if not checked:
            return
        rb=self.sender()
        if rb==self.align_left:
            self.header_alignment=Qt.AlignmentFlag.AlignLeft
        elif rb==self.align_center:
            self.header_alignment=Qt.AlignmentFlag.AlignHCenter
        elif rb==self.align_right:
            self.header_alignment=Qt.AlignmentFlag.AlignRight
        self.header_alignment|=Qt.AlignmentFlag.AlignVCenter
        if self.main_win and hasattr(self.main_win,'stream_window') and self.main_win.stream_window:
            self.main_win.stream_window.update_header_alignment(self.header_alignment)
        if self.main_win and self.main_win.header_preview_container and self.main_win.header_preview_container.isVisible():
            self.main_win._update_preview_label_style()
                
    def _open_live_update_dialog(self, dialog_type, current_value, update_method, live_update_method, title, calling_button):
        if not self.main_win: 
            return
        
        is_header_control = calling_button in [self.header_font_button, self.header_color_button]
        if is_header_control:
            self.main_win.show_header_preview()

        dialog = dialog_type(current_value, self)
        dialog.setWindowTitle(title)
        
        original_value = None
        if dialog_type == QFontDialog:
            dialog.currentFontChanged.connect(live_update_method)
            original_value = QFont(current_value)
        elif dialog_type == QColorDialog:
            dialog.currentColorChanged.connect(live_update_method)
            original_value = QColor(current_value)

        self._last_focused_control = calling_button
        self._active_dialog = dialog # Set before exec
        
        accepted = dialog.exec()
        self._active_dialog = None # Clear after exec

        if accepted:
            selected_value = None
            if dialog_type == QFontDialog: 
                selected_value = dialog.selectedFont()
            elif dialog_type == QColorDialog: 
                selected_value = dialog.selectedColor()
            if selected_value:
                update_method(selected_value)
        else: 
            if original_value:
                live_update_method(original_value)

        if self._last_focused_control: 
            # Ensure last_focused_control is still valid and can receive focus
            if self._last_focused_control.isVisible() and self._last_focused_control.isEnabled():
                 self._last_focused_control.setFocus()
        
        # Only re-check hiding for header controls to avoid hiding preview unnecessarily for other dialogs
        if is_header_control:
             QTimer.singleShot(0, self._check_hide_preview)


    def change_header_font(self):
        self._open_live_update_dialog(QFontDialog, self.header_font, self._set_final_header_font, self._live_update_header_font, "Select Header Font", self.header_font_button)

    def _set_final_header_font(self, font): 
        self.header_font = font
        self._live_update_header_font(font)

    def _live_update_header_font(self, font):
        if self.main_win and hasattr(self.main_win,'stream_window'): 
            self.main_win.stream_window.update_header_font(font)
        if self.main_win and self.main_win.header_preview_container and self.main_win.header_preview_container.isVisible(): 
            self.main_win._update_preview_label_style()

    def pick_header_color(self):
        self._open_live_update_dialog(QColorDialog, self.header_color, self._set_final_header_color, self._live_update_header_color, "Pick Header Color", self.header_color_button)

    def _set_final_header_color(self, color): 
        self.header_color = color
        self._live_update_header_color(color)

    def _live_update_header_color(self, color):
        if self.main_win and hasattr(self.main_win,'stream_window'): 
            self.main_win.stream_window.update_header_color(color)
        if self.main_win and self.main_win.header_preview_container and self.main_win.header_preview_container.isVisible(): 
            self.main_win._update_preview_label_style()

    def pick_button_color(self):
        if not self.sync_with_bg_checkbox.isChecked():
            self._open_live_update_dialog(QColorDialog, self.main_win.button_color, self._set_final_button_color, self._live_update_button_color, "Pick Button Color", self.button_color_button)

    def _set_final_button_color(self, color): 
        self._original_button_color = QColor(color)
        self._live_update_button_color(color)

    def _live_update_button_color(self, color):
        if self.main_win and color.isValid(): 
            self.main_win.button_color = color
            self.main_win.update_button_styles()

    def pick_text_color(self):
        self._open_live_update_dialog(QColorDialog, self.main_win.button_text_color, self._set_final_text_color, self._live_update_text_color, "Pick Text Color", self.text_color_button)

    def _set_final_text_color(self, color): 
        self._live_update_text_color(color)

    def _live_update_text_color(self, color):
        if self.main_win and color.isValid(): 
            self.main_win.button_text_color = color
            self.main_win.update_button_styles()
        
    def change_button_font(self):
        self._open_live_update_dialog(QFontDialog, self.main_win.button_font, self._set_final_button_font, self._live_update_button_font, "Change Button Font", self.font_button)

    def _set_final_button_font(self, font): 
        self._live_update_button_font(font)

    def _live_update_button_font(self, font):
        if self.main_win: 
            self.main_win.button_font = font
            self.main_win.update_button_styles()

    def pick_bg_color(self):
        self._open_live_update_dialog(QColorDialog, self.main_win._background_qcolor, self._set_final_bg_color, self._live_update_bg_color, "Pick Background Color", self.bg_color_button)

    def _set_final_bg_color(self, color): 
        self._live_update_bg_color(color)

    def _live_update_bg_color(self, color):
        if self.main_win and color.isValid():
            self.main_win._background_qcolor = color
            self.main_win.update()
            if hasattr(self.main_win,'stream_window'): 
                self.main_win.stream_window._background_qcolor = color
                self.main_win.stream_window.update()
            if self.sync_with_bg_checkbox.isChecked(): 
                self.main_win.button_color = QColor(color)
                self.main_win.update_button_styles()

    def change_whiteboard_font(self):
        self._open_live_update_dialog(QFontDialog, self.main_win.whiteboard_font, self._set_final_whiteboard_font, self._live_update_whiteboard_font, "Change Whiteboard Font", self.whiteboard_font_button)

    def _set_final_whiteboard_font(self, font): 
        self._live_update_whiteboard_font(font)

    def _live_update_whiteboard_font(self, font):
        if self.main_win:
            self.main_win.whiteboard_font = font
            style_sheet = f"background:transparent;border:none;font-size:{font.pointSize()}px;font-family:\"{font.family()}\";padding-top:10px;"
            self.main_win.whiteboard.setStyleSheet(f"QTextEdit {{{style_sheet}}}")
            if hasattr(self.main_win,'stream_window'): 
                self.main_win.stream_window.whiteboard.setStyleSheet(f"QTextEdit {{{style_sheet}}}")

    def closeEvent(self,event):
        if self.main_win:
            self.main_win.hide_header_preview()
        super().closeEvent(event)

    def toggle_sync_with_bg(self,state):
        _ = None 
        if state: 
            _ = QColor(self.main_win.button_color)
            self._original_button_color = _
            self.main_win.button_color = QColor(self.main_win._background_qcolor)
            self.button_color_button.setEnabled(False)
        else:
            if self._original_button_color is not None: 
                self.main_win.button_color = QColor(self._original_button_color)
            self.button_color_button.setEnabled(True)
        self.main_win.update_button_styles()

    def create_background_group(self):
        group=QGroupBox("Background")
        layout=QVBoxLayout(group)
        self.bg_color_button=QPushButton("Pick Background Color")
        self.bg_color_button.clicked.connect(self.pick_bg_color)
        layout.addWidget(self.bg_color_button)
        self.image_button=QPushButton("Select Background Image")
        self.image_button.setFixedSize(220,30)
        self.image_button.clicked.connect(self.select_image)
        layout.addWidget(self.image_button)
        self.scale_slider=QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(1,100)
        self.scale_slider.setValue(int(self.main_win._image_scale_modifier*100 if self.main_win else 22))
        self.scale_slider.setFixedWidth(200)
        self.scale_slider.valueChanged.connect(self.update_image_scale)
        layout.addWidget(QLabel("Scale Image:"))
        layout.addWidget(self.scale_slider)
        self.opacity_slider=QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0,100)
        self.opacity_slider.setValue(int(self.main_win._background_opacity*100 if self.main_win else 50))
        self.opacity_slider.setFixedWidth(200)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        layout.addWidget(QLabel("Image Opacity:"))
        layout.addWidget(self.opacity_slider)
        return group

    def update_image_scale(self,value):
        scale=value/100.0
        if self.main_win:
            self.main_win._image_scale_modifier=scale
            self.main_win.update()
            if hasattr(self.main_win,'stream_window'):
                self.main_win.stream_window._image_scale_modifier=scale
                self.main_win.stream_window.update()

    def update_opacity(self,value):
        opacity=value/100.0
        if self.main_win:
            self.main_win._background_opacity=opacity
            self.main_win.update()
            if hasattr(self.main_win,'stream_window'):
                self.main_win.stream_window._background_opacity=opacity
                self.main_win.stream_window.update()

    def select_image(self):
        path,_=QFileDialog.getOpenFileName(self,"Select Background Image","","Images (*.png *.jpg *.jpeg *.bmp *.svg)")
        if path and self.main_win:
            self.main_win._background_image_path=path
            self.main_win.update()
            if hasattr(self.main_win,'stream_window'):
                self.main_win.stream_window._background_image_path=path
                self.main_win.stream_window.update()


if __name__ == "__main__":
    os.makedirs("img", exist_ok=True)
    dummy_svg_content = '<svg width="10" height="10"><rect width="10" height="10" style="fill:rgb(0,0,255);" /></svg>'
    if not os.path.exists("img/bg.svg"):
        with open("img/bg.svg", "w") as f: 
            f.write(dummy_svg_content)
    if not os.path.exists("img/tray_icon.svg"):
        with open("img/tray_icon.svg", "w") as f: 
            f.write(dummy_svg_content)

    app = QApplication(sys.argv)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())