#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define BLINK_GPIO 2

void app_main(void)
{
    // Reset the GPIO pin configuration to default
    gpio_reset_pin(BLINK_GPIO);

    // Set the GPIO as output
    gpio_set_direction(BLINK_GPIO, GPIO_MODE_OUTPUT);

    while (1) {
        gpio_set_level(BLINK_GPIO, 1);   // LED ON
        vTaskDelay(500 / portTICK_PERIOD_MS);

        gpio_set_level(BLINK_GPIO, 0);   // LED OFF
        vTaskDelay(500 / portTICK_PERIOD_MS);
    }
}