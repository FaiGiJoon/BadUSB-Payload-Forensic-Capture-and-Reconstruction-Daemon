# Forensic Ducky Monitor Architecture

This document describes the architecture of the Python-based background daemon designed to capture and analyze keystroke-injection payloads from BadUSB / Rubber Ducky devices.

## Overview

The system is designed to run in an isolated Windows 11 VM. it hooks into the low-level keyboard events, records timing information, and reconstructs the Duckyscript equivalent of the captured input.

## Components

1.  **Low-Level Event Hook (`ducky_monitor/hook.py`)**:
    *   Uses `pynput` to interface with the Windows API for global keyboard hooking.
    *   Captures key presses and releases.
    *   Records high-resolution timestamps for each event to calculate inter-keystroke delays.

2.  **Timing & State Engine (`ducky_monitor/reconstructor.py`)**:
    *   Processes the raw stream of keyboard events.
    *   **Dynamic Delay Thresholding**: Uses a moving average of recent keystroke intervals to distinguish between intentional `DELAY` commands and system jitter. This prevents false `DELAY` detections during CPU stutter.
    *   **Modifier State Tracking**: Maintains a set of active modifiers (Shift, Ctrl, Alt, GUI) to correctly reconstruct complex combinations like `CTRL ALT DELETE`.
    *   Converts key combinations into Duckyscript commands (e.g., `GUI r`, `ENTER`, `STRING powershell.exe`).

3.  **Real-Time Asynchronous Logger (`ducky_monitor/logger.py`)**:
    *   **Decoupled I/O Pipeline**: Uses a thread-safe `Queue` and a background worker thread to handle file writes.
    *   **Non-Blocking Hook**: Ensures that slow disk I/O operations (fsync) do not block the keyboard hook thread, preventing packet loss during high-speed injection.
    *   Ensures data is persisted even if the system crashes or reboots.

4.  **Main Orchestrator (`main.py`)**:
    *   Initializes the logger and reconstructor.
    *   Starts the keyboard listener.
    *   Handles clean shutdown, ensuring all logs are flushed.

## Data Flow

1.  **HID Injection**: The BadUSB device sends keystrokes to the OS.
2.  **Hook Capture**: The `pynput` listener intercepts the keystrokes at the OS level.
3.  **Event Processing**: Events are passed to the Reconstructor.
4.  **Reconstruction**: The Reconstructor identifies patterns using dynamic thresholds and modifier state tracking.
5.  **Asynchronous Logging**: Reconstructed commands are queued and written to disk by a dedicated worker thread.

## Security & Operational Considerations

*   **Hook Persistence (UAC Bypass)**: Standard keyboard hooks are lost when Windows switches to the Secure Desktop (e.g., during a UAC prompt). To maintain persistence, the daemon **must** run under the `NT AUTHORITY\SYSTEM` context.
*   **Deployment**: Use the provided `setup_service.ps1` script to configure the monitor as a Scheduled Task with highest privileges under the System account.
*   **Isolation**: The daemon should run in a non-persistent or air-gapped VM to prevent malware from escaping.
