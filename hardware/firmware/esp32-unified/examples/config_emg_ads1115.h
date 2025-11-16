/*
 * CONFIGURACIÓN DE EJEMPLO: EMG CON ADS1115
 *
 * Este dispositivo incluye:
 * - ADS1115 conectado en I2C
 * - Señal EMG en canal A0 del ADS1115
 * - Comunicación Serial (115200 baud)
 *
 * HARDWARE:
 * - I2C: SDA=21, SCL=22
 * - ADS1115 dirección: 0x48
 *
 * INSTRUCCIONES:
 * 1. Copiar este archivo a src/config.h
 * 2. Compilar y cargar en el ESP32
 */

#ifndef CONFIG_H
#define CONFIG_H

// ===== IDENTIFICACIÓN DEL DISPOSITIVO =====
#define ESP32_ID 0x0004  // ID único para EMG

// ===== MODO DE COMUNICACIÓN =====
#define COMM_MODE_SERIAL

// ===== CONFIGURACIÓN SERIAL =====
#ifdef COMM_MODE_SERIAL
  #define SERIAL_BAUD 115200
#endif

// ===== SENSORES ACTIVOS =====
#define USE_EMG_ADS1115

// ===== PINES - EMG con ADS1115 =====
#ifdef USE_EMG_ADS1115
  #define EMG_ADS_SDA 21
  #define EMG_ADS_SCL 22
  #define EMG_ADS_ADDR 0x48
  #define EMG_ADS_GAIN GAIN_FOUR
  #define EMG_ADS_CHANNEL 0  // Canal A0
#endif

#endif
