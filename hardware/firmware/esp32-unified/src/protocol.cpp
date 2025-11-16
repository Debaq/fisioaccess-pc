#include "protocol.h"
#include "config.h"

// Buffer de datos
SensorData dataBuffer[MAX_DATOS_PER_MSG];
uint8_t dataCount = 0;

// Buffer de mensaje final
uint8_t messageBuffer[256];

void initProtocol() {
  clearBuffer();
}

void addData(uint8_t sensorId, float value) {
  if (dataCount < MAX_DATOS_PER_MSG) {
    dataBuffer[dataCount].id = sensorId;
    dataBuffer[dataCount].value = value;
    dataCount++;
  }
}

uint16_t calculateCRC16(uint8_t* data, size_t length) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < length; i++) {
    crc ^= data[i];
    for (uint8_t j = 0; j < 8; j++) {
      if (crc & 0x0001) {
        crc = (crc >> 1) ^ 0x8408;
      } else {
        crc >>= 1;
      }
    }
  }
  return crc;
}

void sendBuffer() {
  if (dataCount == 0) return;

  uint16_t idx = 0;

  // SYNC
  messageBuffer[idx++] = SYNC_BYTE_1;
  messageBuffer[idx++] = SYNC_BYTE_2;

  // ID_ESP32 (little-endian)
  messageBuffer[idx++] = ESP32_ID & 0xFF;
  messageBuffer[idx++] = (ESP32_ID >> 8) & 0xFF;

  // TIMESTAMP (little-endian)
  uint32_t timestamp = millis();
  messageBuffer[idx++] = timestamp & 0xFF;
  messageBuffer[idx++] = (timestamp >> 8) & 0xFF;
  messageBuffer[idx++] = (timestamp >> 16) & 0xFF;
  messageBuffer[idx++] = (timestamp >> 24) & 0xFF;

  // N_DATOS
  messageBuffer[idx++] = dataCount;

  // DATOS
  for (uint8_t i = 0; i < dataCount; i++) {
    messageBuffer[idx++] = dataBuffer[i].id;

    // Float en little-endian
    uint8_t* floatBytes = (uint8_t*)&dataBuffer[i].value;
    messageBuffer[idx++] = floatBytes[0];
    messageBuffer[idx++] = floatBytes[1];
    messageBuffer[idx++] = floatBytes[2];
    messageBuffer[idx++] = floatBytes[3];
  }

  // CRC16 (calculado desde ID_ESP32 hasta fin de DATOS)
  uint16_t crc = calculateCRC16(&messageBuffer[2], idx - 2);
  messageBuffer[idx++] = crc & 0xFF;
  messageBuffer[idx++] = (crc >> 8) & 0xFF;

  // Enviar según modo de comunicación
  #ifdef COMM_MODE_WIFI
    sendWiFi(messageBuffer, idx);
  #elif defined(COMM_MODE_SERIAL)
    sendSerial(messageBuffer, idx);
  #elif defined(COMM_MODE_BLUETOOTH)
    sendBluetooth(messageBuffer, idx);
  #endif

  clearBuffer();
}

void clearBuffer() {
  dataCount = 0;
}
