#ifndef SENSOR_BASE_H
#define SENSOR_BASE_H

#include <Arduino.h>

class SensorBase {
public:
  virtual void init() = 0;
  virtual void read() = 0;
  virtual ~SensorBase() {}
};

#endif
