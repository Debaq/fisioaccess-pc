/*
 * CONFIGURACIÓN DE EJEMPLO: ECG ANALÓGICO DIRECTO
 *
 * Este dispositivo incluye:
 * - Señal ECG conectada directamente a pin analógico A0
 * - Lead detection en pines D2 (LD+) y D3 (LD-)
 * - Comunicación Serial (115200 baud)
 * - Frecuencia de muestreo: 500 Hz
 *
 * HARDWARE:
 * - ECG: GPIO36 (A0)
 * - LD+: D2 (GPIO 2)
 * - LD-: D3 (GPIO 3)
 *
 * INSTRUCCIONES:
 * 1. Copiar este archivo a src/config.h
 * 2. Compilar y cargar en el ESP32
 *
 * NOTA: Este modo requiere un circuito de acondicionamiento de señal
 * que limite el voltaje entre 0-3.3V
 */

#ifndef CONFIG_H
#define CONFIG_H

// ===== IDENTIFICACIÓN DEL DISPOSITIVO =====
#define ESP32_ID 0x0003  // ID único para ECG analógico

// ===== MODO DE COMUNICACIÓN =====
#define COMM_MODE_SERIAL

// ===== CONFIGURACIÓN SERIAL =====
#ifdef COMM_MODE_SERIAL
  #define SERIAL_BAUD 115200
#endif

// ===== SENSORES ACTIVOS =====
#define USE_ECG_ANALOG

// ===== PINES - ECG Analógico Directo =====
#ifdef USE_ECG_ANALOG
  #define ECG_ANALOG_PIN 36  // GPIO36 (A0 en ESP32)
  #define ECG_LD_PLUS_PIN 2   // D2 - LD+
  #define ECG_LD_MINUS_PIN 3  // D3 - LD-
  #define ECG_SAMPLE_RATE 500 // Hz
#endif

#endif
