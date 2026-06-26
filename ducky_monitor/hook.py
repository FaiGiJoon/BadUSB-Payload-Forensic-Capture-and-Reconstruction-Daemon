import time
from pynput import keyboard

class KeyboardHook:
    """
    Hooks into the Windows keyboard events and feeds them to the reconstructor and logger.
    """
    def __init__(self, logger, reconstructor):
        self.logger = logger
        self.reconstructor = reconstructor
        self.listener = None

    def on_press(self, key):
        event_time = time.time()
        try:
            # Log raw event for forensic depth
            self.logger.log_raw_event("PRESS", key)
            # Process for reconstruction
            self.reconstructor.process_press(key, event_time)
        except Exception as e:
            self.logger.log(f"[ERROR] on_press: {e}")

    def on_release(self, key):
        event_time = time.time()
        try:
            self.logger.log_raw_event("RELEASE", key)
            self.reconstructor.process_release(key, event_time)
        except Exception as e:
            self.logger.log(f"[ERROR] on_release: {e}")

    def start(self):
        """Starts the keyboard listener in blocking mode."""
        self.logger.log("Keyboard Hook Started.")
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            self.listener = listener
            listener.join()

    def stop(self):
        """Stops the keyboard listener."""
        if self.listener:
            self.listener.stop()
            self.reconstructor.finalize()
            self.logger.log("Keyboard Hook Stopped.")
