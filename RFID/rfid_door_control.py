import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import requests
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the RFID reader
reader = SimpleMFRC522()

# Relay pin setup
relay_pin = 17

# Ensure GPIO is cleaned up before setting mode
GPIO.cleanup()

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)

# Network Communication
def verify_card(card_id):
    server_url = "https://beca-76-234-147-61.ngrok-free.app/verify"
    data = {"card_id": str(card_id)}
    try:
        response = requests.post(server_url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error communicating with server: {e}")
        return None

# Send door status to server
def send_door_status(status):
    status_url = "https://beca-76-234-147-61.ngrok-free.app/door-status"
    data = {"status": status}
    try:
        response = requests.post(status_url, json=data, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error sending door status: {e}")

# Relay Control
def control_door(open_door):
    GPIO.output(relay_pin, GPIO.HIGH if open_door else GPIO.LOW)
    logging.info(f"Door {'opened' if open_door else 'locked'}")

# Main workflow
def main():
    try:
        while True:
            logging.info("Place your card to read")
            card_id, text = reader.read()
            logging.info(f"Card read: ID={card_id}, Text={text}")
            
            result = verify_card(card_id)
            if result and result.get("authorized"):
                control_door(True)
                send_door_status("opened")
                time.sleep(5)  # Keep the door open for 5 seconds
                control_door(False)
            else:
                logging.info("Access denied")
                
            time.sleep(1)  # Polling interval
    except KeyboardInterrupt:
        logging.info("Program terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
