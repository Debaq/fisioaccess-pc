/*
 * CONFIGURACIÓN DE EJEMPLO: ECG CON ADS1115
 *
 * Este dispositivo incluye:
 * - ADS1115 conectado en I2C
 * - Señal ECG en canal A0 del ADS1115
 * - Lead detection en pines D2 (LD+) y D3 (LD-)
 * - Comunicación Serial (115200 baud)
 *
 * HARDWARE:
 * - I2C: SDA=21, SCL=22
 * - ADS1115 dirección: 0x48
 * - LD+: D2 (GPIO 2)
 * - LD-: D3 (GPIO 3)
 *
 * INSTRUCCIONES:
 * 1. Copiar este archivo a src/config.h
 * 2. Compilar y cargar en el ESP32
 */

#ifndef CONFIG_H
#define CONFIG_H

// ===== IDENTIFICACIÓN DEL DISPOSITIVO =====
#define ESP32_ID 0x0002  // ID único para ECG

// ===== MODO DE COMUNICACIÓN =====
#define COMM_MODE_SERIAL

// ===== CONFIGURACIÓN SERIAL =====
#ifdef COMM_MODE_SERIAL
  #define SERIAL_BAUD 115200
#endif

// ===== SENSORES ACTIVOS =====
#define USE_ECG_ADS1115

// ===== PINES - ECG con ADS1115 =====
#ifdef USE_ECG_ADS1115
  #define ECG_ADS_SDA 21
  #define ECG_ADS_SCL 22
  #define ECG_ADS_ADDR 0x48
  #define ECG_ADS_GAIN GAIN_FOUR  // Ajustar según amplificación del circuito
  #define ECG_ADS_CHANNEL 0  // Canal A0
  #define ECG_LD_PLUS_PIN 2   // D2 - LD+
  #define ECG_LD_MINUS_PIN 3  // D3 - LD-
#endif

#endif
