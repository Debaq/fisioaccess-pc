#include "emg_analog.h"

EMG_Analog::EMG_Analog() {
  lastSampleTime = 0;
  sampleInterval = 1000000 / EMG_SAMPLE_RATE;  // Convertir Hz a microsegundos
}

void EMG_Analog::init() {
  // Configurar pin analógico
  pinMode(EMG_ANALOG_PIN, INPUT);

  // Configurar resolución del ADC (ESP32 tiene ADC de 12 bits)
  analogReadResolution(12);

  // Configurar atenuación del ADC (0-3.3V)
  analogSetAttenuation(ADC_11db);

  lastSampleTime = micros();

  Serial.println("EMG Analógico inicializado");
  Serial.print("Frecuencia de muestreo: ");
  Serial.print(EMG_SAMPLE_RATE);
  Serial.println(" Hz");
}

void EMG_Analog::read() {
  unsigned long currentTime = micros();

  // Controlar frecuencia de muestreo
  if (currentTime - lastSampleTime < sampleInterval) {
    return;  // Aún no es tiempo de muestrear
  }

  lastSampleTime = currentTime;

  // Leer valor analógico (0-4095 en ESP32 con 12 bits)
  int adcValue = analogRead(EMG_ANALOG_PIN);

  // Convertir a voltaje (0-3.3V)
  float voltage = (adcValue / 4095.0) * 3.3;

  // Enviar valor RAW (voltaje)
  addData(ID_EMG_CH1, voltage);
}

EMG_Analog::~EMG_Analog() {
  // Cleanup si es necesario
}
