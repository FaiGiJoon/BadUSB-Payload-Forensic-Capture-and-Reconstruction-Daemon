import sys
import signal
from ducky_monitor.logger import ForensicLogger
from ducky_monitor.reconstructor import DuckyReconstructor
from ducky_monitor.hook import KeyboardHook

def main():
    print("Initializing Forensic Ducky Monitor...")
    
    # Initialize components
    logger = ForensicLogger("ducky_capture.log")
    
    reconstructor = DuckyReconstructor(
        callback=logger.log_ducky_command,
        delay_threshold_ms=50
    )
    
    hook = KeyboardHook(logger, reconstructor)

    # Handle termination signals
    def signal_handler(sig, frame):
        print("\nShutting down...")
        hook.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Forensic Monitor is active. Capture is being logged to 'ducky_capture.log'.")
    print("Press Ctrl+C to stop.")

    try:
        hook.start()
    except Exception as e:
        logger.log(f"[FATAL] {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
