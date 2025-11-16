# Firmware ESP32 Unificado - Sistema de Sensores

## 1. Protocolo de Comunicación Binario

### 1.1 Estructura del Mensaje

```
[SYNC_1][SYNC_2][ID_ESP32][TIMESTAMP][N_DATOS][DATOS...][CRC16]
  1B      1B       2B        4B         1B      variable   2B
```

**Total Header:** 10 bytes  
**Por dato:** 5 bytes (1B ID + 4B valor)  
**Footer:** 2 bytes CRC16

### 1.2 Especificaciones Técnicas

| Campo | Tipo | Bytes | Descripción |
|-------|------|-------|-------------|
| SYNC_1 | uint8_t | 1 | Byte sincronización: `0xFF` |
| SYNC_2 | uint8_t | 1 | Byte sincronización: `0xAA` |
| ID_ESP32 | uint16_t | 2 | ID único del dispositivo (0x0001-0xFFFF) |
| TIMESTAMP | uint32_t | 4 | Milisegundos desde boot |
| N_DATOS | uint8_t | 1 | Cantidad de lecturas (1-255) |
| ID_DATO | uint8_t | 1 | Tipo de sensor/lectura |
| VALOR | float | 4 | Valor RAW del sensor |
| CRC16 | uint16_t | 2 | CRC-16-CCITT |

**Endianness:** Little-endian (nativo ESP32)  
**CRC:** Calculado sobre todo excepto SYNC y CRC mismo

### 1.3 Ejemplo de Mensaje

```
Mensaje con 3 lecturas:
FF AA 01 00 2C 4E 1A 00 03 10 00 00 C8 42 11 CD CC 4C 3E 01 00 00 48 42 A3 5F

Desglose:
- FF AA          : SYNC
- 01 00          : ESP32 ID = 0x0001
- 2C 4E 1A 00    : Timestamp = 1724972 ms
- 03             : 3 datos
- 10             : ID_DATO = ECG Canal 1
- 00 00 C8 42    : VALOR = 100.0
- 11             : ID_DATO = ECG Canal 2
- CD CC 4C 3E    : VALOR = 0.2
- 01             : ID_DATO = Temperatura
- 00 00 48 42    : VALOR = 50.0
- A3 5F          : CRC16
```

---

## 2. Tabla de IDs de Sensores

### 2.1 Sensores Ambientales (0x01-0x0F)

| ID | Descripción |
|----|-------------|
| 0x01 | Temperatura (°C) |
| 0x02 | Humedad (%RH) |
| 0x03 | Presión barométrica (Pa/kPa) |

### 2.2 ECG - Electrocardiograma (0x10-0x1F)

| ID | Descripción |
|----|-------------|
| 0x10 | ECG Canal 1 (raw) |
| 0x11 | ECG Canal 2 (raw) |
| 0x12 | ECG Canal 3 (raw) |
| 0x13 | ECG Canal 4 (raw) |
| 0x14 | Frecuencia cardíaca calculada (BPM) |
| 0x15 | SpO2 (%) |

### 2.3 ADC Genérico (0x20-0x2F)

| ID | Descripción |
|----|-------------|
| 0x20 | ADC Canal 0 (cuando NO es ECG) |
| 0x21 | ADC Canal 1 (genérico) |
| 0x22 | ADC Canal 2 (genérico) |
| 0x23 | ADC Canal 3 (genérico) |

### 2.4 Presión/Fuerza (0x30-0x3F)

| ID | Descripción |
|----|-------------|
| 0x30 | Presión aire (Pa, kPa, etc) |
| 0x31 | Célula de carga (kg, N) |
| 0x32 | Fuerza/Peso genérico |

### 2.5 EEG Procesado - TGAM (0x40-0x4F)

| ID | Descripción |
|----|-------------|
| 0x40 | TGAM Señal calidad (0-200) |
| 0x41 | TGAM Atención (0-100) |
| 0x42 | TGAM Meditación (0-100) |
| 0x43 | TGAM Delta |
| 0x44 | TGAM Theta |
| 0x45 | TGAM Low Alpha |
| 0x46 | TGAM High Alpha |
| 0x47 | TGAM Low Beta |
| 0x48 | TGAM High Beta |
| 0x49 | TGAM Low Gamma |
| 0x4A | TGAM High Gamma |

### 2.6 EEG Raw (0x50-0x5F)

