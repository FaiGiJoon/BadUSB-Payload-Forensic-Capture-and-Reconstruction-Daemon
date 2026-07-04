import os
import time
import pytest
from ducky_monitor.logger import ForensicLogger

def test_logger_creation(tmp_path):
    log_file = tmp_path / "test.log"
    logger = ForensicLogger(str(log_file))
    logger.stop()

    assert log_file.exists()
    with open(log_file, "r") as f:
        content = f.read()
        assert "Ducky Capture Session Started:" in content

def test_asynchronous_logging(tmp_path):
    log_file = tmp_path / "test_async.log"
    logger = ForensicLogger(str(log_file))

    logger.log("Message 1")
    logger.log("Message 2")

    # We might need a small delay or just call stop() which should flush
    logger.stop()

    with open(log_file, "r") as f:
        content = f.read()
        assert "Message 1" in content
        assert "Message 2" in content

def test_raw_event_logging(tmp_path):
    log_file = tmp_path / "test_raw.log"
    logger = ForensicLogger(str(log_file))

    logger.log_raw_event("PRESS", "a", duration=0.05)
    logger.stop()

    with open(log_file, "r") as f:
        content = f.read()
        assert "[RAW] PRESS a (delay: 0.0500s)" in content

def test_ducky_command_logging(tmp_path):
    log_file = tmp_path / "test_ducky.log"
    logger = ForensicLogger(str(log_file))

    logger.log_ducky_command("STRING hello")
    logger.stop()

    with open(log_file, "r") as f:
        content = f.read()
        assert "[DUCKY] STRING hello" in content

def test_logger_directory_creation(tmp_path):
    log_dir = tmp_path / "subdir"
    log_file = log_dir / "test.log"

    # Ensure subdir doesn't exist yet
    assert not log_dir.exists()

    logger = ForensicLogger(str(log_file))
    logger.stop()

    assert log_dir.exists()
    assert log_file.exists()
