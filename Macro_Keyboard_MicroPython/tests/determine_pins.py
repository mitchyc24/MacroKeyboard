import machine
import time

# GPIO pins based on your layout
gpio_pins = [7, 9, 11, 13, 14, 17, 18, 20, 22]

# Initialize all pins as inputs with pull-up resistors
buttons = {pin: machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP) for pin in gpio_pins}

# Store the last state of each button to detect changes
last_states = {pin: 1 for pin in gpio_pins}  # Default state is 1 (not pressed)

print("Button detection script started. Press any button to see its pin number.")

while True:
    for pin, button in buttons.items():
        current_state = button.value()
        if current_state == 0 and last_states[pin] == 1:  # Detect falling edge (button press)
            print(f"You've pressed GP{pin}")
        last_states[pin] = current_state  # Update the last state

    time.sleep(0.01)  # Small delay to prevent overwhelming the processor