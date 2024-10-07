#include <iostream>
#include <pigpio.h>
#include <unistd.h>

#define DATA0_PIN 23
#define DATA1_PIN 18

class WiegandReader {
public:
    WiegandReader() {
        // Initialize GPIO
        if (gpioInitialise() < 0) {
            std::cerr << "Failed to initialize pigpio." << std::endl;
            exit(1);
        }

        // Set up GPIO pins as inputs
        gpioSetMode(DATA0_PIN, PI_INPUT);
        gpioSetMode(DATA1_PIN, PI_INPUT);

        // Attach interrupt handlers
        gpioSetAlertFunc(DATA0_PIN, data0Callback);
        gpioSetAlertFunc(DATA1_PIN, data1Callback);
    }

    ~WiegandReader() {
        gpioTerminate();
    }

    static void data0Callback(int gpio, int level, uint32_t tick) {
        // Handle Data 0
        std::cout << "Data 0: " << level << " at " << tick << std::endl;
    }

    static void data1Callback(int gpio, int level, uint32_t tick) {
        // Handle Data 1
        std::cout << "Data 1: " << level << " at " << tick << std::endl;
    }

    void run() {
        // Keep the program running
        while (true) {
            sleep(1);
        }
    }
};

int main() {
    WiegandReader reader;
    reader.run();
    return 0;
}
