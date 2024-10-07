import pigpio
import time

# Define GPIO pins
DATA0_PIN = 23
DATA1_PIN = 18

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    exit()

# Define callback functions
def data0_callback(gpio, level, tick):
    if level == 0:
        print("Data0 pulse detected")

def data1_callback(gpio, level, tick):
    if level == 0:
        print("Data1 pulse detected")

# Set up edge detection
pi.set_pull_up_down(DATA0_PIN, pigpio.PUD_UP)
pi.set_pull_up_down(DATA1_PIN, pigpio.PUD_UP)

cb0 = pi.callback(DATA0_PIN, pigpio.FALLING_EDGE, data0_callback)
cb1 = pi.callback(DATA1_PIN, pigpio.FALLING_EDGE, data1_callback)

print("Listening for pulses. Press Ctrl+C to exit.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nExiting program")
finally:
    cb0.cancel()
    cb1.cancel()
    pi.stop()
