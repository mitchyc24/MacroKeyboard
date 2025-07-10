#!/usr/bin/env python3
"""
MacroKeyboard Demo Script
Simulates button presses to demonstrate the macro execution without requiring hardware
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock pyautogui for demo purposes
class MockPyAutoGUI:
    FAILSAFE = False
    
    def press(self, key):
        print(f"    → GUI: Pressed key '{key}'")
    
    def hotkey(self, *keys):
        print(f"    → GUI: Pressed key combination '{'+'.join(keys)}'")
    
    def write(self, text):
        print(f"    → GUI: Typed text '{text}'")
    
    def moveTo(self, x, y):
        print(f"    → GUI: Moved mouse to ({x}, {y})")
    
    def click(self, x=None, y=None, button='left'):
        if x is not None and y is not None:
            print(f"    → GUI: Clicked {button} mouse button at ({x}, {y})")
        else:
            print(f"    → GUI: Clicked {button} mouse button at current position")
    
    def scroll(self, clicks):
        direction = "up" if clicks > 0 else "down"
        print(f"    → GUI: Scrolled {direction} {abs(clicks)} click(s)")

# Mock serial
class MockSerial:
    class Serial:
        def __init__(self, *args, **kwargs): pass
        def readline(self): return b""
        def close(self): pass
    class tools:
        class list_ports:
            @staticmethod
            def comports(): return []

sys.modules['pyautogui'] = MockPyAutoGUI()
sys.modules['serial'] = MockSerial()
sys.modules['serial.tools'] = MockSerial.tools
sys.modules['serial.tools.list_ports'] = MockSerial.tools.list_ports

from pc_service import MacroKeyboardService

def demo_button_press(service, button_pin, description):
    """Simulate a button press and show the resulting actions"""
    print(f"\n🔘 {description} (Button {button_pin}):")
    print("-" * 50)
    service.execute_macro(str(button_pin))

def main():
    """Run the demo"""
    print("MacroKeyboard Demo - Simulated Button Presses")
    print("=" * 60)
    print("This demo shows what would happen when you press each button")
    print("on the MacroKeyboard with the default profile.")
    print()
    
    # Load the service with the basic profile
    service = MacroKeyboardService("profiles/pc_profile.json")
    
    # Demo basic actions
    demo_button_press(service, 7, "Simple key press (A)")
    demo_button_press(service, 13, "Key combination (Ctrl+Z)")
    demo_button_press(service, 22, "Complex sequence (Mouse movement + click)")
    
    print("\n" + "=" * 60)
    print("Now demonstrating advanced profile:")
    
    # Load the advanced profile
    service = MacroKeyboardService("profiles/advanced_profile.json")
    
    demo_button_press(service, 7, "Type text")
    demo_button_press(service, 9, "Copy and paste sequence")
    demo_button_press(service, 17, "Mouse click with text input")
    demo_button_press(service, 20, "Mouse scroll")
    demo_button_press(service, 22, "Alt+Tab application switch")
    
    print("\n" + "=" * 60)
    print("✨ Demo complete!")
    print()
    print("Key improvements over HID-only approach:")
    print("  • Absolute mouse positioning (coordinates 100,100, 200,200, etc.)")
    print("  • Complex sequences with delays")
    print("  • Text typing capabilities")
    print("  • Mouse scrolling")
    print("  • Easy profile editing on PC")

if __name__ == "__main__":
    main()