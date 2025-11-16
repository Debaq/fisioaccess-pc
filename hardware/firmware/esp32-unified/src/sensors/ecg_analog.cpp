#include "ecg_analog.h"

ECG_Analog::ECG_Analog() {
  lastSampleTime = 0;
  sampleInterval = 1000000 / ECG_SAMPLE_RATE;  // Convertir Hz a microsegundos
  leadsConnected = false;
}

void ECG_Analog::init() {
  // Configurar pin analógico
  pinMode(ECG_ANALOG_PIN, INPUT);

  // Configurar pines de lead detection
  pinMode(ECG_LD_PLUS_PIN, INPUT);
  pinMode(ECG_LD_MINUS_PIN, INPUT);

  // Configurar resolución del ADC (ESP32 tiene ADC de 12 bits)
  analogReadResolution(12);

  // Configurar atenuación del ADC (0-3.3V)
  analogSetAttenuation(ADC_11db);

  lastSampleTime = micros();

  Serial.println("ECG Analógico inicializado");
  Serial.print("Frecuencia de muestreo: ");
  Serial.print(ECG_SAMPLE_RATE);
  Serial.println(" Hz");
}

bool ECG_Analog::checkLeadDetection() {
  // Leer estado de los pines de lead detection
  int ldPlus = digitalRead(ECG_LD_PLUS_PIN);
  int ldMinus = digitalRead(ECG_LD_MINUS_PIN);

  return (ldPlus == LOW && ldMinus == LOW);
}

void ECG_Analog::read() {
  unsigned long currentTime = micros();

  // Controlar frecuencia de muestreo
  if (currentTime - lastSampleTime < sampleInterval) {
    return;  // Aún no es tiempo de muestrear
  }

  lastSampleTime = currentTime;

  // Verificar estado de leads
  bool ldPlus = (digitalRead(ECG_LD_PLUS_PIN) == LOW);
  bool ldMinus = (digitalRead(ECG_LD_MINUS_PIN) == LOW);
  leadsConnected = (ldPlus && ldMinus);

  // Enviar estado de leads
  addData(ID_ECG_LD_PLUS, ldPlus ? 1.0 : 0.0);
  addData(ID_ECG_LD_MINUS, ldMinus ? 1.0 : 0.0);

  // Leer valor analógico (0-4095 en ESP32 con 12 bits)
  int adcValue = analogRead(ECG_ANALOG_PIN);

  // Convertir a voltaje (0-3.3V)
  float voltage = (adcValue / 4095.0) * 3.3;

  // Enviar valor RAW (voltaje)
  addData(ID_ECG_CH1, voltage);
}

ECG_Analog::~ECG_Analog() {
  // Cleanup si es necesario
}
