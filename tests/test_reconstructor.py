import sys
from unittest.mock import MagicMock

# Mock pynput before it's imported in the reconstructor
mock_pynput = MagicMock()
mock_keyboard = MagicMock()
mock_pynput.keyboard = mock_keyboard
sys.modules["pynput"] = mock_pynput
sys.modules["pynput.keyboard"] = mock_keyboard

import pytest
from ducky_monitor.reconstructor import DuckyReconstructor

# Define some constants that the reconstructor uses from keyboard.Key
class MockKey:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Key.{self.name}"

mock_keyboard.Key.enter = MockKey('enter')
mock_keyboard.Key.esc = MockKey('esc')
mock_keyboard.Key.tab = MockKey('tab')
mock_keyboard.Key.space = MockKey('space')
mock_keyboard.Key.backspace = MockKey('backspace')
mock_keyboard.Key.up = MockKey('up')
mock_keyboard.Key.down = MockKey('down')
mock_keyboard.Key.left = MockKey('left')
mock_keyboard.Key.right = MockKey('right')
mock_keyboard.Key.page_up = MockKey('page_up')
mock_keyboard.Key.page_down = MockKey('page_down')
mock_keyboard.Key.home = MockKey('home')
mock_keyboard.Key.end = MockKey('end')
mock_keyboard.Key.insert = MockKey('insert')
mock_keyboard.Key.delete = MockKey('delete')
mock_keyboard.Key.caps_lock = MockKey('caps_lock')
mock_keyboard.Key.f1 = MockKey('f1')
mock_keyboard.Key.cmd = MockKey('cmd')
mock_keyboard.Key.ctrl = MockKey('ctrl')
mock_keyboard.Key.shift = MockKey('shift')
mock_keyboard.Key.alt = MockKey('alt')

class MockKeyCode:
    def __init__(self, char):
        self.char = char
    @staticmethod
    def from_char(char):
        return MockKeyCode(char)

mock_keyboard.KeyCode = MockKeyCode

def test_string_reconstruction():
    captured = []
    def callback(cmd): captured.append(cmd)
    
    recon = DuckyReconstructor(callback)
    
    # Simulate "hello"
    t = 1000.0
    for char in "hello":
        recon.process_press(MockKeyCode.from_char(char), t)
        recon.process_release(MockKeyCode.from_char(char), t + 0.01)
        t += 0.02
    
    recon.finalize()
    assert "STRING hello" in captured

def test_combination_reconstruction():
    captured = []
    def callback(cmd): captured.append(cmd)
    
    recon = DuckyReconstructor(callback)
    
    # Simulate GUI+r
    t = 1000.0
    recon.process_press(mock_keyboard.Key.cmd, t)
    t += 0.01
    recon.process_press(MockKeyCode.from_char('r'), t)
    t += 0.01
    recon.process_release(MockKeyCode.from_char('r'), t)
    recon.process_release(mock_keyboard.Key.cmd, t + 0.01)
    
    recon.finalize()
    assert "GUI r" in captured

def test_shift_combination_reconstruction():
    captured = []
    def callback(cmd): captured.append(cmd)
    
    recon = DuckyReconstructor(callback)
    
    # Simulate SHIFT+ENTER
    t = 1000.0
    recon.process_press(mock_keyboard.Key.shift, t)
    t += 0.01
    recon.process_press(mock_keyboard.Key.enter, t)
    t += 0.01
    recon.process_release(mock_keyboard.Key.enter, t)
    recon.process_release(mock_keyboard.Key.shift, t + 0.01)
    
    recon.finalize()
    assert "SHIFT ENTER" in captured

def test_delay_detection():
    captured = []
    def callback(cmd): captured.append(cmd)
    
    recon = DuckyReconstructor(callback, delay_threshold_ms=50)
    
    t = 1000.0
    # Type 'a'
    recon.process_press(MockKeyCode.from_char('a'), t)
    recon.process_release(MockKeyCode.from_char('a'), t + 0.01)
    
    # Wait 500ms
    t += 0.5
    
    # Type 'b'
    recon.process_press(MockKeyCode.from_char('b'), t)
    recon.process_release(MockKeyCode.from_char('b'), t + 0.01)
    
    recon.finalize()
    assert "STRING a" in captured
    assert any(cmd.startswith("DELAY") for cmd in captured)
    assert "STRING b" in captured

def test_special_keys():
    captured = []
    def callback(cmd): captured.append(cmd)
    
    recon = DuckyReconstructor(callback)
    
    recon.process_press(mock_keyboard.Key.enter, 1000.0)
    recon.process_release(mock_keyboard.Key.enter, 1000.01)
    
    recon.finalize()
    assert "ENTER" in captured
