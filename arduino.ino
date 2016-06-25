const int motorPin = 5;
const int actTime = 2000;

int incomingByte;      // a variable to read incoming serial data into

void setup() {
  // initialize serial communication:
  Serial.begin(9600);
  // initialize the LED pin as an output:
  pinMode(motorPin, OUTPUT);
}

void loop() {
  // see if there's incoming serial data:
  if (Serial.available() > 0) {
    // read the oldest byte in the serial buffer:
    incomingByte = Serial.read();

    if (incomingByte == 's') {
      analogWrite(motorPin, 255);
      delay(actTime);
      analogWrite(motorPin, 0);
    }

  }
}
