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
        
        # Dynamic delay threshold tracking
        self.intervals = []
        self.max_intervals = 10

        # Track active modifiers
        self.active_modifiers = set()

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

    def _calculate_dynamic_threshold(self):
        """Calculates a threshold based on recent typing speed variance."""
        if len(self.intervals) < 3:
            return self.delay_threshold_ms

        avg = sum(self.intervals) / len(self.intervals)
        # We use a multiplier of the average or a fixed buffer to account for jitter.
        # BadUSB devices are typically very consistent.
        return max(self.delay_threshold_ms, avg * 2.5)

    def process_press(self, key, event_time):
        """Processes a key press event."""
        if self.last_event_time:
            delta_ms = int((event_time - self.last_event_time) * 1000)

            threshold = self._calculate_dynamic_threshold()

            if delta_ms > threshold:
                self._flush_string()
                self.callback(f"DELAY {delta_ms}")
                # Clear intervals after a long delay to reset the moving average
                self.intervals = []
            else:
                self.intervals.append(delta_ms)
                if len(self.intervals) > self.max_intervals:
                    self.intervals.pop(0)
        
        self.last_event_time = event_time

        # Update modifier states
        is_modifier = False
        if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
            self.active_modifiers.add('ctrl')
            is_modifier = True
        elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            self.active_modifiers.add('shift')
            is_modifier = True
        elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            self.active_modifiers.add('alt')
            is_modifier = True
        elif key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            self.active_modifiers.add('gui')
            is_modifier = True

        if is_modifier:
            return

        # Check for combinations (e.g., GUI r, CTRL ALT DEL)
        ctrl = 'ctrl' in self.active_modifiers
        alt = 'alt' in self.active_modifiers
        gui = 'gui' in self.active_modifiers
        shift = 'shift' in self.active_modifiers

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
            self.active_modifiers.discard('ctrl')
        elif key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
            self.active_modifiers.discard('shift')
        elif key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
            self.active_modifiers.discard('alt')
        elif key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
            self.active_modifiers.discard('gui')

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
