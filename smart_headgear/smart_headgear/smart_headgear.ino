const int ledPin = D7;  

void setup() {
  pinMode(ledPin, OUTPUT);  
}

void loop() {
  digitalWrite(ledPin, HIGH); // Turn LED on
  delay(500);                 
  digitalWrite(ledPin, LOW);  
  delay(500);                 
}
