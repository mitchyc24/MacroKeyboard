#!/usr/bin/env python3
"""
Serial Communication Simulator
Simulates the communication between the MacroKeyboard and PC Service
"""

import time
import threading
import queue
import sys
import os

# Mock modules for demo
class MockPyAutoGUI:
    FAILSAFE = False
    def press(self, key): print(f"      ⌨️  Pressed: {key}")
    def hotkey(self, *keys): print(f"      ⌨️  Combo: {'+'.join(keys)}")
    def write(self, text): print(f"      📝 Typed: '{text}'")
    def moveTo(self, x, y): print(f"      🖱️  Mouse to: ({x}, {y})")
    def click(self, x=None, y=None, button='left'): 
        if x and y: print(f"      🖱️  Click {button} at: ({x}, {y})")
        else: print(f"      🖱️  Click {button}")
    def scroll(self, clicks): print(f"      🖱️  Scroll: {clicks} clicks")

class MockSerial:
    def __init__(self, queue_ref):
        self.queue = queue_ref
        self.closed = False
        
    def readline(self):
        if self.closed:
            return b""
        try:
            message = self.queue.get(timeout=0.1)
            return (message + '\n').encode()
        except queue.Empty:
            return b""
    
    def close(self):
        self.closed = True

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules['pyautogui'] = MockPyAutoGUI()

from pc_service import MacroKeyboardService

def simulate_firmware(message_queue, buttons_to_press):
    """Simulate the firmware sending button press events"""
    print("🔧 Firmware: Starting simulation...")
    
    for button_pin in buttons_to_press:
        time.sleep(1)  # Simulate time between button presses
        
        # Simulate button press
        message_queue.put(f"BUTTON_PRESSED:{button_pin}")
        print(f"📡 Firmware → PC: BUTTON_PRESSED:{button_pin}")
        
        time.sleep(0.1)  # Brief delay
        
        # Simulate button release
        message_queue.put(f"BUTTON_RELEASED:{button_pin}")
        print(f"📡 Firmware → PC: BUTTON_RELEASED:{button_pin}")
    
    print("🔧 Firmware: Simulation complete")

def simulate_pc_service(message_queue):
    """Simulate the PC service receiving and processing events"""
    print("💻 PC Service: Starting...")
    
    # Create service instance
    service = MacroKeyboardService("profiles/pc_profile.json")
    
    # Mock serial connection
    mock_serial = MockSerial(message_queue)
    service.serial_conn = mock_serial
    service.running = True
    
    # Listen for events (with timeout to avoid infinite loop)
    start_time = time.time()
    while service.running and (time.time() - start_time) < 10:  # 10 second timeout
        try:
            line = service.serial_conn.readline().decode().strip()
            if line:
                if line.startswith("BUTTON_PRESSED:"):
                    button_pin = line.split(":", 1)[1]
                    print(f"💻 PC Service: Received button press: {button_pin}")
                    print(f"💻 PC Service: Executing macro...")
                    service.execute_macro(button_pin)
                    print()
                elif line.startswith("BUTTON_RELEASED:"):
                    button_pin = line.split(":", 1)[1]
                    print(f"💻 PC Service: Received button release: {button_pin}")
        except:
            break
    
    service.stop()
    print("💻 PC Service: Stopped")

def main():
    """Run the communication simulation"""
    print("MacroKeyboard Serial Communication Simulation")
    print("=" * 60)
    print("This demo shows the communication flow between:")
    print("  🔧 Raspberry Pi Pico (Firmware)")  
    print("  💻 PC Service (Python)")
    print()
    
    # Create message queue for communication
    message_queue = queue.Queue()
    
    # Buttons to simulate pressing
    buttons_to_simulate = [7, 13, 22]  # A, Ctrl+Z, Mouse sequence
    
    # Start firmware simulation in background
    firmware_thread = threading.Thread(
        target=simulate_firmware, 
        args=(message_queue, buttons_to_simulate),
        daemon=True
    )
    firmware_thread.start()
    
    # Run PC service simulation
    simulate_pc_service(message_queue)
    
    # Wait for firmware thread to complete
    firmware_thread.join()
    
    print("\n" + "=" * 60)
    print("✨ Communication simulation complete!")
    print()
    print("In the real system:")
    print("  • Firmware runs on Raspberry Pi Pico")
    print("  • PC Service runs on your computer")
    print("  • Communication happens via USB serial")
    print("  • Macros execute with real keyboard/mouse control")

if __name__ == "__main__":
    main()