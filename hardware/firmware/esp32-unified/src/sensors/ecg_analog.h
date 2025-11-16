#ifndef ECG_ANALOG_H
#define ECG_ANALOG_H

#include "sensor_base.h"
#include "../protocol.h"
#include "../config.h"

class ECG_Analog : public SensorBase {
private:
  unsigned long lastSampleTime;
  unsigned long sampleInterval;  // Microsegundos entre muestras
  bool leadsConnected;

  bool checkLeadDetection();

public:
  ECG_Analog();
  void init() override;
  void read() override;
  ~ECG_Analog();
};

#endif
