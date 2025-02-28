#define PIN1 31
#define PIN2 33
#define PIN3 35
#define PIN4 37
#define PIN5 39
#define PIN6 41
#define PIN7 43


void setup() {
	Serial.begin(115200);    
  pinMode(PIN1, OUTPUT);
  pinMode(PIN2, OUTPUT);
  pinMode(PIN3, OUTPUT);
  pinMode(PIN4, OUTPUT);
  pinMode(PIN5, OUTPUT);
  pinMode(PIN6, OUTPUT);
  pinMode(PIN7, OUTPUT);
}

void loop() {
  if(Serial.available() >= 3){
    char serial_received[3];
    Serial.readBytes(serial_received, 3);
    control_pin(serial_received);
  } 
}

void control_pin(char* command) {
  char first_digit = command[0];
  char second_digit = command[1];
  char action = command[2];
  
  String pin_string = String(first_digit) + String(second_digit);
  int pin_int = pin_string.toInt();

  if (action == '1') {
    digitalWrite(pin_int, HIGH);  
  } else if (action == '0') {
    digitalWrite(pin_int, LOW); 
  }
}



