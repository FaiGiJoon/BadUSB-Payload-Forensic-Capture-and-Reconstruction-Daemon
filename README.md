# Forensic Ducky Monitor

A Python-based background daemon for forensic analysis of HID injection (BadUSB / Rubber Ducky) payloads. It captures keystrokes, analyzes timing, and reconstructs the Duckyscript used to generate the traffic.

## Features

- **Global Hooking**: Intercepts all keyboard events system-wide.
- **Timing Analysis**: Detects `[DELAY]` parameters by measuring inter-keystroke intervals.
- **Duckyscript Reconstruction**: Converts raw input (modifiers + keys) back into readable Duckyscript.
- **Forensic Logging**: Real-time flushing to disk ensures data persistence even during system crashes or reboots.
- **Raw Event Logging**: Logs both high-level Duckyscript and low-level key events for deep analysis.

## Requirements

- Python 3.x
- Windows 11 (tested in isolated VM)
- Dependencies: `pynput`

## Installation

1.  **Isolated Environment**: It is highly recommended to run this inside an air-gapped, non-persistent Windows VM.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the monitor with administrative privileges (to ensure global hooking):

```bash
python main.py
```

Captured data will be written to `ducky_capture.log` in the current directory.

### Persistent Service Setup (UAC Persistence)

Standard keyboard hooks are lost when Windows switches to the Secure Desktop (e.g., during a UAC prompt). To maintain persistence across these transitions, the daemon must run under the `NT AUTHORITY\SYSTEM` account.

A PowerShell script is provided to configure the monitor as a Windows Scheduled Task with the highest privileges:

```powershell
.\setup_service.ps1
```

Once configured, the task will start automatically on boot. You can also start it manually:

```powershell
Start-ScheduledTask -TaskName "ForensicDuckyMonitor"
```

### Log Output Example

```
[2023-10-27 10:00:00] [DUCKY] GUI r
[2023-10-27 10:00:00] [DUCKY] DELAY 500
[2023-10-27 10:00:01] [DUCKY] STRING powershell.exe
[2023-10-27 10:00:01] [DUCKY] ENTER
```

## Testing

To run the test suite, use `pytest` from the root directory:

```bash
PYTHONPATH=. pytest
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## Defensive Focus

This tool is designed for **forensic analysis and defense**. It helps security researchers understand the payloads delivered via BadUSB devices by providing a clear, reconstructed script of the injection attack.
