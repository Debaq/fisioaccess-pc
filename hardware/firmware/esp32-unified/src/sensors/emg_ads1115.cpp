#include "emg_ads1115.h"

EMG_ADS1115::EMG_ADS1115() {
  ads = new Adafruit_ADS1115();
}

void EMG_ADS1115::init() {
  Serial.println("Inicializando EMG con ADS1115...");

  // Inicializar ADS1115
  if (!ads->begin(EMG_ADS_ADDR)) {
    Serial.println("Error: ADS1115 no encontrado en dirección configurada");
    return;
  }

  // Configurar ganancia según config.h
  ads->setGain(EMG_ADS_GAIN);

  // Configurar frecuencia de muestreo alta para EMG (860 SPS)
  ads->setDataRate(RATE_ADS1115_860SPS);

  Serial.println("ADS1115 para EMG inicializado correctamente");
  Serial.print("Ganancia configurada: ");
  Serial.println(EMG_ADS_GAIN);
}

void EMG_ADS1115::read() {
  // Leer señal EMG del canal configurado
  int16_t adc = ads->readADC_SingleEnded(EMG_ADS_CHANNEL);

  // Convertir a voltaje
  float voltage = ads->computeVolts(adc);

  // Enviar valor RAW (voltaje)
  addData(ID_EMG_CH1, voltage);
}

EMG_ADS1115::~EMG_ADS1115() {
  delete ads;
}
