// wiegand_pigpio_reader.cpp
#include <pigpio.h>
#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <ctime>
#include <csignal>
#include <unistd.h>

// --------------------- Configuration ---------------------

// GPIO pin assignments
const int DATA0_PIN = 23; // Green wire (Data 0) - BCM GPIO23
const int DATA1_PIN = 18; // White wire (Data 1) - BCM GPIO18

// Wiegand configuration
const int EXPECTED_BITS = 26;      // Change to 34 if your reader uses 34-bit Wiegand
const double BIT_TIMEOUT = 0.5;    // Time (in seconds) to wait before processing data
const unsigned int DEBOUNCE_TIME_MS = 50; // Debounce time in milliseconds

// Logging configuration
const std::string LOG_FILENAME = "wiegand_reader.log";

// Reader information
const std::string READER_TYPE = "Indala Wiegand";

// --------------------- Global Variables ---------------------

std::vector<int> wiegand_data;
double last_bit_time = 0.0;

// Log file stream
std::ofstream log_file;

// --------------------- Utility Functions ---------------------

std::string get_current_timestamp() {
    std::time_t now = std::time(nullptr);
    std::tm* now_tm = std::localtime(&now);
    char buffer[20];
    std::strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", now_tm);
    return std::string(buffer);
}

void log_message(const std::string& level, const std::string& message) {
    std::string timestamp = get_current_timestamp();
    std::string log_entry = timestamp + " [" + level + "] " + message;
    // Write to log file
    if (log_file.is_open()) {
        log_file << log_entry << std::endl;
    }
    // Also print to console
    if (level == "INFO" || level == "WARNING" || level == "ERROR") {
        std::cout << log_entry << std::endl;
    }
}

// --------------------- Callback Functions ---------------------

// Forward declaration
void process_wiegand_data();

// Callback for Data0 (appends 0)
void data0_callback(int gpio, int level, uint32_t tick) {
    if (level == 0) { // Falling edge
        wiegand_data.push_back(0);
        last_bit_time = gpioTick() / 1e6; // Convert microseconds to seconds
        log_message("DEBUG", "Data0 pulse detected on GPIO" + std::to_string(gpio) + ". Bit appended: 0");
        std::cout << "Data0 pulse detected" << std::endl;

        // Check if expected bits reached
        if (wiegand_data.size() >= EXPECTED_BITS) {
            process_wiegand_data();
        }
    }
}

// Callback for Data1 (appends 1)
void data1_callback(int gpio, int level, uint32_t tick) {
    if (level == 0) { // Falling edge
        wiegand_data.push_back(1);
        last_bit_time = gpioTick() / 1e6; // Convert microseconds to seconds
        log_message("DEBUG", "Data1 pulse detected on GPIO" + std::to_string(gpio) + ". Bit appended: 1");
        std::cout << "Data1 pulse detected" << std::endl;

        // Check if expected bits reached
        if (wiegand_data.size() >= EXPECTED_BITS) {
            process_wiegand_data();
        }
    }
}

// --------------------- Data Processing Function ---------------------

void process_wiegand_data() {
    if (wiegand_data.size() >= EXPECTED_BITS) {
        // Convert bits to binary string
        std::string card_bits = "";
        for (int bit : wiegand_data) {
            card_bits += std::to_string(bit);
        }

        // Convert binary string to integer
        unsigned long card_value = std::stoul(card_bits, nullptr, 2);

        // Calculate required hex digits
        int required_hex_digits = (EXPECTED_BITS + 3) / 4; // 4 bits per hex digit

        // Convert to hex string with leading zeros
        std::stringstream ss;
        ss << std::uppercase << std::hex << std::setw(required_hex_digits) << std::setfill('0') << card_value;
        std::string card_hex = ss.str();

        // Parsing based on Wiegand 26-bit format
        unsigned long facility_code = 0;
        unsigned long card_number = 0;

        if (EXPECTED_BITS == 26) {
            // 1 start bit, 8 facility code bits, 16 card number bits, 1 parity bit
            std::string facility_code_bits = card_bits.substr(1, 8);
            std::string card_number_bits = card_bits.substr(9, 16);
            facility_code = std::stoul(facility_code_bits, nullptr, 2);
            card_number = std::stoul(card_number_bits, nullptr, 2);
        } else if (EXPECTED_BITS == 34) {
            // Example parsing for 34-bit Wiegand
            // Adjust based on your reader's specification
            std::string facility_code_bits = card_bits.substr(1, 8);
            std::string card_number_bits = card_bits.substr(9, 24);
            facility_code = std::stoul(facility_code_bits, nullptr, 2);
            card_number = std::stoul(card_number_bits, nullptr, 2);
        } else {
            // Handle other bit lengths if necessary
        }

        // Logging
        log_message("INFO", "--------------------------------------------------");
        log_message("INFO", "Card Read Detected:");
        log_message("INFO", "Reader Type    : " + READER_TYPE);
        log_message("INFO", "Binary Data    : " + card_bits);
        log_message("INFO", "Hex Data       : " + card_hex);
        if (EXPECTED_BITS == 26 || EXPECTED_BITS == 34) {
            log_message("INFO", "Facility Code  : " + std::to_string(facility_code));
        }
        log_message("INFO", "Card Number    : " + std::to_string(card_number));
        log_message("INFO", "--------------------------------------------------");

        // Console Output
        std::cout << "\nCard Read Detected:" << std::endl;
        std::cout << "Reader Type   : " << READER_TYPE << std::endl;
        std::cout << "Binary Data   : " << card_bits << std::endl;
        std::cout << "Hex Data      : " << card_hex << std::endl;
        if (EXPECTED_BITS == 26 || EXPECTED_BITS == 34) {
            std::cout << "Facility Code : " << facility_code << std::endl;
        }
        std::cout << "Card Number   : " << card_number << std::endl;
        std::cout << "--------------------------------------------------\n" << std::endl;

        // Clear the data for the next read
        wiegand_data.clear();
    }
}

