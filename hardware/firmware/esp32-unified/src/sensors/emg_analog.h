#ifndef EMG_ANALOG_H
#define EMG_ANALOG_H

#include "sensor_base.h"
#include "../protocol.h"
#include "../config.h"

class EMG_Analog : public SensorBase {
private:
  unsigned long lastSampleTime;
  unsigned long sampleInterval;  // Microsegundos entre muestras

public:
  EMG_Analog();
  void init() override;
  void read() override;
  ~EMG_Analog();
};

#endif
