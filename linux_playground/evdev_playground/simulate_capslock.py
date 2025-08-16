from evdev import UInput, ecodes
import time

def simulate_capslock():
    # Create a virtual input device
    with UInput() as ui:
        # Simulate Caps Lock key-down
        ui.write(ecodes.EV_KEY, ecodes.KEY_CAPSLOCK, 1)
        time.sleep(0.1)  # Small delay to simulate a real key press

        # Simulate Caps Lock key-up
        ui.write(ecodes.EV_KEY, ecodes.KEY_CAPSLOCK, 0)

        # Synchronize the events at the end
        ui.syn()

def main():
    print("Simulating Caps Lock key press using evdev...")
    simulate_capslock()
    print("Caps Lock key press simulated.")

if __name__ == "__main__":
    main()