| ID | Descripción |
|----|-------------|
| 0x50 | EEG raw Canal 1 |
| 0x51 | EEG raw Canal 2 |
| 0x52 | EEG raw Canal 3 |
| 0x53 | EEG raw Canal 4 |

### 2.7 IMU - Datos Raw (0x60-0x6F)

| ID | Descripción |
|----|-------------|
| 0x60 | Acelerómetro X (m/s² o g) |
| 0x61 | Acelerómetro Y |
| 0x62 | Acelerómetro Z |
| 0x63 | Giroscopio X (°/s o rad/s) |
| 0x64 | Giroscopio Y |
| 0x65 | Giroscopio Z |
| 0x66 | Magnetómetro X (μT) |
| 0x67 | Magnetómetro Y |
| 0x68 | Magnetómetro Z |

### 2.8 IMU - Datos Procesados (0x70-0x7F)

| ID | Descripción |
|----|-------------|
| 0x70 | Roll (grados) |
| 0x71 | Pitch (grados) |
| 0x72 | Yaw (grados) |
| 0x73 | Quaternion W |
| 0x74 | Quaternion X |
| 0x75 | Quaternion Y |
| 0x76 | Quaternion Z |

### 2.9 Reservado (0x80-0xFF)

Usuario/futuro - Expansión libre

---

## 3. Arquitectura del Firmware

### 3.1 Estructura de Archivos

```
esp32-sensor-firmware/
├── src/
│   ├── main.cpp                 # Loop principal
│   ├── config.h                 # Configuración del dispositivo
│   ├── protocol.h               # Definiciones del protocolo
│   ├── protocol.cpp             # Funciones de protocolo
│   ├── communication/
│   │   ├── wifi_comm.h
│   │   ├── wifi_comm.cpp
│   │   ├── serial_comm.h
│   │   ├── serial_comm.cpp
│   │   ├── bt_comm.h
│   │   └── bt_comm.cpp
│   └── sensors/
│       ├── sensor_base.h        # Clase base abstracta
│       ├── temp_sensor.h/.cpp   # Temperatura
│       ├── ecg_sensor.h/.cpp    # ECG
│       ├── ads1115.h/.cpp       # ADS1115
│       ├── hx710b.h/.cpp        # HX710B/HX711
│       ├── tgam.h/.cpp          # TGAM EEG
│       ├── imu_sensor.h/.cpp    # IMU genérico
│       └── ...                  # Otros sensores
├── platformio.ini
└── README.md
```

### 3.2 Configuración del Dispositivo

**Archivo: `config.h`**

```cpp
#ifndef CONFIG_H
#define CONFIG_H

// ===== IDENTIFICACIÓN DEL DISPOSITIVO =====
#define ESP32_ID 0x0001  // Cambiar por dispositivo

// ===== MODO DE COMUNICACIÓN =====
// Descomentar SOLO UNO
#define COMM_MODE_WIFI
//#define COMM_MODE_SERIAL
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
#define USE_TEMP_DHT22
#define USE_ECG_ADS1115
#define USE_HX710B
//#define USE_TGAM
//#define USE_IMU_MPU6050

// ===== PINES - TEMPERATURA =====
#ifdef USE_TEMP_DHT22
  #define DHT_PIN 4
  #define DHT_TYPE DHT22
#endif

// ===== PINES - ECG con ADS1115 =====
#ifdef USE_ECG_ADS1115
  #define ADS_SDA 21
  #define ADS_SCL 22
  #define ADS_ADDR 0x48
  // Canales activos (true/false)
  #define ADS_CH0_ACTIVE true   // ECG Canal 1
  #define ADS_CH1_ACTIVE true   // ECG Canal 2
  #define ADS_CH2_ACTIVE false
  #define ADS_CH3_ACTIVE false
#endif

// ===== PINES - HX710B =====
#ifdef USE_HX710B
  #define HX710B_DOUT 19
  #define HX710B_SCK 18
  #define HX710B_MODE_PRESSURE  // o HX710B_MODE_LOADCELL
#endif

// ===== PINES - TGAM =====
#ifdef USE_TGAM
  #define TGAM_RX 16
  #define TGAM_TX 17
#endif

// ===== PINES - IMU =====
#ifdef USE_IMU_MPU6050
  #define IMU_SDA 21
  #define IMU_SCL 22
  #define IMU_USE_DMP true  // Si tiene procesamiento integrado
#endif

#endif
```

### 3.3 Definiciones del Protocolo

**Archivo: `protocol.h`**

