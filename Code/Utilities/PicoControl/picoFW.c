// Description: This code initializes all GPIO pins on a Raspberry Pi Pico,
// controls GPIO pins based on parsed commands from a serial input,
#include "pico/stdlib.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

int scope1_EN = 6; // GPIO pin for Scope1 enable
int scope2_EN = 7; // GPIO pin for Scope2 enable
int wavegen2_EN = 8; // GPIO pin for Wavegen2 enable

int scope1_S0 = 20; // GPIO pin for Scope1 S0
int scope1_S1 = 21; // GPIO pin for Scope1 S1
int scope1_S2 = 22; // GPIO pin for Scope1 S2
int scope1_S3 = 26; // GPIO pin for Scope1 S3
int scope1_S4 = 27; // GPIO pin for Scope1 S4

int scope2_S0 = 19; // GPIO pin for Scope2 S0
int scope2_S1 = 18; // GPIO pin for Scope2 S1
int scope2_S2 = 17; // GPIO pin for Scope2 S2
int scope2_S3 = 16; // GPIO pin for Scope2 S3
int scope2_S4 = 9; // GPIO pin for Scope2 S4

int wavegen2_S0 = 14; // GPIO pin for Wavegen2 S0
int wavegen2_S1 = 13; // GPIO pin for Wavegen2 S1
int wavegen2_S2 = 12; // GPIO pin for Wavegen2 S2
int wavegen2_S3 = 11; // GPIO pin for Wavegen2 S3
int wavegen2_S4 = 10; // GPIO pin for Wavegen2 S4

// Function to initialize all GPIO pins
void initialize_all_gpio(void) {
    for (uint gpio_num = 0; gpio_num <= 29; gpio_num++) {
        gpio_init(gpio_num);
        gpio_set_dir(gpio_num, GPIO_OUT); // Set all GPIO pins as output
        gpio_put(gpio_num, false);       // Set all GPIO pins to low initially
    }
}

// Function to control a GPIO pin (set or clear)
void pico_gpio_control(uint gpio_num, bool gpio_on)  
{
    if (gpio_num > 29) { // Check if the GPIO number is within valid bounds
        return;
    }
    gpio_put(gpio_num, gpio_on);
}

// Function to blink the LED
void blink(int count, int delay_ms) {
    for (int i = 0; i < count; i++) {
        pico_gpio_control(PICO_DEFAULT_LED_PIN, 1);
        sleep_ms(delay_ms);
        pico_gpio_control(PICO_DEFAULT_LED_PIN, 0);
        sleep_ms(delay_ms);
    }
}

// Struct to hold the parsed values
typedef struct {
    unsigned int value1;
    unsigned int value2;
} ParsedCommand;

// Function to parse the command string
ParsedCommand parse_command(const char *command) {
    ParsedCommand result = {0, 0}; // Initialize the struct with default values

    // Find the position of the underscore
    char *underscore_pos = strchr(command, '_');
    if (underscore_pos == NULL) {
        // Handle invalid format (no underscore found)
        return result;
    }

    // Split the string into two parts
    *underscore_pos = '\0'; // Temporarily terminate the first part
    const char *part1 = command;
    const char *part2 = underscore_pos + 1;

    // Convert the parts to unsigned integers
    result.value1 = (unsigned int)strtoul(part1, NULL, 10);
    result.value2 = (unsigned int)strtoul(part2, NULL, 10);

    return result;
}
// Abstract the actual wiring to be 1 to 1 between devices
int muxToPicoMap[3][32] = {
    // here lebel refers to the schematic label number 
    // Scope1 (Index 0)
    {
        // Label 1-16 (Index 0-15) -> MUX IO (original value - 1)  ---- BUG index 15 wont map to wavegen2
         0,  1,  2,  3,  4,  5,  11,  10,  9,  8, 7, 6, 15, 14, 13, 12,
        // Label 17-32 (Index 16-31) -> MUX IO (original value - 1)
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
    },
    // Scope2 (Index 1)
    {
        // Label 1-16 (Index 0-15) -> MUX IO (original value - 1)
        11, 10,  9,  8,  7,  6,  0,  1,  2,  3,  4,  5, 28, 29, 30, 31,
        // Label 17-32 (Index 16-31) -> MUX IO (original value - 1)
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 12, 13, 14, 15
    },
    // Wavegen2 (Index 2) - Values for Labels 17-32 were assumed previously
    {
        // Label 1-16 (Index 0-15) -> MUX IO (original value - 1)
        11, 10,  9,  8,  7,  6,  5,  4,  3,  2,  1,  0, 12, 13, 14, 15,
        // Label 17-32 (Index 16-31) -> Nothing connected
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
    }
};

