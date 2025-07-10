import time
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

# --- MouseController Class for Absolute Positioning ---
class MouseController:
    """
    Manages mouse state, including screen dimensions and current cursor position,
    to enable absolute positioning.
    """
    def __init__(self, mouse_device, screen_width=1920, screen_height=1080):
        """
        Initializes the controller.
        :param mouse_device: The adafruit_hid.mouse.Mouse object.
        :param screen_width: The width of the screen in pixels.
        :param screen_height: The height of the screen in pixels.
        """
        self.mouse = mouse_device
        self.screen_width = screen_width
        self.screen_height = screen_height
        # Assume starting position is unknown until reset.
        # We will set it to (0, 0) after the initial reset.
        self.current_x = 0
        self.current_y = 0

    def reset_position(self):
        """
        Resets the cursor to the top-left corner (0, 0) by moving it
        a very large distance in the negative X and Y directions.
        This provides a known starting point for absolute moves.
        This process can take a second or two.
        """
        print("Resetting mouse position to (0,0)...")
        # Move a large amount to ensure it hits the corner of any reasonably sized screen.
        # The move is done in chunks, as the HID protocol has a max relative move of 127.
        for _ in range(64): # Move ~8000 pixels diagonally
            self.mouse.move(x=-127, y=-127)
            time.sleep(0.005) # Small delay for the OS to keep up
        self.current_x = 0
        self.current_y = 0
        print("Mouse position reset.")

    def move_abs(self, x, y):
        """
        Moves the mouse to an absolute (x, y) coordinate on the screen.
        """
        # Clamp target coordinates to stay within screen bounds
        target_x = max(0, min(self.screen_width - 1, x))
        target_y = max(0, min(self.screen_height - 1, y))

        # Calculate the required relative move
        dx = target_x - self.current_x
        dy = target_y - self.current_y

        self._move_in_chunks(dx, dy)

        # Update the current position
        self.current_x = target_x
        self.current_y = target_y

    def move_rel(self, dx, dy):
        """
        Moves the mouse by a relative (dx, dy) amount.
        """
        # Calculate the theoretical new position
        new_x = self.current_x + dx
        new_y = self.current_y + dy

        # Clamp it to the screen boundaries
        target_x = max(0, min(self.screen_width - 1, new_x))
        target_y = max(0, min(self.screen_height - 1, new_y))

        # The actual move is the difference between the clamped target and current position
        actual_dx = target_x - self.current_x
        actual_dy = target_y - self.current_y

        self._move_in_chunks(actual_dx, actual_dy)

        # Update the current position
        self.current_x = target_x
        self.current_y = target_y

    def _move_in_chunks(self, dx, dy):
        """Helper function to break down large moves into HID-compatible chunks."""
        while dx != 0 or dy != 0:
            move_dx = max(-127, min(127, dx))
            move_dy = max(-127, min(127, dy))
            self.mouse.move(x=move_dx, y=move_dy)
            dx -= move_dx
            dy -= move_dy
            # A small delay is crucial for the OS to process rapid events
            time.sleep(0.005)

    def click(self, button):
        """Performs a standard mouse click (press and release)."""
        self.mouse.press(button)
        time.sleep(0.05)
        self.mouse.release(button)

