/*
  Lectura HX710B con ESP32-C3
  GPIO 5 -> DOUT
  GPIO 6 -> SCK
  Autor: tu nombre
*/

#define DOUT 5   // cambiar si lo necesitas
#define SCK  6

void setup() {
  Serial.begin(115200);
  pinMode(SCK, OUTPUT);
  pinMode(DOUT, INPUT);

  Serial.println("HX710B test – ESP32-C3");
}

/*  Lectura cruda 24-bit del HX710B/HX711  */
long readHX710B() {
  long data = 0;

  // esperar a que DOUT baje (dato listo)
  while (digitalRead(DOUT) == HIGH) yield();

  // desplazar 24 bits (MSB first)
  for (uint8_t i = 0; i < 24; i++) {
    digitalWrite(SCK, HIGH);
    delayMicroseconds(1);
    data = (data << 1) | digitalRead(DOUT);
    digitalWrite(SCK, LOW);
    delayMicroseconds(1);
  }

  // pulso 25 para volver al modo de conversión (ganancia 128)
  digitalWrite(SCK, HIGH);
  delayMicroseconds(1);
  digitalWrite(SCK, LOW);

  // sign-extend de 24 a 32 bits
  if (data & 0x00800000) data |= 0xFF000000;

  return data;
}

// ---------- loop ----------
long raw;
float offset = 0;   // lo calibrarás después
float scale  = 1.0; // factor de escala (kPa / count)

void loop() {
  raw = readHX710B();

  // restar offset para tener “0” a 1 atm
  float press = (raw - offset) * scale;

  Serial.print("Raw: "); Serial.print(raw);
  Serial.print("   ->  "); Serial.print(press, 2);
  Serial.println(" kPa");

  delay(10);
}