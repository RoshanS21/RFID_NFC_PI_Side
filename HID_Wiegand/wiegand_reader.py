import pigpio
import time

class WiegandReader:
    def __init__(self, pi, gpio_0, gpio_1):
        self.pi = pi
        self.gpio_0 = gpio_0
        self.gpio_1 = gpio_1
        self._data = []
        
        # Set the GPIO pins to input mode
        self.pi.set_mode(self.gpio_0, pigpio.INPUT)
        self.pi.set_mode(self.gpio_1, pigpio.INPUT)

        # Add callbacks for data lines D0 and D1
        self._cb_0 = self.pi.callback(self.gpio_0, pigpio.FALLING_EDGE, self._data_received)
        self._cb_1 = self.pi.callback(self.gpio_1, pigpio.FALLING_EDGE, self._data_received)

    def _data_received(self, gpio, level, tick):
        # Wiegand sends bits in a sequence via D0 and D1
        if gpio == self.gpio_0:
            self._data.append(0)
        elif gpio == self.gpio_1:
            self._data.append(1)

    def get_card_data(self):
        if self._data:
            return self._data
        return None

    def clear(self):
        self._data = []

if __name__ == "__main__":
    # Initialize the pigpio library
    pi = pigpio.pi()
    
    # Wiegand reader on GPIO 17 (D0) and GPIO 27 (D1)
    reader = WiegandReader(pi, 17, 27)

    print("Waiting for card...")
    
    while True:
        card_data = reader.get_card_data()
        
        if card_data:
            # Convert the binary list to a string of bits
            card_data_str = ''.join(map(str, card_data))

            # Convert binary string to integer, then to hex
            card_data_hex = hex(int(card_data_str, 2)).upper()

            print(f"Card Data (Binary): {card_data_str}")
            print(f"Card Data (Hex): {card_data_hex}")
            
            # Print a blank line to separate outputs
            print("\n")

            # Clear the data buffer for the next read
            reader.clear()
        
        # Sleep for 3 seconds between loops
        time.sleep(3)
