import board
import busio
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize I2C and PN532
reset_pin = DigitalInOut(board.D6)
req_pin = DigitalInOut(board.D12)
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, reset=reset_pin, req=req_pin)

# Get firmware version
try:
    ic, ver, rev, support = pn532.firmware_version
    logging.info(f'Found PN532 with firmware version: {ver}.{rev}')
except Exception as e:
    logging.error(f"Failed to get firmware version: {e}")
    exit()

# Configure PN532 to communicate with MiFare cards
try:
    pn532.SAM_configuration()
except Exception as e:
    logging.error(f"Failed to configure SAM: {e}")
    exit()

# Wait for a card
logging.info("Waiting for RFID/NFC card...")
uid = pn532.read_passive_target(timeout=10)

if uid is None:
    logging.error("No card detected.")
    exit()

uid_str = ' '.join([f'{byte:02X}' for byte in uid])
logging.info(f"Found card with UID: {uid_str}")

# Define known SAK mappings (extend as needed)
sak_card_mapping = {
    0x08: "MiFare Ultralight",
    0x18: "MiFare Classic 1K",
    0x20: "NTAG213",
    0x28: "NTAG215",
    0x30: "NTAG216",
    0x40: "MiFare Plus (Configured)",
    0x60: "MiFare DESFire EV1",
    # Add more mappings as needed
}

# Since we cannot retrieve SAK and ATQA directly, infer based on UID
# Example assumption: UID starting with 0x33 is NTAG213
first_byte = uid[0]

if first_byte == 0x33:
    card_type = "NTAG213"
elif first_byte == 0x04:
    card_type = "MiFare Classic 1K"
else:
    card_type = "Unknown or unsupported"

logging.info(f"Assumed Card Type: {card_type}")

# Proceed based on assumed card type
if "NTAG" in card_type:
    logging.info("This is an NTAG card. You can perform NDEF operations.")
elif "MiFare Classic" in card_type:
    logging.info("This is a MiFare Classic card. You can perform sector-based operations.")
else:
    logging.warning("Card type is unknown or unsupported for standard operations.")
