import os
from evdev import UInput, ecodes as e, AbsInfo
import time
import signal
import sys

# Ensure /dev/uinput exists and open with correct permissions
UINPUT_DEV = '/dev/uinput'
if not os.access(UINPUT_DEV, os.W_OK):
    print(f"Error: Cannot write to {UINPUT_DEV}. Try running with sudo or check permissions.")
    sys.exit(1)

# Create the virtual joystick device
ui = UInput(
    events={
        e.EV_ABS: [
            (e.ABS_X, AbsInfo(0, 0, 255, 0, 0, 0)),
            (e.ABS_Y, AbsInfo(0, 0, 255, 0, 0, 0))
        ],
        e.EV_KEY: [e.BTN_TRIGGER, e.BTN_THUMB]
    },
    name="Virtual Joystick",
    version=0x3
)

# Clean exit handler
def handle_exit(sig, frame):
    print("\nClosing virtual joystick...")
    ui.close()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

print("Virtual joystick running. Open jstest-gtk to view. Press Ctrl+C to exit.")

x, y = 0, 255
step = 10
trigger = 0
thumb = 0

def update_state():
    global x, y, trigger, thumb

    print(f"Sending events: ABS_X={x}, ABS_Y={y}, BTN_TRIGGER={trigger}, BTN_THUMB={thumb}")
    ui.write(e.EV_ABS, e.ABS_X, x)
    ui.write(e.EV_ABS, e.ABS_Y, y)
    ui.write(e.EV_KEY, e.BTN_TRIGGER, trigger)
    ui.write(e.EV_KEY, e.BTN_THUMB, thumb)
    ui.syn()

    x = (x + step) % 256
    y = (y - step) % 256
    trigger ^= 1
    thumb ^= 1

# Run until interrupted, allowing jstest-gtk to detect events
while True:
    update_state()
    time.sleep(0.5)
