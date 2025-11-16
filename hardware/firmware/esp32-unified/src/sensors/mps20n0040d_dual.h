#ifndef MPS20N0040D_DUAL_H
#define MPS20N0040D_DUAL_H

#include "sensor_base.h"
#include "../protocol.h"
#include "../config.h"

class MPS20N0040DDual : public SensorBase {
private:
  // Funciones privadas
  long readHX710B(uint8_t doutPin, uint8_t sckPin);
  bool initHX710B(uint8_t doutPin, uint8_t sckPin);

public:
  MPS20N0040DDual();
  void init() override;
  void read() override;
  ~MPS20N0040DDual();
};

#endif
