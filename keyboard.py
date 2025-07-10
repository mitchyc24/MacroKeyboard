import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

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

# Map each button to a specific key or key combination
button_key_map = {
    7: [Keycode.A],          # Button on GP7 sends "A"
    9: [Keycode.B],          # Button on GP9 sends "B"
    11: [Keycode.C],         # Button on GP11 sends "C"
    13: [Keycode.CONTROL, Keycode.Z],  # Button on GP13 sends "Ctrl+Z"
    14: [Keycode.CONTROL, Keycode.Y],  # Button on GP14 sends "Ctrl+Y"
    17: [Keycode.F1],        # Button on GP17 sends "F1"
    18: [Keycode.F2],        # Button on GP18 sends "F2"
    20: [Keycode.F3],        # Button on GP20 sends "F3"
    22: [Keycode.F4],        # Button on GP22 sends "F4"
}

# Initialize the keyboard
keyboard = Keyboard(usb_hid.devices)

# Store the last state of each button to detect changes
last_states = {pin: True for pin in gpio_pins}  # Default state is True (not pressed)

print("Macro keyboard script started. Press buttons to send keypresses.")

while True:
    for pin, button in buttons.items():
        current_state = button.value
        if not current_state and last_states[pin]:  # Detect falling edge (button press)
            print(f"Button on GP{pin} pressed. Sending key(s): {button_key_map[pin]}")
            keyboard.press(*button_key_map[pin])  # Send the key(s)
        elif current_state and not last_states[pin]:  # Detect rising edge (button release)
            keyboard.release(*button_key_map[pin])  # Release the key(s)
        last_states[pin] = current_state  # Update the last state

    time.sleep(0.01)  # Small delay to prevent overwhelming the processor