#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <WiFi.h>
#include <WebServer.h>
#include <EEPROM.h>

#define CAP_SEND_PIN D7             // Digital pin to charge the pad (adjust as needed)
#define CAP_RECEIVE_PIN A0         // Analog pin to read capacitance (ADC-capable)
#define LED_PIN 10                 // XIAO ESP32 onboard LED is GPIO 10

#define CALIBRATION_SAMPLES 50
#define ANALOG_CAP_THRESHOLD 500
#define IMPACT_THRESHOLD 20.0
#define IMPACT_COOLDOWN_MS 1000
#define MAX_IMPACTS 100
#define EEPROM_SIZE 512

Adafruit_MPU6050 mpu;
WebServer server(80);

int capBaseline = 0;
int impactCount = 0;
unsigned long lastImpactTime = 0;

struct ImpactData {
  unsigned long timestamp;
  float magnitude;
  int capDeviation;
};
ImpactData impactHistory[MAX_IMPACTS];

const char* ssid = "MAKERSPACE";
const char* password = "12345678";

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Smart Headgear Monitor</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      margin: 0;
      padding: 20px;
      background: #f5f5f5;
      color: #333;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      background: white;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
      color: #2196F3;
      text-align: center;
      margin-bottom: 30px;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    .stat-card {
      background: #fff;
      padding: 15px;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
      text-align: center;
      border: 1px solid #e0e0e0;
    }
    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #2196F3;
      margin: 10px 0;
    }
    .stat-label {
      color: #666;
      font-size: 14px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
      background: white;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #e0e0e0;
    }
    th {
      background: #f8f9fa;
      font-weight: 600;
      color: #444;
    }
    tr:hover {
      background: #f5f5f5;
    }
    .timestamp {
      color: #666;
      font-size: 0.9em;
    }
    .magnitude {
      font-weight: 500;
      color: #2196F3;
    }
    .cap-diff {
      color: #4CAF50;
    }
    .status {
      text-align: center;
      margin-top: 20px;
      color: #666;
      font-size: 0.9em;
    }
    @media (max-width: 600px) {
      .container {
        padding: 10px;
      }
      .stats {
        grid-template-columns: 1fr;
      }
      th, td {
        padding: 8px;
        font-size: 14px;
      }
    }
  </style>
  <script>
    let maxMagnitude = 0;
    let totalImpacts = 0;
    let totalMagnitude = 0;

    function formatTime(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    }

    function updateStats() {
      document.getElementById('total-impacts').textContent = totalImpacts;
      document.getElementById('max-magnitude').textContent = maxMagnitude.toFixed(2);
      document.getElementById('avg-magnitude').textContent = 
        totalImpacts > 0 ? (totalMagnitude / totalImpacts).toFixed(2) : '0.00';
    }

    async function fetchData() {
      try {
        const res = await fetch('/data');
        const data = await res.json();
        
        // Reset stats
        maxMagnitude = 0;
        totalImpacts = data.length;
        totalMagnitude = 0;
        
        // Clear existing table rows
        const table = document.querySelector('table');
        while (table.rows.length > 1) {
          table.deleteRow(1);
        }
        
        // Add new data
        data.forEach((impact, index) => {
          const row = table.insertRow();
          row.innerHTML = `
            <td>${index + 1}</td>
            <td class="timestamp">${formatTime(impact.timestamp)}</td>
            <td class="magnitude">${impact.magnitude.toFixed(2)} m/s²</td>
            <td class="cap-diff">${impact.capDeviation}</td>
          `;
          
          // Update stats
          if (impact.magnitude > maxMagnitude) maxMagnitude = impact.magnitude;
          totalMagnitude += impact.magnitude;
        });
        
        updateStats();
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    }

    // Initial fetch
    fetchData();
    
    // Update every 5 seconds
    setInterval(fetchData, 5000);
  </script>
</head>
<body>
  <div class="container">
    <h1>Smart Headgear Monitor</h1>
    
    <div class="stats">
      <div class="stat-card">
        <div class="stat-value" id="total-impacts">0</div>
        <div class="stat-label">Total Impacts</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="max-magnitude">0.00</div>
        <div class="stat-label">Max Magnitude (m/s²)</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="avg-magnitude">0.00</div>
        <div class="stat-label">Avg Magnitude (m/s²)</div>
      </div>
    </div>

    <table>
      <tr>
        <th>#</th>
        <th>Time</th>
        <th>Magnitude</th>
        <th>Cap Difference</th>
      </tr>
    </table>

    <div class="status">
      Auto-refreshing every 5 seconds
    </div>
  </div>
</body>
</html>
)rawliteral";

void calibrateCapacitiveSensor() {
  pinMode(CAP_SEND_PIN, OUTPUT);
  capBaseline = 0;
  for (int i = 0; i < CALIBRATION_SAMPLES; i++) {
    digitalWrite(CAP_SEND_PIN, HIGH);
    delayMicroseconds(100);
    digitalWrite(CAP_SEND_PIN, LOW);
    capBaseline += analogRead(CAP_RECEIVE_PIN);
    delay(10);
  }
  capBaseline /= CALIBRATION_SAMPLES;
  Serial.print("Cap baseline: "); Serial.println(capBaseline);
}

void recordImpact(float magnitude, int capDeviation) {
  if (impactCount < MAX_IMPACTS) {
    impactHistory[impactCount++] = {millis(), magnitude, capDeviation};
    EEPROM.write(0, impactCount);
    EEPROM.commit();
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);

  EEPROM.begin(EEPROM_SIZE);
  impactCount = EEPROM.read(0);
  if (impactCount > MAX_IMPACTS) impactCount = 0;

  // Init MPU6050
  if (!mpu.begin()) {
    Serial.println("MPU6050 not found");
    while (1) delay(10);
  }
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  calibrateCapacitiveSensor();

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500); Serial.print(".");
  }
  Serial.println("\nWiFi connected: " + WiFi.localIP().toString());

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html", index_html);
  });

  server.on("/data", HTTP_GET, []() {
    String json = "[";
    for (int i = 0; i < impactCount; i++) {
      json += String("{\"timestamp\":") + impactHistory[i].timestamp +
              ",\"magnitude\":" + impactHistory[i].magnitude +
              ",\"capDeviation\":" + impactHistory[i].capDeviation + "}";
      if (i < impactCount - 1) json += ",";
    }
    json += "]";
    server.send(200, "application/json", json);
  });

  server.begin();
}

void loop() {
  server.handleClient();

  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  float mag = sqrt(a.acceleration.x * a.acceleration.x +
                   a.acceleration.y * a.acceleration.y +
                   a.acceleration.z * a.acceleration.z);

  digitalWrite(CAP_SEND_PIN, HIGH);
  delayMicroseconds(100);
  digitalWrite(CAP_SEND_PIN, LOW);
  int capVal = analogRead(CAP_RECEIVE_PIN);
  int capDiff = abs(capVal - capBaseline);

  if (mag > IMPACT_THRESHOLD && capDiff > ANALOG_CAP_THRESHOLD) {
    unsigned long now = millis();
    if (now - lastImpactTime > IMPACT_COOLDOWN_MS) {
      Serial.print("Impact detected! Mag: "); Serial.print(mag);
      Serial.print(" Cap Diff: "); Serial.println(capDiff);
      digitalWrite(LED_PIN, HIGH);
      delay(100);
      digitalWrite(LED_PIN, LOW);
      lastImpactTime = now;
      recordImpact(mag, capDiff);
    }
  }
}
