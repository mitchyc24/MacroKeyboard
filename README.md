# MacroKeyboard

A customizable macro keyboard built for the Raspberry Pi Pico using CircuitPython. This project allows you to assign keyboard shortcuts or keypresses to physical buttons, making repetitive tasks faster and easier.

---

## Features

- 9 programmable buttons
- Supports single keys and key combinations (e.g., Ctrl+Z)
- Easy to update and customize
- Plug-and-play USB HID device

---

## Pinout

Button layout and GPIO pin mapping:

```
+----+----+----+
| 17 | 20 | 22 |
+----+----+----+
| 18 | 14 | 13 |
+----+----+----+
|  7 |  9 | 11 |
+----+----+----+
        |
       USB
```

| Button Position | GPIO Pin |
|:--------------:|:--------:|
| Top Left       |   17     |
| Top Middle     |   20     |
| Top Right      |   22     |
| Middle Left    |   18     |
| Middle Middle  |   14     |
| Middle Right   |   13     |
| Bottom Left    |    7     |
| Bottom Middle  |    9     |
| Bottom Right   |   11     |

---

## Usage

1. **Plug in the MacroKeyboard to your PC.**
2. The device will be recognized as a standard USB keyboard.
3. Press any of the 9 buttons to send the assigned key or key combination.

---

## Updating the Code on the Raspberry Pi Pico

To upload new code to your MacroKeyboard, follow these steps:

1. **Install Python 3.9** (recommended for compatibility with `rshell`).
2. **Install [`uv`](https://github.com/astral-sh/uv) (a fast Python package/dependency manager):**
   ```bash
   pip install uv
   ```
3. **Create and activate a virtual environment using Python 3.9 and `uv`:**
   ```bash
   uv venv .venv --python=3.9
   ```
   - On Windows, activate with:
     ```cmd
     .venv\Scripts\activate
     ```
   - On Linux/macOS, activate with:
     ```bash
     source .venv/bin/activate
     ```
4. **Install `rshell` inside the virtual environment:**
   ```bash
   pip install rshell
   ```
5. **Connect your Raspberry Pi Pico to your computer via USB.**
6. **Find the Pico's serial port:**
   - On Windows, it will appear as `COMx` (e.g., `COM5`).
   - On Linux/macOS, it will appear as `/dev/ttyACM0` or similar.
7. **Open a command prompt and start `rshell`:**
   ```bash
   rshell -p COM5
   ```
   Replace `COM5` with your Pico's port if different.
8. **At the `rshell>` prompt, upload your code:**
   ```bash
   cp tests/blink.py /pyboard/main.py
   ```
   Replace `tests/blink.py` with the path to your script and `/pyboard/main.py` with the desired destination filename.
9. **Reset the Pico** (unplug and replug, or press the reset button) to run the new code.

For more details, see the [rshell documentation](https://github.com/dhylands/rshell).



