import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
import logging
import sys

# Configure logging to output to the command line
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_pn532():
    """
    Initialize the PN532 NFC/RFID module over I2C.
    Returns the PN532 object if successful, else None.
    """
    try:
        # Define the reset and request pins
        reset_pin = DigitalInOut(board.D6)
        req_pin = DigitalInOut(board.D12)

        # Initialize I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)

        # Initialize PN532 with I2C connection
        pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)

        # Get firmware version
        ic, ver, rev, support = pn532.firmware_version
        logging.info(f'Found PN532 with firmware version: {ver}.{rev}')

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        return pn532

    except Exception as e:
        logging.error(f"Error initializing PN532: {e}")
        return None

def read_card(pn532):
    """
    Continuously scan for NFC/RFID cards and display their UIDs.
    If the card is MiFare Classic, attempt to read a memory block.
    """
    logging.info("Waiting for RFID/NFC card...")

    try:
        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=0.5)

            # Try again if no card is available
            if uid is None:
                continue

            # Format UID for display
            uid_str = ' '.join([f'{byte:02X}' for byte in uid])
            logging.info(f'Found card with UID: {uid_str}')

            # Attempt to read MiFare Classic blocks
            try:
                # Access the MiFare class
                mifare = pn532.mifare

                # Select the card
                if not mifare.select(uid):
                    logging.warning("Failed to select the card.")
                    continue

                # Default key for MiFare Classic
                DEFAULT_KEY = b'\xFF\xFF\xFF\xFF\xFF\xFF'

                # Define block to read (e.g., block 4)
                BLOCK_NUMBER = 4

                # Authenticate block 4 with key A
                if mifare.authenticate(BLOCK_NUMBER, DEFAULT_KEY, PN532_I2C.MIFARE_CMD_AUTH_A):
                    logging.info(f'Authenticated block {BLOCK_NUMBER} successfully.')
                    # Read block data
                    block_data = mifare.read_block(BLOCK_NUMBER)
                    if block_data:
                        block_str = ' '.join([f'{byte:02X}' for byte in block_data])
                        logging.info(f'Block {BLOCK_NUMBER} Data: {block_str}')
                    else:
                        logging.warning(f'Failed to read block {BLOCK_NUMBER}')
                else:
                    logging.warning(f'Authentication failed for block {BLOCK_NUMBER}')

            except AttributeError:
                logging.info('Card is not a MiFare Classic card or does not support authentication.')

            except Exception as e:
                logging.error(f'Error handling MiFare Classic card: {e}')

            time.sleep(1)  # Prevent multiple detections of the same card

    except KeyboardInterrupt:
        logging.info("NFC scanning interrupted by user.")

    except Exception as e:
        logging.error(f"An error occurred during card reading: {e}")

def main():
    pn532 = initialize_pn532()
    if pn532 is None:
        logging.error("Failed to initialize PN532. Exiting program.")
        sys.exit(1)

    read_card(pn532)

if __name__ == "__main__":
    main()