```cpp
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

// ECG
#define ID_ECG_CH1 0x10
#define ID_ECG_CH2 0x11
#define ID_ECG_CH3 0x12
#define ID_ECG_CH4 0x13
#define ID_HEART_RATE 0x14
#define ID_SPO2 0x15

// ADC Genérico
#define ID_ADC_CH0 0x20
#define ID_ADC_CH1 0x21
#define ID_ADC_CH2 0x22
#define ID_ADC_CH3 0x23

// Presión/Fuerza
#define ID_PRESION_AIRE 0x30
#define ID_CELULA_CARGA 0x31
#define ID_FUERZA 0x32

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

#endif
```

### 3.4 Implementación del Protocolo

**Archivo: `protocol.cpp`**

```cpp
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
```

### 3.5 Clase Base de Sensores

**Archivo: `sensors/sensor_base.h`**

```cpp
#ifndef SENSOR_BASE_H
#define SENSOR_BASE_H

#include <Arduino.h>

class SensorBase {
public:
  virtual void init() = 0;
  virtual void read() = 0;
  virtual ~SensorBase() {}
};

#endif
```

### 3.6 Ejemplo de Sensor - Temperatura DHT22

**Archivo: `sensors/temp_sensor.h`**

```cpp
#ifndef TEMP_SENSOR_H
#define TEMP_SENSOR_H

#include "sensor_base.h"
#include <DHT.h>
#include "../protocol.h"
#include "../config.h"

class TempSensor : public SensorBase {
private:
  DHT* dht;
  
public:
  TempSensor();
  void init() override;
  void read() override;
  ~TempSensor();
};

#endif
```

**Archivo: `sensors/temp_sensor.cpp`**

```cpp
#include "temp_sensor.h"

TempSensor::TempSensor() {
  dht = new DHT(DHT_PIN, DHT_TYPE);
}

void TempSensor::init() {
  dht->begin();
}

void TempSensor::read() {
  float temp = dht->readTemperature();
  float hum = dht->readHumidity();
  
  if (!isnan(temp)) {
    addData(ID_TEMPERATURA, temp);
  }
  
  if (!isnan(hum)) {
    addData(ID_HUMEDAD, hum);
  }
}

TempSensor::~TempSensor() {
  delete dht;
}
```

### 3.7 Ejemplo de Sensor - ECG con ADS1115

**Archivo: `sensors/ecg_sensor.h`**

```cpp
#ifndef ECG_SENSOR_H
#define ECG_SENSOR_H

#include "sensor_base.h"
#include <Adafruit_ADS1X15.h>
#include "../protocol.h"
#include "../config.h"

class ECGSensor : public SensorBase {
private:
  Adafruit_ADS1115* ads;
  
public:
  ECGSensor();
  void init() override;
  void read() override;
  ~ECGSensor();
};

#endif
```

**Archivo: `sensors/ecg_sensor.cpp`**

```cpp
#include "ecg_sensor.h"

ECGSensor::ECGSensor() {
  ads = new Adafruit_ADS1115();
}

void ECGSensor::init() {
  if (!ads->begin(ADS_ADDR)) {
    Serial.println("Error: ADS1115 no encontrado");
  }
  ads->setGain(GAIN_ONE);  // Ajustar según tu circuito
}

void ECGSensor::read() {
  #ifdef ADS_CH0_ACTIVE
    int16_t adc0 = ads->readADC_SingleEnded(0);
    float voltage0 = ads->computeVolts(adc0);
    addData(ID_ECG_CH1, voltage0);
  #endif
  
  #ifdef ADS_CH1_ACTIVE
    int16_t adc1 = ads->readADC_SingleEnded(1);
    float voltage1 = ads->computeVolts(adc1);
    addData(ID_ECG_CH2, voltage1);
  #endif
  
  #ifdef ADS_CH2_ACTIVE
    int16_t adc2 = ads->readADC_SingleEnded(2);
    float voltage2 = ads->computeVolts(adc2);
    addData(ID_ECG_CH3, voltage2);
  #endif
  
  #ifdef ADS_CH3_ACTIVE
    int16_t adc3 = ads->readADC_SingleEnded(3);
    float voltage3 = ads->computeVolts(adc3);
    addData(ID_ECG_CH4, voltage3);
  #endif
}

ECGSensor::~ECGSensor() {
  delete ads;
}
```

### 3.8 Loop Principal

**Archivo: `main.cpp`**

