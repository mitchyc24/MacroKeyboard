# MacroKeyboard

A customizable macro keyboard built for the Raspberry Pi Pico using CircuitPython. This project allows you to assign complex macro sequences to physical buttons, including keyboard shortcuts, mouse commands with absolute positioning, and text input.

---

## Features

- 9 programmable buttons
- **New: Full keyboard and mouse support with absolute positioning**
- **New: Complex macro sequences with delays and multiple actions**
- **New: PC-based profiles for enhanced customization**
- Supports single keys, key combinations, and complex sequences
- Mouse click and movement commands with absolute coordinates
- Text typing and scrolling commands
- Easy to update and customize profiles on your PC

---

## Architecture

### Version 2.0: PC-Based Macro Service (Current)

The MacroKeyboard now uses a split architecture for enhanced capabilities:

1. **Raspberry Pi Pico (firmware_serial.py)**: Detects button presses and sends events via serial communication
2. **PC Service (pc_service.py)**: Receives button events and executes complex macros including mouse commands

This architecture enables:
- **Absolute mouse positioning** (not possible with HID-only approach)
- **Complex macro sequences** with delays and multiple actions
- **PC-based profile storage** for easier management
- **Enhanced action types**: typing, mouse movement, scrolling, etc.

### Legacy Versions

- **keyboard.py**: Original version with hardcoded key mappings (HID-only)
- **keyboard_v2.py**: Config-based version with profiles stored on device (HID-only)

---

## Quick Start

### 1. Install PC Service Dependencies

```bash
pip install -r requirements.txt
```

### 2. Upload Firmware to Pico

Follow the steps in [Updating the Code](#updating-the-code-on-the-raspberry-pi-pico) section to upload `firmware_serial.py` to your Pico.

### 3. Start the PC Service

```bash
python pc_service.py
```

The service will automatically detect your MacroKeyboard and load the default profile.

### 4. Customize Your Macros

Edit `profiles/pc_profile.json` to customize your button mappings. See [Profile Format](#profile-format) for details.

---

## Profile Format

Profiles are stored as JSON files with enhanced action support:

```json
{
  "7": [
    {"type": "key", "key": "a"}
  ],
  "22": [
    {"type": "mouse_move", "x": 500, "y": 300},
    {"type": "delay", "duration": 0.1},
    {"type": "mouse_click", "button": "left"}
  ]
}
```

### Supported Action Types

- **`key`**: Single key press
  ```json
  {"type": "key", "key": "f1"}
  ```

- **`key_combo`**: Key combination
  ```json
  {"type": "key_combo", "keys": ["ctrl", "z"]}
  ```

- **`type`**: Type text
  ```json
  {"type": "type", "text": "Hello World!"}
  ```

- **`mouse_move`**: Move mouse to absolute position
  ```json
  {"type": "mouse_move", "x": 100, "y": 200}
  ```

- **`mouse_click`**: Click mouse button
  ```json
  {"type": "mouse_click", "button": "left", "x": 100, "y": 200}
  ```

- **`scroll`**: Scroll wheel
  ```json
  {"type": "scroll", "clicks": 3}
  ```

- **`delay`**: Wait/pause
  ```json
  {"type": "delay", "duration": 1.0}
  ```

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

### Current Version (2.0)

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Upload firmware**: Upload `firmware_serial.py` to your Pico as `main.py`
3. **Start PC service**: Run `python pc_service.py`
4. **Press buttons**: Your macros will execute on the PC with full keyboard/mouse support

### Legacy Versions

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



