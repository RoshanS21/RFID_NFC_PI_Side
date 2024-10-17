import board
import busio
from digitalio import DigitalInOut, Direction
from adafruit_pn532.i2c import PN532_I2C
import logging
import time
import RPi.GPIO as GPIO
from authorized_uids import AUTHORIZED_UIDS  # Import the authorized UIDs list

# Configure logging to also output to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("access_control.log"),
        logging.StreamHandler()
    ]
)

# Define GPIO pins for relay
RELAY_SET_PIN = 27    # GPIO27 connected to relay's SET pin (Unlock)
RELAY_UNSET_PIN = 17  # GPIO17 connected to relay's UNSET pin (Lock)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_SET_PIN, GPIO.OUT)
GPIO.setup(RELAY_UNSET_PIN, GPIO.OUT)

# Ensure relay pins are low initially
GPIO.output(RELAY_SET_PIN, GPIO.LOW)
GPIO.output(RELAY_UNSET_PIN, GPIO.LOW)

# Cooldown parameters to prevent multiple rapid activations
COOLDOWN_TIME = 5  # seconds
last_activation_time = 0

def initialize_pn532():
    """
    Initialize the PN532 NFC/RFID module over I2C.
    Returns the PN532 object if successful, else None.
    """
    try:
        # Define reset and request pins
        reset_pin = DigitalInOut(board.D6)
        req_pin = DigitalInOut(board.D12)

        # Initialize I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)

        # Initialize PN532 with I2C connection
        pn532 = PN532_I2C(i2c, reset=reset_pin, req=req_pin)

        # Get firmware version
        ic, ver, rev, support = pn532.firmware_version
        logging.info(f'Found PN532 with firmware version: {ver}.{rev}')

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        return pn532
    except Exception as e:
        logging.error(f"Error initializing PN532: {e}")
        return None

def activate_relay():
    """
    Activates the relay to unlock the door for 5 seconds, then locks it again.
    """
    global last_activation_time
    try:
        # Update the last activation time
        last_activation_time = time.time()

        logging.info("Activating relay to unlock the door...")
        # Pulse the SET pin to unlock
        GPIO.output(RELAY_SET_PIN, GPIO.HIGH)
        time.sleep(0.1)  # 100 ms pulse
        GPIO.output(RELAY_SET_PIN, GPIO.LOW)

        # Keep the door unlocked for 5 seconds
        logging.info("Door unlocked. Keeping it unlocked for 5 seconds...")
        time.sleep(5)

        # Pulse the UNSET pin to lock
        logging.info("Deactivating relay to lock the door...")
        GPIO.output(RELAY_UNSET_PIN, GPIO.HIGH)
        time.sleep(0.1)  # 100 ms pulse
        GPIO.output(RELAY_UNSET_PIN, GPIO.LOW)

        logging.info("Door locked successfully.")
    except Exception as e:
        logging.error(f"Error activating relay: {e}")

def main():
    pn532 = initialize_pn532()
    if pn532 is None:
        logging.error("Failed to initialize PN532. Exiting program.")
        return

    logging.info("Access Control System is active. Waiting for RFID/NFC cards...")

    while True:
        try:
            current_time = time.time()
            # Implement cooldown to prevent multiple activations
            if current_time - last_activation_time < COOLDOWN_TIME:
                time.sleep(0.1)
                continue

            # Read a passive target (card) for 0.5 seconds
            uid = pn532.read_passive_target(timeout=0.5)
            if uid is None:
                continue  # No card detected, continue waiting

            # Format UID for logging and comparison
            uid_str = ' '.join([f'{byte:02X}' for byte in uid])
            logging.info(f"Detected card with UID: {uid_str}")

            if uid in AUTHORIZED_UIDS:
                logging.info("Access granted. Authorized card detected.")
                activate_relay()
            else:
                logging.warning("Access denied. Unauthorized card detected.")

            # Small delay to prevent multiple scans in quick succession
            time.sleep(1)

        except KeyboardInterrupt:
            logging.info("Program interrupted by user. Exiting...")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    # Clean up GPIO settings before exiting
    GPIO.cleanup()

if __name__ == "__main__":
    main()
