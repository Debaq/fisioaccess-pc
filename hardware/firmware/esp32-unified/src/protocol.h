#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <Arduino.h>

// ===== CONSTANTES DEL PROTOCOLO =====
#define SYNC_BYTE_1 0xFF
#define SYNC_BYTE_2 0xAA
#define MAX_DATOS_PER_MSG 32

// ===== IDs DE SENSORES =====
// Ambientales
#define ID_TEMPERATURA 0x01
#define ID_HUMEDAD 0x02
#define ID_PRESION_BAR 0x03

// ECG - Electrocardiograma (0x10-0x1F)
#define ID_ECG_CH1 0x10         // ECG Canal 1 (RAW ADC)
#define ID_ECG_CH2 0x11         // ECG Canal 2 (RAW ADC)
#define ID_ECG_CH3 0x12         // ECG Canal 3 (RAW ADC)
#define ID_ECG_CH4 0x13         // ECG Canal 4 (RAW ADC)
#define ID_HEART_RATE 0x14      // Frecuencia cardíaca calculada (BPM) - Procesado en Python
#define ID_SPO2 0x15            // SpO2 (%) - Procesado en Python
#define ID_ECG_LD_PLUS 0x16     // Estado del lead detection positivo (0/1)
#define ID_ECG_LD_MINUS 0x17    // Estado del lead detection negativo (0/1)

// EMG - Electromiograma (0x18-0x1F)
#define ID_EMG_CH1 0x18         // EMG Canal 1 (RAW ADC)
#define ID_EMG_CH2 0x19         // EMG Canal 2 (RAW ADC)
#define ID_EMG_CH3 0x1A         // EMG Canal 3 (RAW ADC)
#define ID_EMG_CH4 0x1B         // EMG Canal 4 (RAW ADC)

// ADC Genérico
#define ID_ADC_CH0 0x20
#define ID_ADC_CH1 0x21
#define ID_ADC_CH2 0x22
#define ID_ADC_CH3 0x23

// Presión/Fuerza (0x30-0x3F)
#define ID_PRESION_AIRE 0x30
#define ID_CELULA_CARGA 0x31
#define ID_FUERZA 0x32
#define ID_PRESION_1 0x33      // Sensor 1 RAW ADC (HX710B 24-bit) - Espirometría
#define ID_PRESION_2 0x34      // Sensor 2 RAW ADC (HX710B 24-bit) - Rinomanometría
// IDs 0x35-0x38 reservados para datos procesados en Python (flujo, volumen, etc.)

// EEG TGAM
#define ID_TGAM_QUALITY 0x40
#define ID_TGAM_ATTENTION 0x41
#define ID_TGAM_MEDITATION 0x42
#define ID_TGAM_DELTA 0x43
#define ID_TGAM_THETA 0x44
#define ID_TGAM_LOW_ALPHA 0x45
#define ID_TGAM_HIGH_ALPHA 0x46
#define ID_TGAM_LOW_BETA 0x47
#define ID_TGAM_HIGH_BETA 0x48
#define ID_TGAM_LOW_GAMMA 0x49
#define ID_TGAM_HIGH_GAMMA 0x4A

// EEG Raw
#define ID_EEG_RAW_CH1 0x50
#define ID_EEG_RAW_CH2 0x51
#define ID_EEG_RAW_CH3 0x52
#define ID_EEG_RAW_CH4 0x53

// IMU Raw
#define ID_ACCEL_X 0x60
#define ID_ACCEL_Y 0x61
#define ID_ACCEL_Z 0x62
#define ID_GYRO_X 0x63
#define ID_GYRO_Y 0x64
#define ID_GYRO_Z 0x65
#define ID_MAG_X 0x66
#define ID_MAG_Y 0x67
#define ID_MAG_Z 0x68

// IMU Procesado
#define ID_ROLL 0x70
#define ID_PITCH 0x71
#define ID_YAW 0x72
#define ID_QUAT_W 0x73
#define ID_QUAT_X 0x74
#define ID_QUAT_Y 0x75
#define ID_QUAT_Z 0x76

// ===== ESTRUCTURA DE DATOS =====
struct SensorData {
  uint8_t id;
  float value;
};

// ===== FUNCIONES =====
void initProtocol();
void addData(uint8_t sensorId, float value);
void sendBuffer();
void clearBuffer();
uint16_t calculateCRC16(uint8_t* data, size_t length);

// Declaración de funciones de comunicación (implementadas según modo)
void sendSerial(uint8_t* data, size_t length);
void sendWiFi(uint8_t* data, size_t length);
void sendBluetooth(uint8_t* data, size_t length);

#endif
