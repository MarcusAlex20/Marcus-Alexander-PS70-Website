#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <SoftwareSerial.h>

// MPU6050 sensor
Adafruit_MPU6050 mpu;

// Cap sensor pins
const int CAP_SENSOR_DIGITAL_1 = 2;  // Digital pin for first cap sensor
const int CAP_SENSOR_DIGITAL_2 = 3;  // Digital pin for second cap sensor
const int CAP_SENSOR_ANALOG_1 = A0;  // Analog pin for first cap sensor
const int CAP_SENSOR_ANALOG_2 = A1;  // Analog pin for second cap sensor

// Threshold values for cap sensors
const int CAP_DIGITAL_THRESHOLD = 500;  // Threshold for digital readings
const int CAP_ANALOG_THRESHOLD = 500;   // Threshold for analog readings

// Variables to store sensor readings
int capDigital1Value = 0;
int capDigital2Value = 0;
int capAnalog1Value = 0;
int capAnalog2Value = 0;

void setup() {
  Serial.begin(9600);
  
  // Initialize MPU6050
  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }
  
  // Configure MPU6050
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  
  // Initialize cap sensor pins
  pinMode(CAP_SENSOR_DIGITAL_1, INPUT);
  pinMode(CAP_SENSOR_DIGITAL_2, INPUT);
  pinMode(CAP_SENSOR_ANALOG_1, INPUT);
  pinMode(CAP_SENSOR_ANALOG_2, INPUT);
  
  Serial.println("Smart Headgear initialized");
}

void loop() {
  // Read MPU6050 data
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  // Read cap sensor values
  capDigital1Value = digitalRead(CAP_SENSOR_DIGITAL_1);
  capDigital2Value = digitalRead(CAP_SENSOR_DIGITAL_2);
  capAnalog1Value = analogRead(CAP_SENSOR_ANALOG_1);
  capAnalog2Value = analogRead(CAP_SENSOR_ANALOG_2);
  
  // Calculate impact magnitude
  float magnitude = sqrt(
    a.acceleration.x * a.acceleration.x +
    a.acceleration.y * a.acceleration.y +
    a.acceleration.z * a.acceleration.z
  );
  
  // Create JSON data
  Serial.print("{");
  Serial.print("\"x\":");
  Serial.print(a.acceleration.x);
  Serial.print(",\"y\":");
  Serial.print(a.acceleration.y);
  Serial.print(",\"z\":");
  Serial.print(a.acceleration.z);
  Serial.print(",\"magnitude\":");
  Serial.print(magnitude);
  Serial.print(",\"cap_digital_1\":");
  Serial.print(capDigital1Value);
  Serial.print(",\"cap_digital_2\":");
  Serial.print(capDigital2Value);
  Serial.print(",\"cap_analog_1\":");
  Serial.print(capAnalog1Value);
  Serial.print(",\"cap_analog_2\":");
  Serial.print(capAnalog2Value);
  Serial.print(",\"timestamp\":");
  Serial.print(millis());
  Serial.println("}");
  
  delay(100); // 10Hz sampling rate
} 