// Function to handle parsed commands
void handle_parsed_command(ParsedCommand command) {
    
    // Check if the command is valid
    if ((command.value1 <= 2 || command.value2 <= 3) && (command.value1 >= 0 || command.value2 >= 0)) {
        if (command.value2 == 32) // Check for enable
        {
            //printf("Enable command: %u\n", command.value2);
            switch (command.value1) 
            { // Index to the mux
                case 0:
                    pico_gpio_control(scope1_EN, 1);

                    break;
                case 1:
                    pico_gpio_control(scope2_EN, 1);

                    break;
                case 2:
                    pico_gpio_control(wavegen2_EN, 1);

                    break;
                default:
                    // pass
                    break;
            }
        } 
        else if (command.value2 == 33) // Check for disable
        {
            //printf("Disable command: %u\n", command.value2);
            switch (command.value1) 
            { // Index to the mux
                case 0:
                    pico_gpio_control(scope1_EN, 0);

                    break;
                case 1:
                    pico_gpio_control(scope2_EN, 0);

                    break;
                case 2:
                    pico_gpio_control(wavegen2_EN, 0);

                    break;
                default:
                    // pass
                    break;
            } 
        }
        else // must be GPIO
        {
            bool value2Bits[5] = {false};
            for (int i = 0; i < 5; i++) 
            {
                value2Bits[i] = (muxToPicoMap[command.value1][command.value2] >> i) & 1; // Extract the bits
            }
        
            switch (command.value1) 
            { // Index to the mux
                case 0:
                    pico_gpio_control(scope1_EN, 1);
        
                    pico_gpio_control(scope1_S0, value2Bits[0]);
                    pico_gpio_control(scope1_S1, value2Bits[1]);
                    pico_gpio_control(scope1_S2, value2Bits[2]);
                    pico_gpio_control(scope1_S3, value2Bits[3]);
                    pico_gpio_control(scope1_S4, value2Bits[4]);
                    
                    pico_gpio_control(scope1_EN, 0);
                    break;
                    case 1:
                    pico_gpio_control(scope2_EN, 1);
                    
                    pico_gpio_control(scope2_S0, value2Bits[0]);
                    pico_gpio_control(scope2_S1, value2Bits[1]);
                    pico_gpio_control(scope2_S2, value2Bits[2]);
                    pico_gpio_control(scope2_S3, value2Bits[3]);
                    pico_gpio_control(scope2_S4,  value2Bits[4]);
                    
                    pico_gpio_control(scope2_EN, 0);
                    break;
                    case 2:
                    pico_gpio_control(wavegen2_EN, 1);
                    
                    pico_gpio_control(wavegen2_S0, value2Bits[0]);
                    pico_gpio_control(wavegen2_S1, value2Bits[1]);
                    pico_gpio_control(wavegen2_S2, value2Bits[2]);
                    pico_gpio_control(wavegen2_S3, value2Bits[3]);
                    pico_gpio_control(wavegen2_S4, value2Bits[4]);
        
                    pico_gpio_control(wavegen2_EN, 0);
                    break;
                default:
                    // pass
                    break;
            }
        }
        //printf("Invalid command: %u_%u\n", command.value1, command.value2);
        // Pass and dont update the GPIO
        return;
    }
    // Check for EN commmands
    //printf("%u_%u maps to %d\n", command.value1, command.value2, muxToPicoMap[command.value1][command.value2]);
    //fflush(stdout);
}

int main() {
    // Initialize all GPIO pins
    initialize_all_gpio();

    // Initialize UART for serial communication
    stdio_init_all();
    while (!stdio_usb_connected()) {
        blink(3, 250);
    }
            
    // Wait for the serial connection to be ready
    sleep_ms(2000); // Allow time for the host to connect

    while (true) {
        char command[16] = {0}; // Buffer to store the command
        int index = 0;

        // Read characters from serial until a newline or buffer is full
        while (true) {
            int c = getchar_timeout_us(100000); // Wait for 100ms for input
            if (c == PICO_ERROR_TIMEOUT) {
                continue; // No input, keep waiting
            }
            if (c == '\n' || c == '\r' || index >= sizeof(command) - 1) {
                break; // End of command
            }
            command[index++] = (char)c;
        }

        // Null-terminate the command string
        command[index] = '\0';

        // Parse the command and handle it
        ParsedCommand parsed = parse_command(command);
        handle_parsed_command(parsed);
    }
}

