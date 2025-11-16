#include "mps20n0040d_dual.h"

MPS20N0040DDual::MPS20N0040DDual() {
  // Constructor
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
  } else {
    Serial.println("Sensor 1 inicializado");
  }

  // Inicializar HX710B sensor 2
  if (!initHX710B(MPS_DOUT_PIN_2, MPS_SCK_PIN_2)) {
    Serial.println("Error: Sensor 2 no responde");
  } else {
    Serial.println("Sensor 2 inicializado");
  }

  Serial.println("Sensores MPS20N0040D listos - Enviando datos RAW");
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

void MPS20N0040DDual::read() {
  // Leer valor RAW del sensor 1 (HX710B devuelve valor de 24 bits con signo)
  long raw1 = readHX710B(MPS_DOUT_PIN_1, MPS_SCK_PIN_1);

  // Leer valor RAW del sensor 2
  long raw2 = readHX710B(MPS_DOUT_PIN_2, MPS_SCK_PIN_2);

  // Enviar valores RAW como float al buffer del protocolo
  // Python se encargará de:
  // - Calibrar (restar offset)
  // - Convertir a kPa
  // - Calcular flujo
  // - Integrar volumen
  addData(ID_PRESION_1, (float)raw1);
  addData(ID_PRESION_2, (float)raw2);
}

MPS20N0040DDual::~MPS20N0040DDual() {
  // Cleanup si es necesario
}
