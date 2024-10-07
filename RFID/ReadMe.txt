Ensure the wiring is as follows:

Wiring Diagram:
Here is how you connect the RC522 module to the Raspberry Pi:

RFID RC522 Pin	Raspberry Pi Pin	GPIO Number	Function
VCC		Pin 1			3.3V		Power
GND		Pin 6			GND		Ground
MISO		Pin 21			GPIO 9		Master In Slave Out
MOSI		Pin 19			GPIO 10		Master Out Slave In
SCK		Pin 23			GPIO 11		Clock
SDA		Pin 24			GPIO 8		Chip Select (CS)
RST		Pin 22			GPIO 25		Reset


Software Setup

Update your system:
sudo apt update
sudo apt upgrade

Install Required Libraries:
sudo apt install python3-pip python3-dev spi-tools
pip3 install spidev mfrc522 requests RPi.GPIO

Enable SPI Interface:
Run raspi-config:
sudo raspi-config
Go to Interfacing Options > SPI and enable it.

