"""
MacroKeyboard Firmware - Serial Communication Version
This firmware sends button press events via serial to a PC service
that handles macro execution with full keyboard and mouse support.
"""

import time
import board
import digitalio
import usb_cdc

# Map GPIO numbers to board pin names
pin_map = {
    7: board.GP7,
    9: board.GP9,
    11: board.GP11,
    13: board.GP13,
    14: board.GP14,
    17: board.GP17,
    18: board.GP18,
    20: board.GP20,
    22: board.GP22,
}

gpio_pins = list(pin_map.keys())

# Initialize all pins as inputs with pull-up resistors
buttons = {}
for pin, board_pin in pin_map.items():
    btn = digitalio.DigitalInOut(board_pin)
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP
    buttons[pin] = btn

# Initialize serial communication
serial = usb_cdc.console

# Store the last state of each button to detect changes
last_states = {pin: True for pin in gpio_pins}  # Default state is True (not pressed)

print("MacroKeyboard Serial Firmware started.")
print("Waiting for button presses to send to PC service...")

while True:
    for pin, button in buttons.items():
        current_state = button.value
        if not current_state and last_states[pin]:  # Detect falling edge (button press)
            # Send button press event via serial
            message = f"BUTTON_PRESSED:{pin}\n"
            serial.write(message.encode())
            print(f"Sent: {message.strip()}")
        elif current_state and not last_states[pin]:  # Detect rising edge (button release)
            # Send button release event via serial  
            message = f"BUTTON_RELEASED:{pin}\n"
            serial.write(message.encode())
            print(f"Sent: {message.strip()}")
        last_states[pin] = current_state  # Update the last state

    time.sleep(0.01)  # Small delay to prevent overwhelming the processor