```cpp
#include <Arduino.h>
#include "config.h"
#include "protocol.h"

// Incluir comunicación según modo
#ifdef COMM_MODE_WIFI
  #include "communication/wifi_comm.h"
#elif defined(COMM_MODE_SERIAL)
  #include "communication/serial_comm.h"
#elif defined(COMM_MODE_BLUETOOTH)
  #include "communication/bt_comm.h"
#endif

// Incluir sensores activos
#ifdef USE_TEMP_DHT22
  #include "sensors/temp_sensor.h"
  TempSensor* tempSensor;
#endif

#ifdef USE_ECG_ADS1115
  #include "sensors/ecg_sensor.h"
  ECGSensor* ecgSensor;
#endif

#ifdef USE_HX710B
  #include "sensors/hx710b.h"
  HX710BSensor* hx710bSensor;
#endif

#ifdef USE_TGAM
  #include "sensors/tgam.h"
  TGAMSensor* tgamSensor;
#endif

#ifdef USE_IMU_MPU6050
  #include "sensors/imu_sensor.h"
  IMUSensor* imuSensor;
#endif

void setup() {
  Serial.begin(115200);
  
  // Inicializar protocolo
  initProtocol();
  
  // Inicializar comunicación
  #ifdef COMM_MODE_WIFI
    initWiFi();
  #elif defined(COMM_MODE_SERIAL)
    initSerial();
  #elif defined(COMM_MODE_BLUETOOTH)
    initBluetooth();
  #endif
  
  // Inicializar sensores
  #ifdef USE_TEMP_DHT22
    tempSensor = new TempSensor();
    tempSensor->init();
  #endif
  
  #ifdef USE_ECG_ADS1115
    ecgSensor = new ECGSensor();
    ecgSensor->init();
  #endif
  
  #ifdef USE_HX710B
    hx710bSensor = new HX710BSensor();
    hx710bSensor->init();
  #endif
  
  #ifdef USE_TGAM
    tgamSensor = new TGAMSensor();
    tgamSensor->init();
  #endif
  
  #ifdef USE_IMU_MPU6050
    imuSensor = new IMUSensor();
    imuSensor->init();
  #endif
  
  Serial.println("Sistema iniciado");
}

void loop() {
  // Leer todos los sensores activos
  #ifdef USE_TEMP_DHT22
    tempSensor->read();
  #endif
  
  #ifdef USE_ECG_ADS1115
    ecgSensor->read();
  #endif
  
  #ifdef USE_HX710B
    hx710bSensor->read();
  #endif
  
  #ifdef USE_TGAM
    tgamSensor->read();
  #endif
  
  #ifdef USE_IMU_MPU6050
    imuSensor->read();
  #endif
  
  // Enviar buffer de datos
  sendBuffer();
  
  // Opcional: pequeño delay para estabilidad
  // delay(10);
}
```

---

## 4. Comunicación WiFi

**Archivo: `communication/wifi_comm.h`**

```cpp
#ifndef WIFI_COMM_H
#define WIFI_COMM_H

#include <WiFi.h>

void initWiFi();
void sendWiFi(uint8_t* data, size_t length);

#endif
```

**Archivo: `communication/wifi_comm.cpp`**

```cpp
#include "wifi_comm.h"
#include "../config.h"

WiFiClient client;

void initWiFi() {
  Serial.print("Conectando a WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  
  // Conectar al servidor
  Serial.print("Conectando al servidor...");
  while (!client.connect(SERVER_IP, SERVER_PORT)) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConectado al servidor");
}

void sendWiFi(uint8_t* data, size_t length) {
  if (client.connected()) {
    client.write(data, length);
  } else {
    // Reconectar si se perdió conexión
    if (client.connect(SERVER_IP, SERVER_PORT)) {
      client.write(data, length);
    }
  }
}
```

---

## 5. Comunicación Serial

**Archivo: `communication/serial_comm.h`**

```cpp
#ifndef SERIAL_COMM_H
#define SERIAL_COMM_H

#include <Arduino.h>

void initSerial();
void sendSerial(uint8_t* data, size_t length);

#endif
```

**Archivo: `communication/serial_comm.cpp`**

```cpp
#include "serial_comm.h"
#include "../config.h"

void initSerial() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial) {
    delay(10);
  }
  Serial.println("Serial iniciado");
}

void sendSerial(uint8_t* data, size_t length) {
  Serial.write(data, length);
}
```

---

## 6. Comunicación Bluetooth

**Archivo: `communication/bt_comm.h`**

```cpp
#ifndef BT_COMM_H
#define BT_COMM_H

#include <BluetoothSerial.h>

void initBluetooth();
void sendBluetooth(uint8_t* data, size_t length);

#endif
```

