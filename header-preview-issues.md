# Header Preview Mode - Requirements and Issues

## Requirements

### Core Functionality
1. Header preview mode should be activated when:
   - Any header control in Profile Settings gains focus
   - Color picker or Font settings window opens
   - Header text is being edited

2. Header preview should be a two-layer system:
   - Background layer: Semi-transparent white background
   - Text layer: Header text with font and color settings

3. Rendering Strategy:
   - Background layer should only re-render when background settings change
   - Text layer should only re-render when text content, font, or color changes
   - Opening Color Picker/Font settings should not trigger any re-rendering

4. Taskbar Management:
   - Taskbar should be completely removed during preview mode
   - Preview container should occupy the exact same space as Taskbar
   - Taskbar should be restored when preview mode is deactivated

## Current Issues

### Flickering
1. Taskbar still appears during preview mode
2. Full re-rendering occurs during color/font changes
3. Background layer is not properly isolated from text updates

### Preview Activation
1. Preview mode is not immediately active when Color Picker/Font settings open
2. First change is required to activate preview mode
3. Preview mode may deactivate unexpectedly during color/font changes

### Font Rendering
1. Font styles (italic, bold) are not properly rendered
2. Font changes may not be immediately visible
3. Font preview may not match Stream window exactly

### Layout
1. Preview container may not perfectly match Taskbar dimensions
2. Text alignment may shift during updates
3. Padding/margins may be inconsistent between preview and Stream window

## Next Steps
1. Implement proper layer isolation
2. Fix preview activation timing
3. Ensure consistent font rendering
4. Perfect layout matching
5. Eliminate all flickering 