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
  Time.zone(-5);
  sensor.begin();
}

void loop(void) {
  int degreesCelsius = sensor.readTemperature();
  int degreesFahrenheit = (degreesCelsius * 9 / 5) + 32;
  int relativeHumidity = sensor.readHumidity();

  Particle.publish("temperature", String(degreesFahrenheit), PRIVATE);
  Particle.publish("humidity", String(relativeHumidity), PRIVATE);

  if (isEndOfDay() == true) {
    Particle.publish("climateAverageUpdate", "Updating climate data file", PRIVATE);
  }

  delay(10s);

  System.sleep(systemSleepConfiguration
    .gpio(WKP, RISING)
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
