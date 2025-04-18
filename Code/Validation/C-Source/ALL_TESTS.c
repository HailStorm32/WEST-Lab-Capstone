#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "memory_map.h"
#include "optical.h"
#include "scm3c_hw_interface.h"
#include "gpio.h"
#include "rftimer.h"


#include "radio.h"

#define TX_PACKET_LEN 8 + 2  // 2 for CRC

void RF_RX_SWEEP_TEST(void);
void DD_GPIO_TEST(void);
void AD_CLOCK_TEST(void);
void trig_pulse(void);

//=========================== prototypes ======================================
void fill_tx_packet(uint8_t* packet, uint8_t packet_len,
                    repeat_rx_tx_state_t state);

typedef struct {
    uint8_t count;
		uint8_t dummy;
    uint8_t index;
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
// SCuM's normal init routine	--------------------------------------------
	memset(&app_vars, 0, sizeof(app_vars_t));
    initialize_mote();
    crc_check();
    perform_calibration();
//------------------------------------------------------------------------


// SCuM TX Sweep test---------------------------------------------------
	RF_RX_SWEEP_TEST();
//----------------------------------------------------------------------
		
	
// Set all GPIO to cortexGPIO, disable all inputs, enable all outputs-----	
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
//----------------------------------------------------------------------


// SCuM Clock test------------------------------------------------------	
  //SCuM will mux set pins 0 - 7 to bank 10. 
	AD_CLOCK_TEST();
//----------------------------------------------------------------------


//SCuM will Set all pins GPIO testing------------------------------------	
	DD_GPIO_TEST();
//-----------------------------------------------------------------------

		
	while (true) 
	{
		printf("Hello World! %u\n", g_tx_counter);
		++g_tx_counter;

		for (size_t i = 0; i < NUM_CYCLES_BETWEEN_TX; ++i);
	}	
}

void rftimer_callback(void) { }

void trig_pulse(void)
{
		// SCuM will pause
	delay_milliseconds_synchronous(500, 1);
	
	// SCuM will pulse the trigger pin to signal upcoming test
	gpio_set_high(TRIGGER_PIN);
	delay_milliseconds_synchronous(500, 1);
	gpio_set_low(TRIGGER_PIN);
	
	// SCuM will pause before test
	delay_milliseconds_synchronous(500, 1);
}

void DD_GPIO_TEST(void)
{

	trig_pulse();
	
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
}

void RF_RX_SWEEP_TEST(void)
{
    trig_pulse();
	
	  repeat_rx_tx_params_t repeat_params;

    memset(&app_vars, 0, sizeof(app_vars_t));

    initialize_mote();
    crc_check();
    perform_calibration();

    repeat_params.packet_count = 4805; // 31 * 31 * 5
    repeat_params.pkt_len = TX_PACKET_LEN;
    repeat_params.radio_mode = TX_MODE;
    repeat_params.repeat_mode = SWEEP;
    repeat_params.fill_tx_packet = fill_tx_packet;
    repeat_params.sweep_lc_coarse_start = 20;
    repeat_params.sweep_lc_coarse_end = 25;
    repeat_params.sweep_lc_mid_start = 0;
    repeat_params.sweep_lc_mid_end = 31;
    repeat_params.sweep_lc_fine_start = 0;
    repeat_params.sweep_lc_fine_end = 31;
    repeat_params.fixed_lc_coarse = 22;
    repeat_params.fixed_lc_mid = 30;
    repeat_params.fixed_lc_fine = 22;

    repeat_rx_tx(repeat_params);
}

void AD_CLOCK_TEST(void)
{
// Set up GPIO banks--------------------------------------------	
	//Disable all in
	GPI_control(0, 0, 0, 0); 
	//Enable all out
	GPO_control(10, 10, 6,6); 
		
	GPI_enables(0x0000);

    // Set GPO enables
  GPO_enables(0xFFFF);
	
	// Enable LF_CLOCK
  clear_asc_bit(553);
	
	//Wrtie changes to scan chain
	analog_scan_chain_write();
  analog_scan_chain_load();
//-------------------------------------------------------------

	
	trig_pulse();
	delay_milliseconds_synchronous(500, 1);// Delay here to allow device to perform test

// Re-config GPIO to default-----------------------------------
	//Disable all in
	GPI_control(0, 0, 0, 0); 
	//Enable all out
	GPO_control(6, 6, 6,6); 
		
	GPI_enables(0x0000);

    // Set GPO enables
  GPO_enables(0xFFFF);
	
	// Disable LF_CLOCK
  set_asc_bit(553);
	
	//Wrtie changes to scan chain
	analog_scan_chain_write();
  analog_scan_chain_load();
//----------------------------------------------------------------	
}


//=========================== private ========================================= Copied from freq_sweep_tx_simple.c
void fill_tx_packet(uint8_t* packet, uint8_t packet_len,
                    repeat_rx_tx_state_t state) {
    sprintf(packet, "%d %d %d", state.cfg_coarse, state.cfg_mid,
            state.cfg_fine);
}