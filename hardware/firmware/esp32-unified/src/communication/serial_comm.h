#ifndef SERIAL_COMM_H
#define SERIAL_COMM_H

#include <Arduino.h>

void initSerial();
void sendSerial(uint8_t* data, size_t length);

#endif
