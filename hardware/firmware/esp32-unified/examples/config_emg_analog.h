/*
 * CONFIGURACIÓN DE EJEMPLO: EMG ANALÓGICO DIRECTO
 *
 * Este dispositivo incluye:
 * - Señal EMG conectada directamente a pin analógico A3
 * - Comunicación Serial (115200 baud)
 * - Frecuencia de muestreo: 500 Hz
 *
 * HARDWARE:
 * - EMG: GPIO39 (A3)
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
#define ESP32_ID 0x0005  // ID único para EMG analógico

// ===== MODO DE COMUNICACIÓN =====
#define COMM_MODE_SERIAL

// ===== CONFIGURACIÓN SERIAL =====
#ifdef COMM_MODE_SERIAL
  #define SERIAL_BAUD 115200
#endif

// ===== SENSORES ACTIVOS =====
#define USE_EMG_ANALOG

// ===== PINES - EMG Analógico Directo =====
#ifdef USE_EMG_ANALOG
  #define EMG_ANALOG_PIN 39  // GPIO39 (A3 en ESP32)
  #define EMG_SAMPLE_RATE 500 // Hz
#endif

#endif
