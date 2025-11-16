#include "serial_comm.h"
#include "../config.h"

void initSerial() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial) {
    delay(10);
  }
  Serial.println("Comunicación Serial iniciada");
  Serial.print("Baudrate: ");
  Serial.println(SERIAL_BAUD);
}

void sendSerial(uint8_t* data, size_t length) {
  Serial.write(data, length);
  Serial.flush();  // Asegurar que los datos se envíen completamente
}
