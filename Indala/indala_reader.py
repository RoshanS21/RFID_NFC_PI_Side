#!/usr/bin/env python3
import pigpio
import time
import logging
import sys

# --------------------- Configuration ---------------------

# GPIO pin assignments
DATA0_PIN = 23  # Green wire (Data 0)
DATA1_PIN = 18  # White wire (Data 1)

# Wiegand configuration
EXPECTED_BITS = 26          # Change to 34 if your reader uses 34-bit Wiegand
BIT_TIMEOUT = 0.5           # Time (in seconds) to wait before processing data
BOUNCE_TIME_MS = 50         # Debounce time in milliseconds

# Logging configuration
LOG_FILENAME = 'wiegand_reader.log'
LOG_LEVEL = logging.INFO    # Set to DEBUG for more detailed logs

# Reader information
READER_TYPE = "Indala Wiegand"

# --------------------- Logging Setup ---------------------

# Configure logging to file and console
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler(sys.stdout)
    ]
)

# --------------------- Global Variables ---------------------

wiegand_data = []
last_bit_time = time.time()

# --------------------- Callback Functions ---------------------

def data0_callback(gpio, level, tick):
    global wiegand_data, last_bit_time
    if level == 0:
        wiegand_data.append(0)
        last_bit_time = time.time()
        logging.debug(f"Data0 pulse detected on GPIO{gpio}. Bit appended: 0")
#        print("Data0 pulse detected")

def data1_callback(gpio, level, tick):
    global wiegand_data, last_bit_time
    if level == 0:
        wiegand_data.append(1)
        last_bit_time = time.time()
        logging.debug(f"Data1 pulse detected on GPIO{gpio}. Bit appended: 1")
 #       print("Data1 pulse detected")

# --------------------- Data Processing Function ---------------------

def process_wiegand_data():
    global wiegand_data
    if len(wiegand_data) >= EXPECTED_BITS:
        card_bits = ''.join(map(str, wiegand_data[:EXPECTED_BITS]))
        card_number = int(card_bits, 2)

        # Parsing based on Wiegand 26-bit format
        if EXPECTED_BITS == 26:
            # Typically: 1 start bit, 8 facility code bits, 16 card number bits, 1 parity bit
            facility_code = int(card_bits[1:9], 2)
            card_number = int(card_bits[9:25], 2)
        elif EXPECTED_BITS == 34:
            # Implement parsing for 34-bit Wiegand if needed
            # This is an example and should be adjusted based on your reader's specification
            facility_code = int(card_bits[1:9], 2)
            card_number = int(card_bits[9:33], 2)
        else:
            facility_code = None  # Not parsed
            # For non-standard bit lengths, adjust parsing accordingly

        # Log the information
        logging.info("--------------------------------------------------")
        logging.info("Card Read Detected:")
        logging.info(f"Reader Type    : {READER_TYPE}")
        logging.info(f"Binary Data    : {card_bits}")
        if facility_code is not None:
            logging.info(f"Facility Code  : {facility_code}")
        logging.info(f"Card Number    : {card_number}")
        logging.info("--------------------------------------------------")

        # Print to console
        print("\nCard Read Detected:")
        print(f"Reader Type   : {READER_TYPE}")
        print(f"Binary Data   : {card_bits}")
        if facility_code is not None:
            print(f"Facility Code : {facility_code}")
        print(f"Card Number   : {card_number}")
        print("--------------------------------------------------\n")

        # Clear the data for the next read
        wiegand_data = []

# --------------------- Main Function ---------------------

def main():
    global wiegand_data, last_bit_time

    # Initialize pigpio
    pi = pigpio.pi()
    if not pi.connected:
        logging.error("Failed to connect to pigpio daemon. Ensure that pigpiod is running.")
        sys.exit(1)

    # Set pull-up resistors for Data0 and Data1
    pi.set_pull_up_down(DATA0_PIN, pigpio.PUD_UP)
    pi.set_pull_up_down(DATA1_PIN, pigpio.PUD_UP)

    # Register callbacks
    cb0 = pi.callback(DATA0_PIN, pigpio.FALLING_EDGE, data0_callback)
    cb1 = pi.callback(DATA1_PIN, pigpio.FALLING_EDGE, data1_callback)

    logging.info("Starting Wiegand Reader. Press Ctrl+C to exit.")
    print("Starting Wiegand Reader. Press Ctrl+C to exit.")

    try:
        while True:
            current_time = time.time()
            if wiegand_data and (current_time - last_bit_time) > BIT_TIMEOUT:
                if len(wiegand_data) >= EXPECTED_BITS:
                    process_wiegand_data()
                else:
                    logging.warning(f"Incomplete Wiegand data received: {wiegand_data}")
                    print("Warning: Incomplete Wiegand data received.")
                    wiegand_data = []
            elif len(wiegand_data) >= EXPECTED_BITS:
                process_wiegand_data()
            time.sleep(0.05)  # Sleep briefly to reduce CPU usage
    except KeyboardInterrupt:
        logging.info("Exiting program due to keyboard interrupt.")
        print("\nExiting program.")
    finally:
        # Clean up callbacks and pigpio
        cb0.cancel()
        cb1.cancel()
        pi.stop()
        logging.info("Cleaned up GPIO and stopped pigpio.")
        print("Cleaned up GPIO and stopped pigpio.")

# --------------------- Entry Point ---------------------

if __name__ == "__main__":
    main()
