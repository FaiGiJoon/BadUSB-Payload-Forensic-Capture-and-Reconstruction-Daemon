import time
from pynput import keyboard

class DuckyReconstructor:
    """
    Parses raw keyboard events into Duckyscript format.
    Tracks modifier states and calculates inter-keystroke delays.
    """
    def __init__(self, callback, delay_threshold_ms=50):
        self.callback = callback
        self.delay_threshold_ms = delay_threshold_ms
        self.last_event_time = None
        self.string_buffer = ""
        
        # Track active modifiers
        self.active_modifiers = {
            'ctrl': False,
            'shift': False,
            'alt': False,
            'gui': False
        }

        # Map pynput keys to Duckyscript command names
        self.key_map = {
            keyboard.Key.enter: 'ENTER',
            keyboard.Key.esc: 'ESCAPE',
            keyboard.Key.tab: 'TAB',
            keyboard.Key.space: 'SPACE',
            keyboard.Key.backspace: 'BACKSPACE',
            keyboard.Key.up: 'UPARROW',
            keyboard.Key.down: 'DOWNARROW',
            keyboard.Key.left: 'LEFTARROW',
            keyboard.Key.right: 'RIGHTARROW',
            keyboard.Key.page_up: 'PAGEUP',
            keyboard.Key.page_down: 'PAGEDOWN',
            keyboard.Key.home: 'HOME',
            keyboard.Key.end: 'END',
            keyboard.Key.insert: 'INSERT',
            keyboard.Key.delete: 'DELETE',
            keyboard.Key.caps_lock: 'CAPSLOCK',
            keyboard.Key.f1: 'F1', keyboard.Key.f2: 'F2', keyboard.Key.f3: 'F3', keyboard.Key.f4: 'F4',
            keyboard.Key.f5: 'F5', keyboard.Key.f6: 'F6', keyboard.Key.f7: 'F7', keyboard.Key.f8: 'F8',
            keyboard.Key.f9: 'F9', keyboard.Key.f10: 'F10', keyboard.Key.f11: 'F11', keyboard.Key.f12: 'F12',
            keyboard.Key.print_screen: 'PRINTSCREEN',
            keyboard.Key.scroll_lock: 'SCROLLLOCK',
            keyboard.Key.pause: 'PAUSE',
            keyboard.Key.menu: 'MENU',
        }

    def _flush_string(self):
        if self.string_buffer:
            self.callback(f"STRING {self.string_buffer}")
            self.string_buffer = ""

    def process_press(self, key, event_time):
        """Processes a key press event."""
        if self.last_event_time:
            delta_ms = int((event_time - self.last_event_time) * 1000)
            if delta_ms > self.delay_threshold_ms:
                self._flush_string()
                self.callback(f"DELAY {delta_ms}")
        
        self.last_event_time = event_time

        # Update modifier states
        is_modifier = False
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.active_modifiers['ctrl'] = True
            is_modifier = True
        elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            self.active_modifiers['shift'] = True
            is_modifier = True
        elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            self.active_modifiers['alt'] = True
            is_modifier = True
        elif key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            self.active_modifiers['gui'] = True
            is_modifier = True

        if is_modifier:
            return

        # Check for combinations (e.g., GUI r, CTRL ALT DEL)
        ctrl = self.active_modifiers['ctrl']
        alt = self.active_modifiers['alt']
        gui = self.active_modifiers['gui']
        shift = self.active_modifiers['shift']

        if ctrl or alt or gui or (shift and not hasattr(key, 'char')):
            self._flush_string()
            parts = []
            if gui: parts.append("GUI")
            if ctrl: parts.append("CTRL")
            if alt: parts.append("ALT")
            if shift: parts.append("SHIFT")
            
            key_str = self._get_key_str(key)
            parts.append(key_str)
            self.callback(" ".join(parts))
        else:
            # Normal key or special key without modifiers
            if hasattr(key, 'char') and key.char:
                # Regular printable character
                self.string_buffer += key.char
            elif key == keyboard.Key.space:
                # Space is usually part of a STRING in Duckyscript
                self.string_buffer += " "
            elif key in self.key_map:
                # Special key like ENTER, TAB, etc.
                self._flush_string()
                self.callback(self.key_map[key])
            else:
                # Fallback for other keys
                self._flush_string()
                self.callback(f"REM Unknown key: {key}")

    def process_release(self, key, event_time):
        """Processes a key release event to track modifier states."""
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.active_modifiers['ctrl'] = False
        elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            self.active_modifiers['shift'] = False
        elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            self.active_modifiers['alt'] = False
        elif key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            self.active_modifiers['gui'] = False

    def finalize(self):
        """Flushes any remaining buffered data."""
        self._flush_string()

    def _get_key_str(self, key):
        """Converts a key object to its string representation for Duckyscript."""
        if hasattr(key, 'char') and key.char:
            return key.char
        if key in self.key_map:
            return self.key_map[key]
        return str(key).replace("Key.", "").upper()
