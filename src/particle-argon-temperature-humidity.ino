#include "Adafruit_Si7021.h" 

Adafruit_Si7021 sensor = Adafruit_Si7021();

void setup() {
  sensor.begin();
}

void loop(void) {
  int celsius = sensor.readTemperature();
  int fahrenheit = (celsius * 9 / 5) + 32;
  int humidityPercentage = sensor.readHumidity();

  Particle.publish("temperature", String(fahrenheit));
  Particle.publish("humidity", String(humidityPercentage));
  delay(10000);
}
