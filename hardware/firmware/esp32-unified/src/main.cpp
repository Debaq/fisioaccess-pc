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
#ifdef USE_MPS20N0040D_DUAL
  #include "sensors/mps20n0040d_dual.h"
  MPS20N0040DDual* mpsensor;
#endif

#ifdef USE_ECG_ADS1115
  #include "sensors/ecg_ads1115.h"
  ECG_ADS1115* ecgSensor;
#endif

#ifdef USE_ECG_ANALOG
  #include "sensors/ecg_analog.h"
  ECG_Analog* ecgSensor;
#endif

#ifdef USE_EMG_ADS1115
  #include "sensors/emg_ads1115.h"
  EMG_ADS1115* emgSensor;
#endif

#ifdef USE_EMG_ANALOG
  #include "sensors/emg_analog.h"
  EMG_Analog* emgSensor;
#endif

void setup() {
  Serial.begin(115200);
  delay(100);

  Serial.println("========================================");
  Serial.println("ESP32 Firmware Unificado - FisioAccess");
  Serial.println("========================================");
  Serial.print("ID del dispositivo: 0x");
  Serial.println(ESP32_ID, HEX);
  Serial.println();

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

  Serial.println();
  Serial.println("Inicializando sensores...");
  Serial.println("----------------------------------------");

  // Inicializar sensores
  #ifdef USE_MPS20N0040D_DUAL
    mpsensor = new MPS20N0040DDual();
    mpsensor->init();
    Serial.println("[OK] MPS20N0040D Dual");
  #endif

  #ifdef USE_ECG_ADS1115
    ecgSensor = new ECG_ADS1115();
    ecgSensor->init();
    Serial.println("[OK] ECG con ADS1115");
  #endif

  #ifdef USE_ECG_ANALOG
    ecgSensor = new ECG_Analog();
    ecgSensor->init();
    Serial.println("[OK] ECG Analógico");
  #endif

  #ifdef USE_EMG_ADS1115
    emgSensor = new EMG_ADS1115();
    emgSensor->init();
    Serial.println("[OK] EMG con ADS1115");
  #endif

  #ifdef USE_EMG_ANALOG
    emgSensor = new EMG_Analog();
    emgSensor->init();
    Serial.println("[OK] EMG Analógico");
  #endif

  Serial.println("----------------------------------------");
  Serial.println("Sistema iniciado correctamente");
  Serial.println("Comenzando transmisión de datos...");
  Serial.println("========================================");
  Serial.println();
}

void loop() {
  // Leer todos los sensores activos
  #ifdef USE_MPS20N0040D_DUAL
    mpsensor->read();
  #endif

  #ifdef USE_ECG_ADS1115
    ecgSensor->read();
  #endif

  #ifdef USE_ECG_ANALOG
    ecgSensor->read();
  #endif

  #ifdef USE_EMG_ADS1115
    emgSensor->read();
  #endif

  #ifdef USE_EMG_ANALOG
    emgSensor->read();
  #endif

  // Enviar buffer de datos
  sendBuffer();

  // Pequeño delay para estabilidad (opcional, ajustar según necesidad)
  // Para ECG/EMG de alta frecuencia, comentar o reducir este delay
  // delay(1);
}
