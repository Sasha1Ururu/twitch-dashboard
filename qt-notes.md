## Qt Version-Specific Notes

### PyQt6 Import Changes
1. QtCore
   + `QPoint`, `QSize`, `QRectF` moved to `PyQt6.QtCore`
   + `Qt` enum values moved to `PyQt6.QtCore.Qt`

2. QtGui
   + `QColor`, `QPainter`, `QIcon`, `QPixmap`, `QAction`, `QFont` moved to `PyQt6.QtGui`
   + `QKeySequence` moved to `PyQt6.QtGui`

3. QtWidgets
   + All widget classes moved to `PyQt6.QtWidgets`
   + Dialog classes (`QDialog`, `QColorDialog`, `QFontDialog`, `QFileDialog`) moved to `PyQt6.QtWidgets`

4. QtSvg
   + `QSvgRenderer` moved to `PyQt6.QtSvg`

### Version Compatibility
1. PyQt6 vs PyQt5
   + PyQt6 requires explicit imports from correct modules
   + Some enum values have been renamed or moved
   + Signal/slot connections use different syntax
   + Some widget properties and methods have changed

2. Linux-specific Issues
   + Window flags behavior differs between X11 and Wayland
   + `X11BypassWindowManagerHint` may not work on Wayland
   + Tray icon implementation varies between desktop environments

3. SVG Handling
   + SVG rendering requires explicit painter setup
   + SVG scaling and positioning must be handled manually
   + SVG opacity requires separate color channel management


## Qt Implementation Notes

### Window Management Issues
1. Stay-on-Top Behavior
   + Window flags must be set before window creation
   + `WindowStaysOnTopHint` alone is insufficient
   + Requires combination with `FramelessWindowHint` and `X11BypassWindowManagerHint`
   + Needs periodic reactivation (1s timer) to maintain top position
   + Must use both `raise_()` and `showNormal()` for reliable positioning

2. Window Dragging
   + Custom implementation required for frameless windows
   + Must track both press and move events
   + Need to handle edge cases (window boundaries)
   + Must update position manually using `move()`

3. Window Resizing
   + Custom implementation needed for frameless windows
   + Must track resize direction and handle edge cases
   + Need to manage minimum window size
   + Must update size and position manually

### UI Styling Issues
1. Style Updates
   + Style changes don't apply immediately to existing widgets
   + Must manually update all affected widgets
   + Need to maintain separate lists of buttons, labels, checkboxes
   + Style updates require explicit widget updates

2. Font Management
   + Font changes require explicit application to each widget type
   + Must handle font changes for buttons, labels, checkboxes separately
   + Font updates need to be propagated to all related widgets
   + Font dialog requires manual centering

3. Color Management
   + Color changes require explicit widget updates
   + Color dialog requires manual centering
   + Need to handle color synchronization between elements
   + Must manage opacity through separate color channels

### Dialog Window Issues
1. Parent-Child Relationships
   + Dialogs must be centered manually
   + Need to handle parent window relationships carefully
   + Must manage dialog modality
   + Need to handle dialog closing events

2. File Dialog
   + Must set appropriate file filters
   + Need to handle file selection validation
   + Must manage file path updates

### System Integration Issues
1. Tray Icon
   + SVG icons need manual rendering to pixmap
   + Must handle icon updates manually
   + Menu actions need explicit connections
   + Need to handle tray icon visibility

2. Screen Geometry
   + Screen geometry must be queried manually
   + Need to handle multi-monitor setups explicitly
   + Window centering requires manual calculation
   + Must handle screen resolution changes

### Event Handling Issues
1. Mouse Events
   + Must handle both press and release events
   + Need to track mouse position for dragging
   + Must handle edge cases in resize operations
   + Need to manage event propagation

2. Timer Events
   + Must handle timer cleanup
   + Need to manage timer intervals
   + Must handle timer state changes

### Signal/Slot Issues
1. Connections
   + Must handle signal disconnection
   + Need to manage multiple connections
   + Must handle connection cleanup
   + Need to handle signal blocking

2. State Management
   + Must handle state changes properly
   + Need to manage state synchronization
   + Must handle state persistence
   + Need to handle state restoration


