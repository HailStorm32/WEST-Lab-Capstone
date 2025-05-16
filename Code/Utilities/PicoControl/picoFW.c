// Description: This code initializes all GPIO pins on a Raspberry Pi Pico,
// controls GPIO pins based on parsed commands from a serial input,
#include "pico/stdlib.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

int scope1_EN_A = 3; // GPIO pin for Scope1 enable
int scope1_EN_B = 8; // GPIO pin for Scope1 enable
int scope1_S0 = 18; // GPIO pin for Scope1 S0
int scope1_S1 = 19; // GPIO pin for Scope1 S1
int scope1_S2 = 2; // GPIO pin for Scope1 S2
int scope1_S3 = 28; // GPIO pin for Scope1 S3

int scope2_EN_A = 6; // GPIO pin for Scope2 enable
int scope2_EN_B = 7; // GPIO pin for Scope1 enable
int scope2_S0 = 16; // GPIO pin for Scope2 S0
int scope2_S1 = 17; // GPIO pin for Scope2 S1
int scope2_S2 = 5; // GPIO pin for Scope2 S2
int scope2_S3 = 4; // GPIO pin for Scope2 S3

int Wavegen1_EN = 27; // GPIO pin for Wavegen1 enable
int Wavegen1_S0 = 21; // GPIO pin for Wavegen1 S0
int Wavegen1_S1 = 20; // GPIO pin for Wavegen1 S1
int Wavegen1_S2 = 26; // GPIO pin for Wavegen1 S2
int Wavegen1_S3 = 22; // GPIO pin for Wavegen1 S3

// Function to initialize all GPIO pins
void initialize_all_gpio(void) 
{
    for (uint gpio_num = 0; gpio_num <= 29; gpio_num++) 
    {
        gpio_init(gpio_num);
        gpio_set_dir(gpio_num, GPIO_OUT); // Set all GPIO pins as output
        gpio_put(gpio_num, false);       // Set all GPIO pins to low initially
    }
    // EN is active low to set high an init
    gpio_put(scope1_EN_A, 1);
    gpio_put(scope1_EN_B, 1);
    gpio_put(scope2_EN_A, 1);
    gpio_put(scope2_EN_B, 1);
    gpio_put(Wavegen1_EN, 1);
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
void blink(int count, int delay_ms) 
{
    for (int i = 0; i < count; i++) 
    {
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
ParsedCommand parse_command(const char *command) 
{
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
    // Scope1 (Index 0)
    {
        // Label 1-16 (Index 0-15) -> MUX IO (original value - 1) 
         1,  0,  4,  6,  8,  10,  12,  14,  2,  3, 5, 7, 9, 11, 13, 15,
        // Label 17-32 (Index 16-31) -> MUX IO (original value - 1)
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
    },
    // Scope2 (Index 1)
    {
        // Label 1-16 (Index 0-15) -> MUX IO (original value - 1) 
        1,  0,  4,  6,  8,  10,  12,  14,  2,  3, 5, 7, 9, 11, 13, 15,
        // Label 17-32 (Index 16-31) -> MUX IO (original value - 1)
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
    },
    // Wavegen1 (Index 2) - Values for Labels 17-32 were assumed previously
    {
        // Label 1-16 (Index 0-15) -> MUX IO (original value - 1) 
        1,  0,  4,  6,  8,  10,  12,  14,  2,  3, 5, 7, 9, 11, 13, 15,
        // Label 17-32 (Index 16-31) -> MUX IO (original value - 1)
        16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
    }
};

// Function to handle parsed commands
void handle_parsed_command(ParsedCommand command) 
{
    
    // Check if the command is valid
    if (((command.value1 >= 0) && (command.value1 <= 2)) && ((command.value2 >= 0) && (command.value2 <= 33))) 
    {
        if (command.value2 == 32) // Check for enable
        {
            //printf("Enable command: %u\n", command.value2);
            switch (command.value1) 
            { // Index to the mux
                case 0:
                    pico_gpio_control(scope1_EN_A, 1);
                    pico_gpio_control(scope1_EN_B, 1);

                    break;
                case 1:
                    pico_gpio_control(scope2_EN_A, 1);
                    pico_gpio_control(scope2_EN_B, 1);

                    break;
                case 2:
                    pico_gpio_control(Wavegen1_EN, 1);

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
                    pico_gpio_control(scope1_EN_A, 0);
                    pico_gpio_control(scope1_EN_B, 0);

                    break;
                case 1:
                    pico_gpio_control(scope2_EN_A, 0);
                    pico_gpio_control(scope2_EN_B, 0);

                    break;
                case 2:
                    pico_gpio_control(Wavegen1_EN, 0);

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
                    pico_gpio_control(scope1_EN_A, 1);
                    pico_gpio_control(scope1_EN_B, 1);
        
                    pico_gpio_control(scope1_S0, value2Bits[0]);
                    pico_gpio_control(scope1_S1, value2Bits[1]);
                    pico_gpio_control(scope1_S2, value2Bits[2]);
                    pico_gpio_control(scope1_S3, value2Bits[3]);
                    if(value2Bits[4])
                    {
                        pico_gpio_control(scope1_EN_B, 0);
                    }
                    else
                    {
                        pico_gpio_control(scope1_EN_A, 0);
                    }
                    
                    

                    break;
                case 1:
                    pico_gpio_control(scope2_EN_A, 1);
                    pico_gpio_control(scope2_EN_B, 1);
                    
                    pico_gpio_control(scope2_S0, value2Bits[0]);
                    pico_gpio_control(scope2_S1, value2Bits[1]);
                    pico_gpio_control(scope2_S2, value2Bits[2]);
                    pico_gpio_control(scope2_S3, value2Bits[3]);
                    if(value2Bits[4])
                    {
                        pico_gpio_control(scope2_EN_B, 0);
                    }
                    else
                    {
                        pico_gpio_control(scope2_EN_A, 0);
                    }
                    
    
                    break;
                case 2:
                    pico_gpio_control(Wavegen1_EN, 1);
                    
                    pico_gpio_control(Wavegen1_S0, value2Bits[0]);
                    pico_gpio_control(Wavegen1_S1, value2Bits[1]);
                    pico_gpio_control(Wavegen1_S2, value2Bits[2]);
                    pico_gpio_control(Wavegen1_S3, value2Bits[3]);
        
                    pico_gpio_control(Wavegen1_EN, 0);
                    break;
                default:
                    // pass
                    break;
            }
        }
    }
}

int main() 
{
    // Initialize all GPIO pins
    initialize_all_gpio();

    // Initialize UART for serial communication
    stdio_init_all();
    while (!stdio_usb_connected()) 
    {
        blink(3, 250);
    }
            
    // Wait for the serial connection to be ready
    sleep_ms(2000); // Allow time for the host to connect

    while (true) {
        char command[16] = {0}; // Buffer to store the command
        int index = 0;

        // Read characters from serial until a newline or buffer is full
        while (true) 
        {
            int c = getchar_timeout_us(100000); // Wait for 100ms for input
            if (c == PICO_ERROR_TIMEOUT) 
            {
                continue; // No input, keep waiting
            }
            if (c == '\n' || c == '\r' || index >= sizeof(command) - 1) 
            {
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

