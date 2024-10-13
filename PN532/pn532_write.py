import time
import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
import logging
import sys

# Define the MIFARE authentication command for Key A
MIFARE_CMD_AUTH_A = 0x60

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

def write_to_card(pn532, block_number, data, key=b'\xFF\xFF\xFF\xFF\xFF\xFF'):
    """
    Authenticate and write data to a specified block on a MiFare Classic card.
    """
    logging.info(f"Attempting to write to block {block_number}...")

    try:
        # Wait for a card
        logging.info("Waiting for RFID/NFC card to write...")
        uid = pn532.read_passive_target(timeout=10)

        if uid is None:
            logging.error("No card detected. Please place a MiFare Classic 1K card near the reader.")
            return

        # Format UID for display
        uid_str = ' '.join([f'{byte:02X}' for byte in uid])
        logging.info(f'Found card with UID: {uid_str}')

        # Authenticate the block with Key A
        if pn532.mifare_classic_authenticate_block(block_number, MIFARE_CMD_AUTH_A, key):
            logging.info(f'Authenticated block {block_number} successfully.')
            # Write data to the block
            success = pn532.mifare_classic_write_block(block_number, data)
            if success:
                logging.info(f'Data written to block {block_number}: {data.hex()}')
            else:
                logging.error(f'Failed to write data to block {block_number}.')
        else:
            logging.error(f'Authentication failed for block {block_number}.')

    except Exception as e:
        logging.error(f"An error occurred during writing: {e}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python pn532_write.py <block_number> <data_hex>")
        print("Example: python pn532_write.py 4 AABBCCDDEEFF00112233445566778899")
        sys.exit(1)

    try:
        block_number = int(sys.argv[1])
    except ValueError:
        logging.error("Invalid block number. It must be an integer.")
        sys.exit(1)

    data_hex = sys.argv[2]

    # Convert hex string to bytes
    try:
        data = bytes.fromhex(data_hex)
        if len(data) != 16:
            logging.error("Data must be exactly 16 bytes (32 hex characters) for a MiFare Classic block.")
            sys.exit(1)
    except ValueError:
        logging.error("Invalid hex data provided.")
        sys.exit(1)

    pn532 = initialize_pn532()
    if pn532 is None:
        logging.error("Failed to initialize PN532. Exiting program.")
        sys.exit(1)

    write_to_card(pn532, block_number, data)

if __name__ == "__main__":
    main()
