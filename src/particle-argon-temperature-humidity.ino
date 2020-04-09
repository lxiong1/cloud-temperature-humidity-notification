#include "Adafruit_Si7021.h" 

Adafruit_Si7021 sensor = Adafruit_Si7021();
bool updated = false;

void setup() {
  Serial.begin(9600);
  sensor.begin();
}

void loop(void) {
  int celsius = sensor.readTemperature();
  int fahrenheit = (celsius * 9 / 5) + 32;
  int humidityPercentage = sensor.readHumidity();

  Particle.publish("temperature", String(fahrenheit), PRIVATE);
  Particle.publish("humidity", String(humidityPercentage), PRIVATE);
  delay(10000);

  if (isEndOfDay() == true) {
    Particle.publish("climateAverageUpdate", "Updating climate data file", PRIVATE);
  }
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
