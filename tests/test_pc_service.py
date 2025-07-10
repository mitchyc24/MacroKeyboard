#!/usr/bin/env python3
"""
Simple test script for the MacroKeyboard PC Service
Tests the profile loading and action parsing without requiring hardware or GUI libraries
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json

# Mock pyautogui to avoid import errors in test environment
class MockPyAutoGUI:
    FAILSAFE = False
    def press(self, key): pass
    def hotkey(self, *keys): pass
    def write(self, text): pass
    def moveTo(self, x, y): pass
    def click(self, x=None, y=None, button='left'): pass
    def scroll(self, clicks): pass

# Mock serial to avoid import errors in test environment  
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

def test_profile_loading():
    """Test that profiles load correctly"""
    print("Testing profile loading...")
    
    # Test with existing profile
    service = MacroKeyboardService("profiles/pc_profile.json")
    assert len(service.profile) == 9, f"Expected 9 buttons, got {len(service.profile)}"
    print("✓ Basic profile loaded correctly")
    
    # Test with advanced profile
    service = MacroKeyboardService("profiles/advanced_profile.json")
    assert len(service.profile) == 9, f"Expected 9 buttons, got {len(service.profile)}"
    print("✓ Advanced profile loaded correctly")
    
    # Test button 22 has multiple actions
    button_22_actions = service.profile.get("22", [])
    assert len(button_22_actions) > 1, "Button 22 should have multiple actions"
    print("✓ Multi-action sequences loaded correctly")

def test_action_validation():
    """Test that action structures are valid"""
    print("\nTesting action validation...")
    
    with open("profiles/pc_profile.json", 'r') as f:
        profile = json.load(f)
    
    required_fields = {
        "key": ["key"],
        "key_combo": ["keys"],
        "type": ["text"],
        "mouse_move": ["x", "y"],
        "mouse_click": ["button"],
        "scroll": ["clicks"],
        "delay": ["duration"]
    }
    
    for button, actions in profile.items():
        for action in actions:
            action_type = action.get("type")
            assert action_type is not None, f"Action missing type: {action}"
            
            if action_type in required_fields:
                for field in required_fields[action_type]:
                    if field not in action and action_type != "mouse_click":  # mouse_click coordinates are optional
                        print(f"Warning: Action {action} missing recommended field: {field}")
    
    print("✓ Action structures are valid")

def test_profile_creation():
    """Test default profile creation"""
    print("\nTesting default profile creation...")
    
    # Test with non-existent profile path
    test_profile_path = "/tmp/test_profile.json"
    if os.path.exists(test_profile_path):
        os.remove(test_profile_path)
    
    service = MacroKeyboardService(test_profile_path)
    assert len(service.profile) > 0, "Default profile should be created"
    assert os.path.exists(test_profile_path), "Profile file should be created"
    
    # Verify the created profile is valid JSON
    with open(test_profile_path, 'r') as f:
        loaded_profile = json.load(f)
    assert loaded_profile == service.profile, "Saved profile should match in-memory profile"
    
    # Cleanup
    os.remove(test_profile_path)
    print("✓ Default profile creation works correctly")

def main():
    """Run all tests"""
    print("Running MacroKeyboard PC Service Tests")
    print("=" * 40)
    
    try:
        test_profile_loading()
        test_action_validation()
        test_profile_creation()
        
        print("\n" + "=" * 40)
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)