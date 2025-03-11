#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "memory_map.h"
#include "optical.h"
#include "scm3c_hw_interface.h"
#include "gpio.h"
#include "rftimer.h"

typedef struct {
	uint8_t count;
} app_vars_t;

app_vars_t app_vars;

// Number of for loop cycles between Hello World messages.
// 700000 for loop cycles roughly correspond to 1 second.
#define NUM_CYCLES_BETWEEN_TX 1000000

#define TRIGGER_PIN	0

void rftimer_callback(void);

// TX counter.
static uint32_t g_tx_counter = 0;

int main(void) {
	memset(&app_vars, 0, sizeof(app_vars_t));
	initialize_mote();
	crc_check();
	perform_calibration();

	delay_milliseconds_synchronous(500, 1);
	//Disable all in
 	GPI_control(0, 0, 0, 0);
	//Enable all out
 	GPO_control(6, 6, 6,6);
  	GPI_enables(0x0000);

	// Set GPO enables
	GPO_enables(0xFFFF);

	//Wrtie changes to scan chain
	analog_scan_chain_write();
  analog_scan_chain_load();
	// SCuM will pause
	delay_milliseconds_synchronous(500, 1);

	// SCuM will pulse the trigger pin to signal upcoming test
	gpio_set_high(TRIGGER_PIN);
	delay_milliseconds_synchronous(500, 1);
	gpio_set_low(TRIGGER_PIN);

	// SCuM will pause before test
	delay_milliseconds_synchronous(500, 1);



	//SCuM will drive all pins for testing




	gpio_1_set();
	gpio_2_set();
	gpio_3_set();
	gpio_4_set();
	gpio_5_set();
	gpio_6_set();
	gpio_7_set();
	gpio_8_set();
	gpio_9_set();
	gpio_10_set();
	gpio_11_set();
	gpio_12_set();
	gpio_13_set();
	gpio_14_set();
	gpio_15_set();
	delay_milliseconds_synchronous(1000, 1);
	gpio_1_clr();
	gpio_2_clr();
	gpio_3_clr();
	gpio_4_clr();
	gpio_5_clr();
	gpio_6_clr();
	gpio_7_clr();
	gpio_8_clr();
	gpio_9_clr();
	gpio_10_clr();
	gpio_11_clr();
	gpio_12_clr();
	gpio_13_clr();
	gpio_14_clr();
	gpio_15_clr();


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
