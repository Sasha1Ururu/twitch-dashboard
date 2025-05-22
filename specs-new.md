Two levels to store various settings: Profile and Settings.
Note that Whiteboard font settings are stored in Profile, and Chat font settings are stored globally - in the Settings.
Also for all service/tool windows (all not the main 2 windows) - they must spawn in the center of the screen.
in UI: use "✓" instead of "enabled" and "⨯" instead of "disabled" in yes/no toggles


# User Interface

## Views:
+ Chat view
+ Whiteboard view

### Chat view
Displays chat web page via QtWebEngine. Url for channel is set up in Settings.
Chat view itself is uninteraclable (except task bars).

### Whiteboard view
A simple WYSIWYG text editor with autosave. Contents and font settings are saved in Profile instance.
- Stream Window is read-only and used only for OBS capture
- Main Window has a view toggle button "🌀" to switch between Chat and Whiteboard views
- Whiteboard view in Main Window is the only place where text can be edited
- Any text edits in Main Window's Whiteboard view must be instantly reflected in Stream Window
- No delay is allowed between Main Window edits and Stream Window updates
- Stream Window must always display the current state of the Whiteboard

#### Whiteboard Header & Header Preview Mode
The header is a configurable element that appears in both Stream Window and Main Window. It can be customized through Profile Settings and previewed in real-time.

##### Header Configuration
- Header text is editable in Profile Settings
- Header properties (font, color, alignment) are configurable in Profile Settings
- All header settings are stored in the active profile
- Header must maintain consistent appearance across both windows

##### Header Preview Mode
- Activates automatically when any header control in Profile Settings gains focus
- Replaces the status bar in Main Window with a header preview
- Deactivates when focus moves outside the header area
- Must maintain pixel-perfect consistency with Stream Window header

##### Visual Requirements
- Header preview must use identical margins and padding as Stream Window header (5px)
- No visual jumping during transitions between status bar and header preview
- Header preview must maintain fixed width to prevent window resizing
- Header preview must preserve all styling properties (font, color, alignment)

##### Focus Management
- Focus must be maintained when interacting with header controls (font picker, color picker)
- Focus must be restored to the respective control after dialog windows close
- Clicking outside the header area in any window must break focus
- Focus state must be properly managed across all windows

##### Real-time Updates
- Color changes must be reflected instantly in both windows
- Font changes must be applied immediately
- Alignment changes must be synchronized between windows
- All property changes must maintain visual consistency

##### Layout Stability
- Status bar and header preview must use consistent padding
- No extra spacing between elements during transitions
- Header preview must be properly removed when hidden
- Layout must be stable during all state transitions


## Background
Both views. Both windows.
SVG for background can be chosen in the profile settings


## Windows:
+ Main window (for sreamer to see. above all windows)
+ Stream window (for OBS to catch. stays under the game window and not seeable by streamer)

### Window defaults:
+ Main window default size: 400x400px
+ Stream window default size: 400x400px
+ All buttons height: 32px
+ All task bars have semi-transparent white background


### Main Window
This window should always stay on top of other windows (even games).

#### Task bar (Main window. Both views)
1. Window Controls (left-top corner)
+ 🌀(Toggle: Chat/Whiteboard view)

2. OBS status bar (top-top position)
+  🎥 • ...or... 🎥 ⏹ (OBS read-only recording status)

3. Viewers count
+ 👀 123 (viewers count)

#### Stream controls bar (Main window. Chat view)
1. Ads
+ 📢 5:12 ⏳ - time till next ad. Make sure view is tabular, so it's 09:59->10:00, not 9:59->10:00 - numbers should not jump.
or 📢  5:12 - remaining time of current ad running
+ ▶ - [RUN] button. run ad right now
+ 🕔... - [DELAY button]. prompts amount of minutes (accepts float)
+ 🕔..5 - [DELAY 5min] button
+ ✖️2 - [x2] toggle. Makes ad runs twice consequentially but cooldown is x2 too.

2. TTS
1. 🗣️ 22 (queue size)
2. ▶ - [PLAY] button. Play a single item from the queue. Or start autoplay if [AUTOPLAY] toggle is active.
3. ⏹ - [STOP] button.
4. 📜 (or 🔁) - [AUTOPLAY] toggle.


### Main Window - Updated position of elements.
This is an update to the descriptions above.

#### Top bar - status bar
+ 🌀(Toggle: Chat/Whiteboard view) - the only actionable element in this bar.
+ 🎥 • (rec) ...or... 🎥 ⏹  (stop) - OBS read-only recording status
+ 👀 123 (Twitch viewers count)
+ 🗣️ 22 (TTS queue size) (👥)
+ 📢  5:12 - (Ads - remaining time of current running ad, or - 📢 5:12 ⏳ - time till next ad)

