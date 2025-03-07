#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "memory_map.h"
#include "optical.h"
#include "scm3c_hw_interface.h"
#include "gpio.h"
#include "rftimer.h"



// Number of for loop cycles between Hello World messages.
// 700000 for loop cycles roughly correspond to 1 second.
#define NUM_CYCLES_BETWEEN_TX 1000000

#define TRIGGER_PIN	0

void rftimer_callback(void);

// TX counter.
static uint32_t g_tx_counter = 0;

int main(void) {
    initialize_mote();
    crc_check();
    perform_calibration();
	
	
	// SCuM will pause
	delay_milliseconds_synchronous(500, 1);
	
	// SCuM will pulse the trigger pin to signal upcoming test
	gpio_set_high(TRIGGER_PIN);
	delay_milliseconds_synchronous(500, 1);
	gpio_set_low(TRIGGER_PIN);
	
	// SCuM will pause before test
	delay_milliseconds_synchronous(500, 1);
	
	//SCuM will drive all pins for testing
	GPIO_REG__OUTPUT = 0xFFFF;
	delay_milliseconds_synchronous(1000, 1);
	GPIO_REG__OUTPUT = ~0xFFFF;
	
	// SCuM will pause before test
	delay_milliseconds_synchronous(500, 1);
	
	gpio_set_high(TRIGGER_PIN);
	delay_milliseconds_synchronous(500, 1);
	gpio_set_low(TRIGGER_PIN);
	

    while (true) {
        printf("Hello World! %u\n", g_tx_counter);
        ++g_tx_counter;

        for (size_t i = 0; i < NUM_CYCLES_BETWEEN_TX; ++i);
    }
}

void rftimer_callback(void) { }