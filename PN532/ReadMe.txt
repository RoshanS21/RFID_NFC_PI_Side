I2C Configuration on the PN532 Breakout Board
The PN532 breakout board can be configured to use different communication protocols. In this project, we will use the I2C protocol.

Jumper Settings for I2C
To use the I2C protocol on the PN532 board, set the jumpers as follows:

SEL0 = ON
SEL1 = OFF
This configures the PN532 to use I2C communication.

GPIO Pin Connections
Below are the connections between the Raspberry Pi GPIO pins and the PN532 breakout board for I2C communication:

Raspberry Pi Pin	PN532 Pin	Description
3.3V (Pin 1)	    3.3V    	Power supply for PN532 board
GND (Pin 6)	        GND	        Ground
SCL (Pin 5)	        SCL	        I2C Clock (SCL)
SDA (Pin 3)	        SDA	        I2C Data (SDA)
GPIO 12 (Pin 32)	P32	        Optional, IRQ/interrupt pin
GPIO 6 (Pin 31)	    RSTPD_N	    Reset pin

Explanation of Pins
    3.3V: Powers the PN532 breakout board.
    GND: Ground connection.
    SCL: Clock line for I2C communication.
    SDA: Data line for I2C communication.
    RSTPD_N: Used to reset the PN532. You can control this pin to reset the NFC reader.
    P32: Can be used as an IRQ (Interrupt Request) pin, although this is optional for basic communication.

Enabling I2C on Raspberry Pi
To enable I2C on the Raspberry Pi, follow these steps:
Open a terminal window on the Raspberry Pi.
Run the following command to open the Raspberry Pi configuration tool:
    sudo raspi-config
Navigate to Interfacing Options > I2C and enable I2C.
Reboot the Raspberry Pi to apply the changes:
    sudo reboot

Verifying the I2C Connection
Once the I2C interface is enabled, you can verify the connection between the Raspberry Pi and the PN532 board by using the following command:
    sudo i2cdetect -y 1
This will scan the I2C bus and display the address of the connected devices. The PN532 breakout board should appear with an address like 0x24.
