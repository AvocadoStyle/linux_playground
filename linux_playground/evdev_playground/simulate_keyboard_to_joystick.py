import asyncio
from evdev import InputDevice, categorize, ecodes, UInput, AbsInfo, KeyEvent

# Define the real keyboard device path (replace this with your actual device)
KEYBOARD_DEVICE_PATH = '/dev/input/event2'  # Use `evtest` or `ls /dev/input/by-id/` to find it

# Axis bounds for virtual joystick
AXIS_MIN = -255
AXIS_MAX = 255
AXIS_CENTER = 0

# Define mappings: key -> (ABS_X, ABS_Y)
KEY_TO_AXIS = {
    'g': (-255, 0),   # Left
    'j': (255, 0),    # Right
    'y': (0, -255),   # Up
    'n': (0, 255),    # Down
    't': (-255, -255),  # Left-Up
    'u': (255, -255),   # Right-Up
    'b': (-255, 255),   # Left-Down
    'm': (255, 255),    # Right-Down
}

# Track pressed keys
direction_state = {}

# Create virtual joystick device
def create_virtual_joystick():
    capabilities = {
        ecodes.EV_ABS: [
            (ecodes.ABS_X, AbsInfo(0, AXIS_MIN, AXIS_MAX, 0, 0, 0)),
            (ecodes.ABS_Y, AbsInfo(0, AXIS_MIN, AXIS_MAX, 0, 0, 0)),
        ]
    }
    return UInput(capabilities, name='VirtualJoystick', bustype=0x03)

# Calculate the current axis state based on all held keys
def calculate_axis():
    x = y = 0
    for (dx, dy) in direction_state.values():
        x += dx
        y += dy
    # Clamp values
    x = max(AXIS_MIN, min(AXIS_MAX, x))
    y = max(AXIS_MIN, min(AXIS_MAX, y))
    return x, y

# Main async loop to forward keys to virtual joystick
async def keyboard_to_joystick():
    dev = InputDevice(KEYBOARD_DEVICE_PATH)
    ui = create_virtual_joystick()

    async for event in dev.async_read_loop():
        if event.type == ecodes.EV_KEY:
            key = categorize(event)
            key_name = ecodes.KEY[key.scancode]
            print(f"Key event: {key_name} - {key.keystate}")
            pure_key_name = key_name.lower().split('_')[1].strip()
            print("pure_key_name:", pure_key_name)
            if pure_key_name in KEY_TO_AXIS:
                print("True key pressed:", key_name)
                # Update direction state based on key event
                if key.keystate == KeyEvent.key_down:
                    direction_state[key_name] = KEY_TO_AXIS[pure_key_name]
                elif key.keystate == KeyEvent.key_up:
                    direction_state.pop(key_name, None)

                x, y = calculate_axis()
                ui.write(ecodes.EV_ABS, ecodes.ABS_X, x)
                ui.write(ecodes.EV_ABS, ecodes.ABS_Y, y)
                ui.syn()

if __name__ == '__main__':
    asyncio.run(keyboard_to_joystick())
