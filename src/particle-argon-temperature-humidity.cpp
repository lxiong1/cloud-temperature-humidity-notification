/******************************************************/
//       THIS IS A GENERATED FILE - DO NOT EDIT       //
/******************************************************/

#include "Particle.h"
#line 1 "/home/luexiong/projects/particle-argon-temperature-humidity/src/particle-argon-temperature-humidity.ino"
#include "Adafruit_Si7021.h" 

void setup();
void loop(void);
#line 3 "/home/luexiong/projects/particle-argon-temperature-humidity/src/particle-argon-temperature-humidity.ino"
Adafruit_Si7021 sensor = Adafruit_Si7021();

void setup() {
  sensor.begin();
}

void loop(void) {
  int celsius = sensor.readTemperature();
  int fahrenheit = (celsius * 9 / 5) + 32;
  int humidityPercentage = sensor.readHumidity();

  Particle.publish("temperature", String(fahrenheit));
  Particle.publish("humidity", String(29));
  delay(10000);
}
