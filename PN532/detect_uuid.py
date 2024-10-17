import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def main():
    pn532 = initialize_pn532()
    if pn532 is None:
        logging.error("Failed to initialize PN532. Exiting.")
        return

    logging.info("UID Detection Script is active. Waiting for RFID/NFC cards...")

    try:
        while True:
            # Read a passive target (card) for 0.5 seconds
            uid = pn532.read_passive_target(timeout=0.5)
            if uid is None:
                continue  # No card detected, continue waiting

            # Format UID for logging and comparison
            uid_str = ' '.join([f'{byte:02X}' for byte in uid])
            logging.info(f"Detected card with UID: {uid_str}")

            # Wait a short period before next scan
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Exiting...")

if __name__ == "__main__":
    main()
