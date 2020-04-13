#include "Adafruit_Si7021.h"
#include "stdbool.h"

Adafruit_Si7021 sensor = Adafruit_Si7021();
SystemSleepConfiguration systemSleepConfiguration;
bool updated = false;
int publishIntervalMilliseconds = 300000;

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
    publishIntervalMilliseconds = 1800000;
  } else {
    publishIntervalMilliseconds = 300000;
  }

  delay(5000);

  System.sleep(systemSleepConfiguration
    .gpio(WKP, RISING)
    .network(NETWORK_INTERFACE_CELLULAR)
    .flag(SystemSleepFlag::WAIT_CLOUD)
    .mode(SystemSleepMode::STOP)
    .duration(publishIntervalMilliseconds));
}

bool isEndOfDay() {
  int now = Time.now();
  int currentHour = Time.hour(now);
  int isMorning = Time.isAM(now);

  if (updated == false && currentHour >= 21) {
    updated = true;
    return true;
  }

  if (updated == true && currentHour >= 6 && isMorning) {
    updated = false;
    return false;
  }

  return false;
}
