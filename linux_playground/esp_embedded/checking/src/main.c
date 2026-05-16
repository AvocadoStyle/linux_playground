#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_http_server.h"
#include "nvs_flash.h"
#include "string.h"

#define BLINK_GPIO GPIO_NUM_2
#define WIFI_SSID "SE-WiFi-Guests" // Change to your WiFi SSID
#define WIFI_PASS "solaredge2017"

static const char *TAG = "led_server";

/* ── WiFi ────────────────────────────────────────────────── */
static void wifi_event_handler(void *arg, esp_event_base_t base,
                               int32_t id, void *data)
{
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START)
    {
        ESP_LOGI(TAG, "Connecting to WiFi SSID: %s ...", WIFI_SSID);
        esp_wifi_connect();
    }
    else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED)
    {
        wifi_event_sta_disconnected_t *event = (wifi_event_sta_disconnected_t *)data;
        ESP_LOGE(TAG, "Disconnected! Reason: %d", event->reason);
        // reason 201 = wrong password, 2 = SSID not found
        if (event->reason == WIFI_REASON_AUTH_FAIL)
            ESP_LOGE(TAG, "Wrong password!");
        else if (event->reason == WIFI_REASON_NO_AP_FOUND)
            ESP_LOGE(TAG, "SSID not found! Check network name and make sure it's 2.4GHz.");
        else
            ESP_LOGI(TAG, "Retrying connection...");
        esp_wifi_connect();
    }
    else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP)
    {
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)data;
        ESP_LOGI(TAG, "Connected! IP: " IPSTR, IP2STR(&event->ip_info.ip));
    }
}

static void wifi_init(void)
{
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_create_default_wifi_sta();

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);

    esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, wifi_event_handler, NULL);
    esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, wifi_event_handler, NULL);

    wifi_config_t wifi_cfg = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASS,
        },
    };
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_set_config(WIFI_IF_STA, &wifi_cfg);
    esp_wifi_start();
}

/* ── HTTP handlers ───────────────────────────────────────── */
static esp_err_t led_on_handler(httpd_req_t *req)
{
    gpio_set_level(BLINK_GPIO, 1);
    httpd_resp_sendstr(req, "LED ON");
    return ESP_OK;
}

static esp_err_t led_off_handler(httpd_req_t *req)
{
    gpio_set_level(BLINK_GPIO, 0);
    httpd_resp_sendstr(req, "LED OFF");
    return ESP_OK;
}

static esp_err_t led_toggle_handler(httpd_req_t *req)
{
    static int state = 0;
    state = !state;
    gpio_set_level(BLINK_GPIO, state);
    httpd_resp_sendstr(req, state ? "LED ON" : "LED OFF");
    return ESP_OK;
}

static esp_err_t index_handler(httpd_req_t *req)
{
    const char *html =
        "<h1>ESP32 LED Control</h1>"
        "<a href='/led/on'><button>ON</button></a>  "
        "<a href='/led/off'><button>OFF</button></a>  "
        "<a href='/led/toggle'><button>TOGGLE</button></a>";
    httpd_resp_set_type(req, "text/html");
    httpd_resp_sendstr(req, html);
    return ESP_OK;
}

static void start_http_server(void)
{
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    httpd_handle_t server = NULL;
    httpd_start(&server, &config);

    httpd_uri_t routes[] = {
        {.uri = "/", .method = HTTP_GET, .handler = index_handler},
        {.uri = "/led/on", .method = HTTP_GET, .handler = led_on_handler},
        {.uri = "/led/off", .method = HTTP_GET, .handler = led_off_handler},
        {.uri = "/led/toggle", .method = HTTP_GET, .handler = led_toggle_handler},
    };

    for (int i = 0; i < sizeof(routes) / sizeof(routes[0]); i++)
        httpd_register_uri_handler(server, &routes[i]);

    ESP_LOGI(TAG, "HTTP server started");
}

/* ── Entry point ─────────────────────────────────────────── */
void app_main(void)
{
    nvs_flash_init();

    gpio_reset_pin(BLINK_GPIO);
    gpio_set_direction(BLINK_GPIO, GPIO_MODE_OUTPUT);

    wifi_init();

    // Wait for IP before starting server
    vTaskDelay(pdMS_TO_TICKS(5000));

    start_http_server();
}
