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
    *   Tracks modifier key states (Shift, Ctrl, Alt, GUI).
    *   Calculates delays between events to detect `[DELAY]` parameters.
    *   Converts key combinations into Duckyscript commands (e.g., `GUI r`, `ENTER`, `STRING powershell.exe`).

3.  **Real-Time Logger (`ducky_monitor/logger.py`)**:
    *   Handles file I/O with immediate flushing.
    *   Ensures data is persisted even if the system crashes or reboots.
    *   Provides a thread-safe interface for logging reconstructed commands.

4.  **Main Orchestrator (`main.py`)**:
    *   Initializes the logger and reconstructor.
    *   Starts the keyboard listener.
    *   Handles clean shutdown.

## Data Flow

1.  **HID Injection**: The BadUSB device sends keystrokes to the OS.
2.  **Hook Capture**: The `pynput` listener intercepts the keystrokes at the OS level.
3.  **Event Processing**: Events are passed to the Reconstructor.
4.  **Reconstruction**: The Reconstructor identifies patterns (e.g., fast typing = `STRING`, specific keys = `COMMAND`).
5.  **Logging**: The reconstructed Duckyscript is sent to the Logger, which writes and flushes it to a local file.

## Security Considerations

*   **Isolation**: The daemon should run in a non-persistent or air-gapped VM to prevent malware from escaping.
*   **Tamper Resistance**: While the daemon is a Python script, it should be started as a system service or a background process to avoid easy detection/termination by basic scripts.
