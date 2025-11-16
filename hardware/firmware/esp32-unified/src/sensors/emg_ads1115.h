#ifndef EMG_ADS1115_H
#define EMG_ADS1115_H

#include "sensor_base.h"
#include <Adafruit_ADS1X15.h>
#include "../protocol.h"
#include "../config.h"

class EMG_ADS1115 : public SensorBase {
private:
  Adafruit_ADS1115* ads;

public:
  EMG_ADS1115();
  void init() override;
  void read() override;
  ~EMG_ADS1115();
};

#endif
