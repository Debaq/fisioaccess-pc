#include "mps20n0040d_dual.h"
#include <math.h>

MPS20N0040DDual::MPS20N0040DDual() {
  calibrationOffset1 = 0;
  calibrationOffset2 = 0;
  volume1 = 0.0;
  volume2 = 0.0;
  lastMeasurementTime = 0;
}

void MPS20N0040DDual::init() {
  // Configurar pines sensor 1
  pinMode(MPS_SCK_PIN_1, OUTPUT);
  pinMode(MPS_DOUT_PIN_1, INPUT);
  digitalWrite(MPS_SCK_PIN_1, LOW);

  // Configurar pines sensor 2
  pinMode(MPS_SCK_PIN_2, OUTPUT);
  pinMode(MPS_DOUT_PIN_2, INPUT);
  digitalWrite(MPS_SCK_PIN_2, LOW);

  Serial.println("Inicializando sensores MPS20N0040D...");

  // Inicializar HX710B sensor 1
  if (!initHX710B(MPS_DOUT_PIN_1, MPS_SCK_PIN_1)) {
    Serial.println("Error: Sensor 1 no responde");
  }

  // Inicializar HX710B sensor 2
  if (!initHX710B(MPS_DOUT_PIN_2, MPS_SCK_PIN_2)) {
    Serial.println("Error: Sensor 2 no responde");
  }

  // Calibrar ambos sensores
  Serial.println("Calibrando sensor 1...");
  calibrateSensor(MPS_DOUT_PIN_1, MPS_SCK_PIN_1, calibrationOffset1);

  Serial.println("Calibrando sensor 2...");
  calibrateSensor(MPS_DOUT_PIN_2, MPS_SCK_PIN_2, calibrationOffset2);

  lastMeasurementTime = millis();
  Serial.println("Sensores MPS20N0040D listos");
}

long MPS20N0040DDual::readHX710B(uint8_t doutPin, uint8_t sckPin) {
  long data = 0;

  // Esperar a que DOUT esté bajo
  while (digitalRead(doutPin) == HIGH) yield();

  // Leer 24 bits
  for (uint8_t i = 0; i < 24; i++) {
    digitalWrite(sckPin, HIGH);
    delayMicroseconds(1);
    data = (data << 1) | digitalRead(doutPin);
    digitalWrite(sckPin, LOW);
    delayMicroseconds(1);
  }

  // Pulso adicional para preparar próxima lectura
  digitalWrite(sckPin, HIGH);
  delayMicroseconds(1);
  digitalWrite(sckPin, LOW);

  // Extender signo si es negativo
  if (data & 0x00800000) data |= 0xFF000000;

  return data;
}

bool MPS20N0040DDual::initHX710B(uint8_t doutPin, uint8_t sckPin) {
  digitalWrite(sckPin, HIGH);
  delayMicroseconds(100);
  digitalWrite(sckPin, LOW);
  delay(100);

  int attempts = 0;
  while (digitalRead(doutPin) == HIGH && attempts < 50) {
    delay(10);
    attempts++;
  }

  if (attempts >= 50) return false;

  readHX710B(doutPin, sckPin); // Lectura dummy
  delay(10);

  return true;
}

void MPS20N0040DDual::calibrateSensor(uint8_t doutPin, uint8_t sckPin, long& offset) {
  const int TOTAL = MPS_CALIBRATION_SAMPLES;
  long sumValues = 0;

  Serial.println("Iniciando calibración...");
  Serial.println("Asegúrese que no hay flujo de aire");
  delay(2000);

  for (int i = 0; i < TOTAL; i++) {
    long adc = readHX710B(doutPin, sckPin);
    sumValues += adc;

    if (i % (TOTAL / 10) == 0) {
      Serial.print("Calibrando: ");
      Serial.print((i * 100L) / TOTAL);
      Serial.println('%');
    }

    delay(10);
  }

  offset = sumValues / TOTAL;

  Serial.print("Calibración completada. Offset: ");
  Serial.println(offset);
}

float MPS20N0040DDual::getPressureKPA(uint8_t doutPin, uint8_t sckPin, long offset) {
  long adc = readHX710B(doutPin, sckPin);
  long calibrated = adc - offset;
  float pressure = (calibrated * MPS_COUNTS_TO_KPA) / MPS_DIVISION_FACTOR;
  return pressure;
}

float MPS20N0040DDual::calculateFlow(float pressureKPA) {
  if (abs(pressureKPA) < PRESSURE_THRESHOLD) {
    return 0.0;
  }

  int direction = (pressureKPA >= 0) ? 1 : -1;
  float flowRate = direction * FLOW_CONSTANT * sqrt(abs(pressureKPA));

  if (abs(flowRate) < FLOW_THRESHOLD) {
    return 0.0;
  }

  return flowRate;
}

void MPS20N0040DDual::read() {
  unsigned long currentTime = millis();
  float deltaTimeSeconds = (currentTime - lastMeasurementTime) / 1000.0;

  // Leer sensor 1
  float pressure1 = getPressureKPA(MPS_DOUT_PIN_1, MPS_SCK_PIN_1, calibrationOffset1);
  float flow1 = calculateFlow(pressure1);

  // Leer sensor 2
  float pressure2 = getPressureKPA(MPS_DOUT_PIN_2, MPS_SCK_PIN_2, calibrationOffset2);
  float flow2 = calculateFlow(pressure2);

  // Integrar volumen si hay flujo significativo
  if (abs(flow1) >= FLOW_THRESHOLD && deltaTimeSeconds > 0 && deltaTimeSeconds < 1.0) {
    volume1 += flow1 * deltaTimeSeconds;
  }

  if (abs(flow2) >= FLOW_THRESHOLD && deltaTimeSeconds > 0 && deltaTimeSeconds < 1.0) {
    volume2 += flow2 * deltaTimeSeconds;
  }

  lastMeasurementTime = currentTime;

  // Enviar datos al buffer del protocolo
  addData(ID_PRESION_1, pressure1);
  addData(ID_FLUJO_1, flow1);
  addData(ID_VOLUMEN_1, volume1);
  addData(ID_PRESION_2, pressure2);
  addData(ID_FLUJO_2, flow2);
  addData(ID_VOLUMEN_2, volume2);
}

void MPS20N0040DDual::resetVolume() {
  volume1 = 0.0;
  volume2 = 0.0;
  lastMeasurementTime = millis();
  Serial.println("Volumen reiniciado");
}

MPS20N0040DDual::~MPS20N0040DDual() {
  // Cleanup si es necesario
}
