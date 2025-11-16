#ifndef ECG_ADS1115_H
#define ECG_ADS1115_H

#include "sensor_base.h"
#include <Adafruit_ADS1X15.h>
#include "../protocol.h"
#include "../config.h"

class ECG_ADS1115 : public SensorBase {
private:
  Adafruit_ADS1115* ads;
  bool leadsConnected;

  bool checkLeadDetection();

public:
  ECG_ADS1115();
  void init() override;
  void read() override;
  ~ECG_ADS1115();
};

#endif
