// Made by Ivan Nestorovski
// This code is designed for position control of N20 DC Motors.
// You can adjust the precision and usage according to your project needs.

#include <AFMotor.h> // Include the Adafruit Motor Shield library

// Initialize an array of AF_DCMotor objects to control up to 4 motors
AF_DCMotor motors[4] = {AF_DCMotor(1), AF_DCMotor(2), AF_DCMotor(3), AF_DCMotor(4)};
// Define the analog input pins connected to the potentiometers
int potPins[4] = {A0, A1, A2, A3};

// Variables to store timing information for control intervals
unsigned long previousMillis = 0;
const long interval = 20; // Control interval in milliseconds
// Arrays to store target positions and last error values for each motor
int targets[4] = {0, 0, 0, 0};
int lastErrors[4] = {0, 0, 0, 0};
// Tolerance for position error
int tolerance = 10;
// Flags to manage new commands from serial input
bool newCommandAvailable = false;
int newTargetMotorIndex = 0;
int newTargetValue = 0;

void setup() {
 Serial.begin(9600); // Start serial communication at 9600 baud rate
 // Initialize motors and read initial potentiometer values
 for (int i = 0; i < 4; i++) {
  motors[i].setSpeed(255); // Set motor speed to maximum
  int initialPotValue = analogRead(potPins[i]); // Read initial potentiometer value
  // Print initial potentiometer values for each motor to the serial monitor
  Serial.print("Initial potentiometer value for motor ");
  Serial.print(i + 1);
  Serial.print(": ");
  Serial.println(initialPotValue);
 }
}

void loop() {
 unsigned long currentMillis = millis(); // Get the current time

 // Check if there is any serial input available
 if (Serial.available()) {
  char c = Serial.read(); // Read the next character from serial input
  // If the character is a digit, process it as part of a command
  if (c >= '0' && c <= '9') {
   if (!newCommandAvailable) {
    // If a new command is not available, build the motor index
    newTargetMotorIndex = newTargetMotorIndex * 10 + c - '0';
   } else {
    // If a new command is available, build the target value
    newTargetValue = newTargetValue * 10 + c - '0';
   }
  } else if (c == ':') {
   // If the character is a colon, mark that a new command is available
   newCommandAvailable = true;
  } else if (c == '\n') {
   // If the character is a newline, process the completed command
   if (newTargetMotorIndex >= 1 && newTargetMotorIndex <= 4) {
    // Set the target position for the specified motor
    targets[newTargetMotorIndex - 1] = newTargetValue;
   }
   // Reset command processing variables
   newCommandAvailable = false;
   newTargetMotorIndex = 0;
   newTargetValue = 0;
  }
 }

 // Control loop for each motor
 for (int i = 0; i < 4; i++) {
  // Check if it's time to update the motor control
  if (currentMillis - previousMillis >= interval && targets[i] != 0) {
   previousMillis = currentMillis; // Update the previousMillis variable

   int potValue = analogRead(potPins[i]); // Read the current potentiometer value
   int error = targets[i] - potValue; // Calculate the position error

   // If the error is greater than the tolerance, adjust motor direction
   if (abs(error) > tolerance) {
    if (error < 0 && error < lastErrors[i]) {
     motors[i].run(FORWARD); // Run motor forward if error is negative and decreasing
    } else if (error > 0 && error > lastErrors[i]) {
     motors[i].run(BACKWARD); // Run motor backward if error is positive and increasing
    }
   } else {
    // If the error is within tolerance, stop the motor and send an acknowledgement
    motors[i].run(RELEASE);
    Serial.print("ack:"); // Acknowledgement prefix
    Serial.println(i + 1); // Send motor index
    targets[i] = 0; // Reset the target position
   }

   lastErrors[i] = error; // Update the last error value
  }
 }
}
