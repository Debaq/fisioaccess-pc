/*
 * CONFIGURACIÓN DE EJEMPLO: ESPIRÓMETRO/RINOMANÓMETRO
 *
 * Este dispositivo incluye:
 * - Dos sensores MPS20N0040D con HX710B
 * - Comunicación Serial (115200 baud)
 *
 * HARDWARE:
 * - Sensor 1: DOUT=5, SCK=6
 * - Sensor 2: DOUT=7, SCK=4
 *
 * INSTRUCCIONES:
 * 1. Copiar este archivo a src/config.h
 * 2. Compilar y cargar en el ESP32
 */

#ifndef CONFIG_H
#define CONFIG_H

// ===== IDENTIFICACIÓN DEL DISPOSITIVO =====
#define ESP32_ID 0x0001  // ID único para espirómetro

// ===== MODO DE COMUNICACIÓN =====
#define COMM_MODE_SERIAL

// ===== CONFIGURACIÓN SERIAL =====
#ifdef COMM_MODE_SERIAL
  #define SERIAL_BAUD 115200
#endif

// ===== SENSORES ACTIVOS =====
#define USE_MPS20N0040D_DUAL

// ===== PINES - MPS20N0040D DUAL =====
#ifdef USE_MPS20N0040D_DUAL
  // Sensor 1
  #define MPS_DOUT_PIN_1 5
  #define MPS_SCK_PIN_1 6
  // Sensor 2
  #define MPS_DOUT_PIN_2 7
  #define MPS_SCK_PIN_2 4
  // Calibración
  #define MPS_COUNTS_TO_KPA 0.000028
  #define MPS_DIVISION_FACTOR 14.388
  #define MPS_CALIBRATION_SAMPLES 50
#endif

#endif