#### Second bar - controls bar
1. Ads
+ 📢  - title-icon
+ ▶ - [RUN] button. run ad right now
+ ⏳N - [DELAY button]. prompts amount of minutes (accepts float)
+ ⏳5 - [DELAY 5min] button
+ ✖️2 - [x2] toggle. Makes ad runs twice consequentially but cooldown is x2 too.
2. | - vertical separator
3. TTS
+ 🗣️ - title-icon
+ ▶ - [PLAY] button. Play a single item from the queue. Or start autoplay if [AUTOPLAY] toggle is active.
+ ⏹ - [STOP] button.
+ 📜 - [AUTOPLAY] toggle.
4. Stream controls (OBS. Do not add this functionality now! It's for later)
+ [START STREAMING]
+ [STOP STREAMING]


##### Window Manipulation
1. Moving
+ Click and hold anywhere on the task bar (except buttons) to drag the window
+ Release to stop moving

2. Resizing
+ Hover over any corner (40x40px area) to see resize cursor
+ Click and drag corner to resize window
+ Release to stop resizing

### Stream Window
Always displays the Whiteboard view. No task bars at all.
This window doesn't always stays on top of other windows.
Add functionality to sync the window geometry&position with the Main window. They should always occupy the exact same position in x,y coordinates, with the Stream window positioned directly underneath the Main window in the z-axis (stacked on top of each other). This synchronization should work during dragging/resizing of the Main Window.

## Tray menu
+ Show Main window
+ Show Stream window
+ TTS
+ Profiles
+ Current profile
+ Settings
+ Exit

### TTS
Radioselector:
+ bits
+ mentions

### Profiles
Button:
1. Duplicate profile (duplicates current profile with new name that follows profiles naming convention from above)

Radio selector:
1. Default (default profile. settings for default profile are never changed. if the user alters profile configuration while "default" profile is selected - create a new profile with "New profile" name appended by integer counter if needed - "New profile 1")
2. My stored profile (stored)
3. Profile 1
N. ..

#### Profile settings:
Profile title:
1. Profile title text input

Whiteboard Header:
1. Header text input (up to 200 characters. 2 lines)
2. Font picker
   - Font family
   - Font size
3. Color picker
4. Alignment options
   - Left
   - Center
   - Right

Button styling:
1. Button color picker
   + Option to sync with background color
2. Text color picker
3. Font picker (applies to all buttons, labels, and checkboxes in task bars)
   + Font family
   + Font size

Background:
1. Choose file (SVG)
2. Background base color
3. ⤡ Scale image
4. ✥ De-center image
5. Image Transparency slider

Whiteboard font:
+ Font picker
+ Text color picker

Chat font:
+ Font picker
+ Text color picker


## Settings
1. Twitch credentials
+ Channel URL
+ Stream key

## On startup
1. Client connects using credentials from Settings. Autorized connection is needed to collect all events from Twitch API.
Note that Chat works perfectly fine without autorization.
2. Last used profile is activated if exists. Otherwise - default profile. Whiteboard contents, whiteboard font and windows background settings are restored.
3. Main window is active and shows Chat view. Stream window is active and shows Whiteboard view.


## On moving & resizing
### Taskbar "Move" & "Resize" buttons
Click on "Move" and hold to move the window. Release the mouse button to stop moving.
Click on "Resize" button to resize the window. Now click and drag the corners (32x32px) to resize the window.

### Profile settings - background image
Click on "Re-center" button. Now you can drag the Main window using the regular "Move" button and its logic. Click on "Re-center" again to exit this mode.
Use the slider to resize background image.
- Consider backup/restore mechanisms for profiles


# Setting storage

## QSettings
+ last used profile
+ settings - chat font
+ TTS - radioselector state (bits/mentions)

## Credentials
Credentials live in the "/config/creds.env" file
+ Twitch channel URL
+ Twitch auth key

## Chat History
- Stored in CSV format
- Location: `/chat_history/` folder
- File naming: `YYYY-MM-DD_HH-MM-SS.csv` (timestamp of session start)
- One file per streaming session

## Profile settings
Location: `/profiles/` folder
Profile settings: `profile_name.json`
Whiteboard content: `profile_name.txt`
Profile discovery: Scan `/profiles/` for JSON files

### Profile Settings (JSON)
+ Window positions and geometry
+ Color schemes
+ Background image path (relative to modules root path)
+ Font settings
+ Other profile-specific configurations

### Whiteboard Content
Stored in separate TXT file
One file per profile
Real-time synchronized with active profile
