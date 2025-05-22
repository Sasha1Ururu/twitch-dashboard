# First phase
Implement new UI and persistent settings features

## [✓] Sync Main&Stream window positions
Windows are now perfectly synchronized in both position and size, with Stream window positioned directly underneath Main window in z-axis. Synchronization works during dragging and resizing.

## [✓] fix the "Show Main/Stream window" tray menu toggle
Tray menu toggles now properly show/hide windows and maintain synchronization between them. Checkboxes accurately reflect window visibility states.

## [  ] Implement profiles & persistent settings
Implement persistent storage for all application settings and states

## [✓] Whiteboard view and real-time save
Implement real-time synchronized whiteboard between Main and Stream windows.

## [✓] Add header to Stream Window
It should occupy the same space as "Status bar" and display the Whiteboard header text.

Following can be set in profile settings:
+ Whiteboard header (2-lines input area ~200 chars). Text updates should be rendered instantly in the stream window. Also if this input area is active - display the header in the Main window on top of existing status bar.
+ Font
+ Font color
+ align (toggle): left, center, right

Background color for header is the same as for the task bar.

## [  ] Whiteboard view - Text selection
I want to be able to select text with mouse
Also text selection should be rendered in the Whiteboard view.

## [  ] Add "Task bar" settings to Profile settings
right after the Whiteboard Header block

+ Taskbar color (color picker)
+ same as Background color (checkbox) - current behaviour
+ Background opacity (slider)


## [  ] Change Status bar elements order
+ Whiteboard toggle
+ Ads status
+ OBS status
+ TTS queue count
+ Viewers count

# Fixes:
## [✓]  Update taskbar icons according to spec
Spec has been updated. Use updated formats, unicode icons, wedget position in the taskbar.

## [✓] Remove all TTS related options from settings
Create a tray menu "TTS" with submenu options (radioselector):
+ bits
+ mentions

## [  ] Header fixes
1. got extra padding in the header preview - the text is rendered differently compared to the whiteboard view header
2. When switching between status bar mode - header preview mode: all elements jump to fill their place during appearence. I want that jump gone.
3. pick header color / pick header font - loses focus, but it should not. focus should be active when those windows are open and after they are closed. Until user clicks somewhere else to lose the focus.

## [  ] Real-time font changes
I should see fonts change before I close the color picker.
Just like color changes during Color picker usage, not after "Ok".

## [~] Fix move/resize buttons
Except: Cursor doesnt change to arrow in the corners (no visual feedback)

## [  ] Stream window can't move offscreen
So it can't maintain true postion sync with the Main Window when move offscreen.

## [  ] Status bar can be more compact
I can see spacing between the elements, but I can't shrink the window any further. What gives?

## [  ] Control bar - "x2" and "autoplay" buttons
It seems like a top-bottom padding? messes with the button text. I can see only 35% in the center of the icon.

## [  ] Resizing issue
If I try to resize the Main window but taskbar wont let me shrink the Window any further - Window starts to move in the direction of my resizing.
The Main window should stay in place if try to resize it farther then possible minimum.

## [  ] "Change whiteboard font" opens window not in the center of the screen
but under the stream window?

## [  ] "Select background image" in profile settings doesn't work
File selection window doesn't open.

# Second phase
Integrate dashboard with external services

## [  ] Chat integration
A simple QWebEngine widget that displays a chat web-page with some elements edited out via css/js magic

## [  ] Twitch integration
### [  ] get views count
### [  ] Ads management
### [  ] Subscribe to EventSub and log all incoming events (bits, subscriptions, ...)

## [  ] TTS local HTTP server integration
### [  ] Implement the server itself separately



