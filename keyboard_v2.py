import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# --- Config parsing ---
def parse_profile_config(filename="profile.config"):
    keycode_lookup = {k: v for k, v in Keycode.__dict__.items() if not k.startswith("_")}
    gpio_pins = []
    button_key_map = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                pin_part, keycodes_part = line.split(":", 1)
                pin = int(pin_part.strip())
                keycodes = [k.strip().upper() for k in keycodes_part.split(",")]
                keycode_values = []
                for k in keycodes:
                    if k in keycode_lookup:
                        keycode_values.append(keycode_lookup[k])
                    else:
                        print(f"Warning: Unknown keycode '{k}' in config for pin {pin}")
                if keycode_values:
                    gpio_pins.append(pin)
                    button_key_map[pin] = keycode_values
    except Exception as e:
        print(f"Error reading config: {e}")
        raise
    return gpio_pins, button_key_map

gpio_pins, button_key_map = parse_profile_config()

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

# Initialize all pins as inputs with pull-up resistors
buttons = {}
for pin in gpio_pins:
    board_pin = pin_map.get(pin)
    if board_pin is not None:
        btn = digitalio.DigitalInOut(board_pin)
        btn.direction = digitalio.Direction.INPUT
        btn.pull = digitalio.Pull.UP
        buttons[pin] = btn
    else:
        print(f"Warning: Pin {pin} not in pin_map, skipping.")

# Initialize the keyboard
keyboard = Keyboard(usb_hid.devices)

# Store the last state of each button to detect changes
last_states = {pin: True for pin in gpio_pins}  # Default state is True (not pressed)

print("Macro keyboard script started. Loaded profile from config.")

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