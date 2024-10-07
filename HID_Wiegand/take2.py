from gpiozero import Button
import time

# Set the GPIO pins for Data 0 and Data 1
DATA0_PIN = 27  # Change to GPIO27
DATA1_PIN = 17  # Change to GPIO17

# Variables to hold Wiegand data
wiegand_data = []

def data0_callback():
    global wiegand_data
    wiegand_data.append(0)

def data1_callback():
    global wiegand_data
    wiegand_data.append(1)

# Use gpiozero Button for edge detection
data0_button = Button(DATA0_PIN, pull_up=True)
data1_button = Button(DATA1_PIN, pull_up=True)

data0_button.when_pressed = data0_callback
data1_button.when_pressed = data1_callback

def process_wiegand_data():
    global wiegand_data
    if len(wiegand_data) >= 26:  # Assuming 26-bit Wiegand
        print("\nCard Read Detected:")
        card_bits = ''.join(map(str, wiegand_data))
        card_number = int(card_bits, 2)  # Convert bits to a number
        print(f"Binary Data: {card_bits}")
        print(f"Card Number: {card_number}")
        print("Reader Type: Indala Wiegand")
        print("")  # Blank line to separate readings
        wiegand_data = []  # Clear for next read

try:
    while True:
        time.sleep(0.1)
        process_wiegand_data()

except KeyboardInterrupt:
    print("Exiting program")
from gpiozero import Button
import time

# Set the GPIO pins for Data 0 and Data 1
DATA0_PIN = 27  # Change to GPIO27
DATA1_PIN = 17  # Change to GPIO17

# Variables to hold Wiegand data
wiegand_data = []

def data0_callback():
    global wiegand_data
    wiegand_data.append(0)

def data1_callback():
    global wiegand_data
    wiegand_data.append(1)

# Use gpiozero Button for edge detection
data0_button = Button(DATA0_PIN, pull_up=True)
data1_button = Button(DATA1_PIN, pull_up=True)

data0_button.when_pressed = data0_callback
data1_button.when_pressed = data1_callback

def process_wiegand_data():
    global wiegand_data
    if len(wiegand_data) >= 26:  # Assuming 26-bit Wiegand
        print("\nCard Read Detected:")
        card_bits = ''.join(map(str, wiegand_data))
        card_number = int(card_bits, 2)  # Convert bits to a number
        print(f"Binary Data: {card_bits}")
        print(f"Card Number: {card_number}")
        print("Reader Type: Indala Wiegand")
        print("")  # Blank line to separate readings
        wiegand_data = []  # Clear for next read

try:
    while True:
        time.sleep(0.1)
        process_wiegand_data()

except KeyboardInterrupt:
    print("Exiting program")