// --------------------- Timeout Handling Function ---------------------

void check_timeout() {
    if (!wiegand_data.empty()) {
        double current_time = gpioTick() / 1e6; // Current time in seconds
        if ((current_time - last_bit_time) > BIT_TIMEOUT) {
            if (wiegand_data.size() >= EXPECTED_BITS) {
                process_wiegand_data();
            } else {
                // Log incomplete data
                std::stringstream ss;
                ss << "Incomplete Wiegand data received (" << wiegand_data.size() << " bits): ";
                for (int bit : wiegand_data) {
                    ss << bit;
                }
                log_message("WARNING", ss.str());
                std::cout << "Warning: Incomplete Wiegand data received." << std::endl;
                wiegand_data.clear();
            }
        }
    }
}

// --------------------- Signal Handler ---------------------

volatile bool keep_running = true;

void signal_handler(int signum) {
    keep_running = false;
}

// --------------------- Main Function ---------------------

int main() {
    // Open log file
    log_file.open(LOG_FILENAME, std::ios::out | std::ios::app);
    if (!log_file.is_open()) {
        std::cerr << "Error: Unable to open log file: " << LOG_FILENAME << std::endl;
        return 1;
    }

    // Register signal handler for graceful shutdown
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    // Initialize pigpio
    if (gpioInitialise() < 0) {
        log_message("ERROR", "pigpio initialization failed.");
        return 1;
    }

    // Set GPIO modes
    gpioSetMode(DATA0_PIN, PI_INPUT);
    gpioSetMode(DATA1_PIN, PI_INPUT);

    // Set pull-up resistors
    gpioSetPullUpDown(DATA0_PIN, PI_PUD_UP);
    gpioSetPullUpDown(DATA1_PIN, PI_PUD_UP);

    // Register callbacks
    int cb0 = gpioSetAlertFunc(DATA0_PIN, data0_callback);
    if (cb0 < 0) {
        log_message("ERROR", "Failed to set callback for DATA0_PIN.");
        gpioTerminate();
        return 1;
    }

    int cb1 = gpioSetAlertFunc(DATA1_PIN, data1_callback);
    if (cb1 < 0) {
        log_message("ERROR", "Failed to set callback for DATA1_PIN.");
        gpioSetAlertFunc(DATA0_PIN, nullptr); // Remove previous callback
        gpioTerminate();
        return 1;
    }

    log_message("INFO", "Starting Wiegand Reader. Press Ctrl+C to exit.");
    std::cout << "Starting Wiegand Reader. Press Ctrl+C to exit." << std::endl;

    // Main loop
    while (keep_running) {
        check_timeout();
        time_sleep(0.05); // Sleep for 50 milliseconds
    }

    log_message("INFO", "Exiting program due to interrupt.");
    std::cout << "\nExiting program." << std::endl;

    // Clean up callbacks
    gpioSetAlertFunc(DATA0_PIN, nullptr);
    gpioSetAlertFunc(DATA1_PIN, nullptr);

    // Close log file
    if (log_file.is_open()) {
        log_file.close();
    }

    // Terminate pigpio
    gpioTerminate();

    log_message("INFO", "Cleaned up GPIO and stopped pigpio.");
    std::cout << "Cleaned up GPIO and stopped pigpio." << std::endl;

    return 0;
}
