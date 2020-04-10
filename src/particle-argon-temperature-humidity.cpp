/******************************************************/
//       THIS IS A GENERATED FILE - DO NOT EDIT       //
/******************************************************/

#include "Particle.h"
#line 1 "/home/luexiong/projects/cloud-temperature-humidity-system/src/particle-argon-temperature-humidity.ino"
#include "Adafruit_Si7021.h" 

void setup();
void loop(void);
boolean isEndOfDay();
#line 3 "/home/luexiong/projects/cloud-temperature-humidity-system/src/particle-argon-temperature-humidity.ino"
Adafruit_Si7021 sensor = Adafruit_Si7021();
SystemSleepConfiguration systemSleepConfiguration;
bool updated = false;

void setup() {
  sensor.begin();
}

void loop(void) {
  int celsius = sensor.readTemperature();
  int fahrenheit = (celsius * 9 / 5) + 32;
  int humidityPercentage = sensor.readHumidity();

  Particle.publish("temperature", String(fahrenheit), PRIVATE);
  Particle.publish("humidity", String(humidityPercentage), PRIVATE);

  if (isEndOfDay() == true) {
    Particle.publish("climateAverageUpdate", "Updating climate data file", PRIVATE);
  }

  delay(10s);

  System.sleep(systemSleepConfiguration
    .network(NETWORK_INTERFACE_CELLULAR)
    .flag(SystemSleepFlag::WAIT_CLOUD)
    .mode(SystemSleepMode::STOP)
    .duration(50s));
}

boolean isEndOfDay() {
  int currentHour = Time.hourFormat12(Time.now());

  if (updated == false && currentHour >= 9 && Time.isPM() == true) {
    updated = true;
    return true;
  }

  if (updated == true && currentHour >= 6 && Time.isAM() == true) {
    updated = false;
    return false;
  }

  return false;
}
