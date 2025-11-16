#ifndef MPS20N0040D_DUAL_H
#define MPS20N0040D_DUAL_H

#include "sensor_base.h"
#include "../protocol.h"
#include "../config.h"

class MPS20N0040DDual : public SensorBase {
private:
  // Calibración
  long calibrationOffset1;
  long calibrationOffset2;

  // Mediciones
  float volume1;
  float volume2;
  unsigned long lastMeasurementTime;

  // Constantes de flujo
  const float FLOW_CONSTANT = 6.77;
  const float PRESSURE_THRESHOLD = 0.010;
  const float FLOW_THRESHOLD = 0.1;

  // Funciones privadas
  long readHX710B(uint8_t doutPin, uint8_t sckPin);
  bool initHX710B(uint8_t doutPin, uint8_t sckPin);
  float getPressureKPA(uint8_t doutPin, uint8_t sckPin, long offset);
  float calculateFlow(float pressureKPA);
  void calibrateSensor(uint8_t doutPin, uint8_t sckPin, long& offset);

public:
  MPS20N0040DDual();
  void init() override;
  void read() override;
  void resetVolume();
  ~MPS20N0040DDual();
};

#endif
