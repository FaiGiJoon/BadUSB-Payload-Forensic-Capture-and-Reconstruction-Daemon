import os
import threading
import time

class ForensicLogger:
    def __init__(self, log_file="ducky_capture.log"):
        self.log_file = log_file
        self.lock = threading.Lock()
        
        # Ensure the file exists and write a header
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write(f"# Ducky Capture started at {time.ctime()}\n")
                f.flush()
                os.fsync(f.fileno())

    def log(self, message):
        """Logs a message and ensures it is flushed to disk immediately."""
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        formatted_message = f"{timestamp} {message}\n"
        
        with self.lock:
            with open(self.log_file, "a") as f:
                f.write(formatted_message)
                f.flush()
                # Ensure it's written to physical disk
                os.fsync(f.fileno())

    def log_raw_event(self, event_type, key, duration=None):
        """Logs raw keyboard events for granular analysis if needed."""
        msg = f"[RAW] {event_type} {key}"
        if duration:
            msg += f" (delay: {duration:.4f}s)"
        self.log(msg)

    def log_ducky_command(self, command):
        """Logs reconstructed Duckyscript commands."""
        self.log(f"[DUCKY] {command}")
