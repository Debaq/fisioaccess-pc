#include "ecg_ads1115.h"

ECG_ADS1115::ECG_ADS1115() {
  ads = new Adafruit_ADS1115();
  leadsConnected = false;
}

void ECG_ADS1115::init() {
  // Configurar pines de lead detection
  pinMode(ECG_LD_PLUS_PIN, INPUT);
  pinMode(ECG_LD_MINUS_PIN, INPUT);

  Serial.println("Inicializando ECG con ADS1115...");

  // Inicializar ADS1115
  if (!ads->begin(ECG_ADS_ADDR)) {
    Serial.println("Error: ADS1115 no encontrado en dirección configurada");
    return;
  }

  // Configurar ganancia según config.h
  ads->setGain(ECG_ADS_GAIN);

  // Configurar frecuencia de muestreo (860 SPS para ECG)
  ads->setDataRate(RATE_ADS1115_860SPS);

  Serial.println("ADS1115 inicializado correctamente");
  Serial.print("Ganancia configurada: ");
  Serial.println(ECG_ADS_GAIN);
}

bool ECG_ADS1115::checkLeadDetection() {
  // Leer estado de los pines de lead detection
  // Normalmente LOW = conectado, HIGH = desconectado
  int ldPlus = digitalRead(ECG_LD_PLUS_PIN);
  int ldMinus = digitalRead(ECG_LD_MINUS_PIN);

  // Si ambos están LOW, los electrodos están conectados
  return (ldPlus == LOW && ldMinus == LOW);
}

void ECG_ADS1115::read() {
  // Verificar estado de leads
  bool ldPlus = (digitalRead(ECG_LD_PLUS_PIN) == LOW);
  bool ldMinus = (digitalRead(ECG_LD_MINUS_PIN) == LOW);
  leadsConnected = (ldPlus && ldMinus);

  // Enviar estado de leads
  addData(ID_ECG_LD_PLUS, ldPlus ? 1.0 : 0.0);
  addData(ID_ECG_LD_MINUS, ldMinus ? 1.0 : 0.0);

  // Leer señal ECG del canal configurado (A0)
  int16_t adc = ads->readADC_SingleEnded(ECG_ADS_CHANNEL);

  // Convertir a voltaje
  float voltage = ads->computeVolts(adc);

  // Enviar valor RAW (voltaje)
  addData(ID_ECG_CH1, voltage);
}

ECG_ADS1115::~ECG_ADS1115() {
  delete ads;
}