**Archivo: `communication/bt_comm.cpp`**

```cpp
#include "bt_comm.h"
#include "../config.h"

BluetoothSerial SerialBT;

void initBluetooth() {
  if (!SerialBT.begin(BT_DEVICE_NAME)) {
    Serial.println("Error: Bluetooth no iniciado");
    while(1);
  }
  Serial.println("Bluetooth iniciado");
}

void sendBluetooth(uint8_t* data, size_t length) {
  SerialBT.write(data, length);
}
```

---

## 7. Proceso de Configuración por Dispositivo

### 7.1 Pasos para Configurar un Nuevo ESP32

1. **Editar `config.h`:**
   - Cambiar `ESP32_ID` a un valor único
   - Seleccionar modo de comunicación (WiFi/Serial/BT)
   - Configurar credenciales WiFi si aplica
   - Activar/desactivar sensores con `#define`
   - Configurar pines según hardware

2. **Compilar y Cargar:**
   ```bash
   pio run -t upload
   ```

3. **Verificar en Monitor Serial:**
   ```bash
   pio device monitor
   ```

### 7.2 Ejemplo de Configuraciones

**Dispositivo 1 - ECG con 2 canales + Temperatura**
```cpp
#define ESP32_ID 0x0001
#define COMM_MODE_WIFI
#define USE_TEMP_DHT22
#define USE_ECG_ADS1115
#define ADS_CH0_ACTIVE true
#define ADS_CH1_ACTIVE true
#define ADS_CH2_ACTIVE false
#define ADS_CH3_ACTIVE false
```

**Dispositivo 2 - Solo presión HX710B**
```cpp
#define ESP32_ID 0x0002
#define COMM_MODE_SERIAL
#define USE_HX710B
#define HX710B_MODE_PRESSURE
```

**Dispositivo 3 - EEG TGAM + IMU**
```cpp
#define ESP32_ID 0x0003
#define COMM_MODE_BLUETOOTH
#define USE_TGAM
#define USE_IMU_MPU6050
#define IMU_USE_DMP true
```

---

## 8. Expansión y Mantenimiento

### 8.1 Agregar Nuevo Sensor

1. Crear `sensors/nuevo_sensor.h` y `.cpp`
2. Heredar de `SensorBase`
3. Implementar `init()` y `read()`
4. En `read()`: usar `addData(ID_SENSOR, valor)`
5. Agregar `#define USE_NUEVO_SENSOR` en `config.h`
6. Incluir en `main.cpp`

### 8.2 Agregar Nuevo ID de Sensor

1. Definir en `protocol.h`:
   ```cpp
   #define ID_NUEVO_SENSOR 0xXX
   ```
2. Documentar en este archivo
3. Actualizar tabla Python del receptor

### 8.3 Verificación de Integridad

- **CRC16:** Verificar en receptor que CRC coincide
- **SYNC:** Buscar `0xFF 0xAA` para sincronizar stream
- **Timestamp:** Detectar pérdidas o saltos temporales

---

## 9. Troubleshooting

### 9.1 No se reciben datos

- Verificar conexión (WiFi/Serial/BT)
- Revisar que sensores inicialicen correctamente
- Comprobar que `sendBuffer()` se ejecuta
- Ver monitor serial para errores

### 9.2 Datos corruptos

- Verificar CRC16 en receptor
- Revisar endianness (debe ser little-endian)
- Comprobar que SYNC está presente
- Verificar baudrate en Serial

### 9.3 Latencia alta

- Reducir `delay()` en loop
- Verificar WiFi: usar TCP en vez de UDP si hay pérdidas
- Optimizar frecuencia de lectura de sensores lentos

---

## 10. Dependencias PlatformIO

**Archivo: `platformio.ini`**

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino

lib_deps = 
    adafruit/Adafruit ADS1X15@^2.4.0
    adafruit/DHT sensor library@^1.4.4
    adafruit/Adafruit Unified Sensor@^1.1.9
    Wire
    SPI

monitor_speed = 115200
```

---

## 11. Notas Finales

- **Datos RAW:** Siempre enviar valores sin calibrar, calibración en Python
- **Sin ACK:** Streaming unidireccional para máxima velocidad
- **Modular:** Fácil activar/desactivar sensores por `#define`
- **Un solo firmware:** Misma base de código para todos los ESP32
- **Escalable:** Agregar sensores sin cambiar protocolo