import os
import threading
import time
from queue import Queue

class ForensicLogger:
    def __init__(self, log_file="ducky_capture.log"):
        self.log_file = log_file
        self.queue = Queue()
        self.running = True
        
        # Ensure the file exists and write a header
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write(f"# Ducky Capture started at {time.ctime()}\n")
                f.flush()
                os.fsync(f.fileno())
        
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def _worker(self):
        """Continuously pops items from the queue and flushes them to disk."""
        while self.running or not self.queue.empty():
            try:
                # Use a short timeout to allow checking self.running
                message = self.queue.get(timeout=0.5)
                self._write_to_disk(message)
                self.queue.task_done()
            except:
                # Timeout reached or other error
                continue

    def _write_to_disk(self, message):
        """Writes and flushes a message to the physical disk."""
        try:
            with open(self.log_file, "a") as f:
                f.write(message)
                f.flush()
                # Ensure it's written to physical disk
                os.fsync(f.fileno())
        except Exception as e:
            # We can't really log to the same file if writing fails
            print(f"Failed to write to log file: {e}")

    def log(self, message):
        """Logs a message by adding it to the asynchronous queue."""
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        formatted_message = f"{timestamp} {message}\n"
        self.queue.put(formatted_message)

    def log_raw_event(self, event_type, key, duration=None):
        """Logs raw keyboard events for granular analysis if needed."""
        msg = f"[RAW] {event_type} {key}"
        if duration:
            msg += f" (delay: {duration:.4f}s)"
        self.log(msg)

    def log_ducky_command(self, command):
        """Logs reconstructed Duckyscript commands."""
        self.log(f"[DUCKY] {command}")

    def stop(self):
        """Stops the logging worker thread and ensures all messages are flushed."""
        self.running = False
        # The worker will finish the remaining items in the queue
        self.worker_thread.join(timeout=5)