# --- Config parsing ---
def parse_profile_config(filename="macro.profile"):
    keycode_lookup = {k: v for k, v in Keycode.__dict__.items() if not k.startswith("_")}
    mouse_button_lookup = {
        "L_CLICK": "left_click",
        "R_CLICK": "right_click",
        "M_CLICK": "middle_click",
    }
    gpio_pins = []
    button_action_map = {}
    screen_resolution = (1920, 1080)  # Default resolution

    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # --- New: Parse screen resolution setting ---
                if line.upper().startswith("SCREEN_RESOLUTION"):
                    try:
                        res_part = line.split(":", 1)[1].strip()
                        coords = res_part.split(",")
                        w = int(coords[0].strip())
                        h = int(coords[1].strip())
                        screen_resolution = (w, h)
                    except Exception as e:
                        print(f"Warning: Could not parse SCREEN_RESOLUTION. Using default. Error: {e}")
                    continue  # Done with this line, move to the next

                # --- Existing pin and action parsing ---
                pin_part, actions_part = line.split(":", 1)
                pin = int(pin_part.strip())
                # --- Updated splitting logic ---
                actions = []
                buf = ""
                paren = 0
                for c in actions_part:
                    if c == "(":
                        paren += 1
                    elif c == ")":
                        paren -= 1
                    if c == "," and paren == 0:
                        actions.append(buf.strip())
                        buf = ""
                    else:
                        buf += c
                if buf.strip():
                    actions.append(buf.strip())
                # --- End update ---
                action_list = []
                for a in actions:
                    a_upper = a.upper()
                    if a.isdigit():
                        action_list.append(("delay", int(a)))
                    elif a_upper in keycode_lookup:
                        action_list.append(("key", keycode_lookup[a_upper]))
                    elif a_upper in mouse_button_lookup:
                        action_list.append(("mouse_click", mouse_button_lookup[a_upper]))
                    elif a_upper.startswith("MOUSE_MOVE_ABS"):
                        try:
                            coords = a[a.find("(")+1:a.find(")")].split(",")
                            x = int(coords[0].strip())
                            y = int(coords[1].strip())
                            action_list.append(("mouse_move_abs", (x, y)))
                        except Exception:
                            print(f"Warning: Invalid absolute mouse move '{a}' in config for pin {pin}")
                    elif a_upper.startswith("MOUSE_MOVE_REL"):
                        try:
                            coords = a[a.find("(")+1:a.find(")")].split(",")
                            dx = int(coords[0].strip())
                            dy = int(coords[1].strip())
                            action_list.append(("mouse_move_rel", (dx, dy)))
                        except Exception:
                            print(f"Warning: Invalid relative mouse move '{a}' in config for pin {pin}")
                    else:
                        print(f"Warning: Unknown action '{a}' in config for pin {pin}")
                if action_list:
                    gpio_pins.append(pin)
                    button_action_map[pin] = action_list
    except Exception as e:
        print(f"Error reading config: {e}")
        raise
    return gpio_pins, button_action_map, screen_resolution

# --- Main script setup ---
gpio_pins, button_action_map, screen_res = parse_profile_config()
screen_width, screen_height = screen_res

pin_map = {
    7: board.GP7, 9: board.GP9, 11: board.GP11, 13: board.GP13,
    14: board.GP14, 17: board.GP17, 18: board.GP18, 20: board.GP20,
    22: board.GP22,
}

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

# --- Initialize devices using the new MouseController ---
keyboard = Keyboard(usb_hid.devices)
mouse_hid = Mouse(usb_hid.devices)
mouse = MouseController(mouse_hid, screen_width, screen_height)

last_states = {pin: True for pin in gpio_pins}

print("Macro keyboard script started. Loaded profile from config.")
print(f"Screen resolution set to: {screen_width}x{screen_height}")
mouse.reset_position() # Initialize mouse position to (0,0)

def perform_actions(actions):
    """Executes a sequence of actions using the keyboard and mouse controller."""
    for action_type, value in actions:
        if action_type == "key":
            keyboard.press(value)
        elif action_type == "mouse_click":
            if value == "left_click":
                mouse.click(Mouse.LEFT_BUTTON)
            elif value == "right_click":
                mouse.click(Mouse.RIGHT_BUTTON)
            elif value == "middle_click":
                mouse.click(Mouse.MIDDLE_BUTTON)
        elif action_type == "mouse_move_abs":
            x, y = value
            mouse.move_abs(x, y)
        elif action_type == "mouse_move_rel":
            dx, dy = value
            mouse.move_rel(dx, dy)
        elif action_type == "delay":
            time.sleep(value / 1000.0)
            print(f"Delay for {value} ms")
        else:
            print(f"Unknown action: {(action_type, value)}")

def release_keys(actions):
    """Releases any keys that were pressed in an action sequence."""
    for action_type, value in actions:
        if action_type == "key":
            keyboard.release(value)
    # Mouse clicks are momentary, so nothing to release for mouse actions

# --- Main loop ---
while True:
    for pin, button in buttons.items():
        current_state = button.value
        if not current_state and last_states[pin]:  # Detect falling edge (button press)
            print(f"Button on GP{pin} pressed. Performing actions: {button_action_map[pin]}")
            perform_actions(button_action_map[pin])
        elif current_state and not last_states[pin]:  # Detect rising edge (button release)
            release_keys(button_action_map[pin])
        last_states[pin] = current_state

    time.sleep(0.01)
