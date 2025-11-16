#ifndef CONFIG_H
#define CONFIG_H

// ===== IDENTIFICACIÓN DEL DISPOSITIVO =====
#define ESP32_ID 0x0001  // Cambiar por dispositivo

// ===== MODO DE COMUNICACIÓN =====
// Descomentar SOLO UNO
//#define COMM_MODE_WIFI
#define COMM_MODE_SERIAL
//#define COMM_MODE_BLUETOOTH

// ===== CONFIGURACIÓN WiFi =====
#ifdef COMM_MODE_WIFI
  #define WIFI_SSID "TuSSID"
  #define WIFI_PASSWORD "TuPassword"
  #define SERVER_IP "192.168.1.100"
  #define SERVER_PORT 8888
#endif

// ===== CONFIGURACIÓN SERIAL =====
#ifdef COMM_MODE_SERIAL
  #define SERIAL_BAUD 115200
#endif

// ===== CONFIGURACIÓN BLUETOOTH =====
#ifdef COMM_MODE_BLUETOOTH
  #define BT_DEVICE_NAME "ESP32_SENSOR"
#endif

// ===== SENSORES ACTIVOS =====
// Descomentar los sensores que uses
//#define USE_MPS20N0040D_DUAL    // Espirometro/Rinomanometro con 2 sensores
//#define USE_ECG_ADS1115         // ECG con ADS1115
//#define USE_ECG_ANALOG          // ECG directo a pin analógico
//#define USE_EMG_ADS1115         // EMG con ADS1115
//#define USE_EMG_ANALOG          // EMG directo a pin analógico

// ===== PINES - MPS20N0040D DUAL =====
#ifdef USE_MPS20N0040D_DUAL
  // Sensor 1
  #define MPS_DOUT_PIN_1 5
  #define MPS_SCK_PIN_1 6
  // Sensor 2
  #define MPS_DOUT_PIN_2 7
  #define MPS_SCK_PIN_2 4
#endif

// ===== PINES - ECG con ADS1115 =====
#ifdef USE_ECG_ADS1115
  #define ECG_ADS_SDA 21
  #define ECG_ADS_SCL 22
  #define ECG_ADS_ADDR 0x48
  #define ECG_ADS_GAIN GAIN_FOUR  // Ajustar según amplificación
  // Pin analógico A0 del ADS1115
  #define ECG_ADS_CHANNEL 0
  // Pines digitales para leads detection
  #define ECG_LD_PLUS_PIN 2   // D2 - LD+
  #define ECG_LD_MINUS_PIN 3  // D3 - LD-
#endif

// ===== PINES - ECG Analógico Directo =====
#ifdef USE_ECG_ANALOG
  #define ECG_ANALOG_PIN 36  // GPIO36 (A0 en ESP32)
  #define ECG_LD_PLUS_PIN 2   // D2 - LD+
  #define ECG_LD_MINUS_PIN 3  // D3 - LD-
  #define ECG_SAMPLE_RATE 500 // Hz
#endif

// ===== PINES - EMG con ADS1115 =====
#ifdef USE_EMG_ADS1115
  #define EMG_ADS_SDA 21
  #define EMG_ADS_SCL 22
  #define EMG_ADS_ADDR 0x48
  #define EMG_ADS_GAIN GAIN_FOUR
  #define EMG_ADS_CHANNEL 0
#endif

// ===== PINES - EMG Analógico Directo =====
#ifdef USE_EMG_ANALOG
  #define EMG_ANALOG_PIN 39  // GPIO39 (A3 en ESP32)
  #define EMG_SAMPLE_RATE 500 // Hz
#endif

#endif
