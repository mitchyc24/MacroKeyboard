"""
MacroKeyboard PC Service
Communicates with the macro keyboard via serial and executes macros
including keyboard and mouse commands with absolute positioning.
"""

import json
import time
import threading
import sys
from pathlib import Path
from typing import Dict, List, Union, Any

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Error: pyserial not installed. Run: pip install pyserial")
    sys.exit(1)

try:
    import pyautogui
except ImportError:
    print("Error: pyautogui not installed. Run: pip install pyautogui")
    sys.exit(1)

# Disable pyautogui failsafe for programmatic use
pyautogui.FAILSAFE = False


class MacroKeyboardService:
    def __init__(self, profile_path: str = "profiles/pc_profile.json"):
        self.profile_path = profile_path
        self.profile = {}
        self.serial_conn = None
        self.running = False
        self.load_profile()
        
    def load_profile(self):
        """Load the macro profile from JSON file"""
        try:
            with open(self.profile_path, 'r') as f:
                self.profile = json.load(f)
            print(f"Loaded profile from {self.profile_path}")
        except FileNotFoundError:
            print(f"Profile file {self.profile_path} not found. Creating default profile...")
            self.create_default_profile()
        except json.JSONDecodeError as e:
            print(f"Error parsing profile JSON: {e}")
            self.create_default_profile()
    
    def create_default_profile(self):
        """Create a default profile with example macros"""
        self.profile = {
            "7": [{"type": "key", "key": "a"}],
            "9": [{"type": "key", "key": "b"}],
            "11": [{"type": "key", "key": "c"}],
            "13": [{"type": "key_combo", "keys": ["ctrl", "z"]}],
            "14": [{"type": "key_combo", "keys": ["ctrl", "y"]}],
            "17": [{"type": "key", "key": "f1"}],
            "18": [{"type": "key", "key": "f2"}],
            "20": [{"type": "key", "key": "f3"}],
            "22": [
                {"type": "mouse_move", "x": 100, "y": 100},
                {"type": "mouse_click", "button": "left"}
            ]
        }
        self.save_profile()
    
    def save_profile(self):
        """Save the current profile to file"""
        # Ensure profiles directory exists
        Path(self.profile_path).parent.mkdir(exist_ok=True)
        with open(self.profile_path, 'w') as f:
            json.dump(self.profile, f, indent=2)
        print(f"Saved profile to {self.profile_path}")
    
    def find_keyboard_port(self):
        """Automatically find the macro keyboard serial port"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Look for Raspberry Pi Pico or CircuitPython device
            if any(keyword in port.description.lower() for keyword in 
                   ['pico', 'circuitpython', 'board in fs mode']):
                return port.device
        return None
    
    def connect_serial(self, port: str = None):
        """Connect to the macro keyboard via serial"""
        if port is None:
            port = self.find_keyboard_port()
            if port is None:
                print("Could not automatically find macro keyboard port")
                print("Available ports:")
                for p in serial.tools.list_ports.comports():
                    print(f"  {p.device}: {p.description}")
                return False
        
        try:
            self.serial_conn = serial.Serial(port, 115200, timeout=1)
            print(f"Connected to macro keyboard on {port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to {port}: {e}")
            return False
    
    def execute_macro(self, button_pin: str):
        """Execute the macro sequence for a given button"""
        if button_pin not in self.profile:
            print(f"No macro defined for button {button_pin}")
            return
        
        macro_sequence = self.profile[button_pin]
        print(f"Executing macro for button {button_pin}: {len(macro_sequence)} action(s)")
        
        for action in macro_sequence:
            try:
                self.execute_action(action)
            except Exception as e:
                print(f"Error executing action {action}: {e}")
    
    def execute_action(self, action: Dict[str, Any]):
        """Execute a single macro action"""
        action_type = action.get("type")
        
        if action_type == "key":
            key = action.get("key")
            pyautogui.press(key)
            print(f"  Pressed key: {key}")
        
        elif action_type == "key_combo":
            keys = action.get("keys", [])
            pyautogui.hotkey(*keys)
            print(f"  Pressed key combo: {'+'.join(keys)}")
        
        elif action_type == "type":
            text = action.get("text", "")
            pyautogui.write(text)
            print(f"  Typed text: {text}")
        
        elif action_type == "mouse_move":
            x, y = action.get("x", 0), action.get("y", 0)
            pyautogui.moveTo(x, y)
            print(f"  Moved mouse to: ({x}, {y})")
        
        elif action_type == "mouse_click":
            button = action.get("button", "left")
            x, y = action.get("x"), action.get("y")
            if x is not None and y is not None:
                pyautogui.click(x, y, button=button)
                print(f"  Clicked {button} at: ({x}, {y})")
            else:
                pyautogui.click(button=button)
                print(f"  Clicked {button} at current position")
        
        elif action_type == "scroll":
            clicks = action.get("clicks", 1)
            pyautogui.scroll(clicks)
            print(f"  Scrolled: {clicks} clicks")
        
        elif action_type == "delay":
            duration = action.get("duration", 1.0)
            time.sleep(duration)
            print(f"  Delayed: {duration}s")
        
        else:
            print(f"  Unknown action type: {action_type}")
        
        # Small delay between actions
        time.sleep(0.05)
    
    def listen_for_events(self):
        """Listen for button events from the macro keyboard"""
        while self.running and self.serial_conn:
            try:
                line = self.serial_conn.readline().decode().strip()
                if line:
                    if line.startswith("BUTTON_PRESSED:"):
                        button_pin = line.split(":", 1)[1]
                        print(f"Received button press: {button_pin}")
                        # Execute macro in a separate thread to avoid blocking
                        threading.Thread(
                            target=self.execute_macro, 
                            args=(button_pin,), 
                            daemon=True
                        ).start()
                    elif line.startswith("BUTTON_RELEASED:"):
                        button_pin = line.split(":", 1)[1]
                        print(f"Received button release: {button_pin}")
                        # Could implement hold/release actions here
            except Exception as e:
                print(f"Error reading from serial: {e}")
                break
    
    def start(self, port: str = None):
        """Start the macro keyboard service"""
        if not self.connect_serial(port):
            return False
        
        self.running = True
        print("MacroKeyboard service started. Press Ctrl+C to stop.")
        
        try:
            self.listen_for_events()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the macro keyboard service"""
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None
        print("MacroKeyboard service stopped.")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MacroKeyboard PC Service")
    parser.add_argument("--port", "-p", help="Serial port (auto-detect if not specified)")
    parser.add_argument("--profile", help="Profile file path", 
                       default="profiles/pc_profile.json")
    
    args = parser.parse_args()
    
    service = MacroKeyboardService(args.profile)
    service.start(args.port)


if __name__ == "__main__":
    main()