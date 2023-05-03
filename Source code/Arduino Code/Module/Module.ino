int pin2count = 0;
int pin3count = 0;
bool interruptOccurred = false;
unsigned long lastSecond = 0;

// ___________________________________________________________________________
//
//                             Initial Setup
// ___________________________________________________________________________

void setup()
{
  Serial.begin(9600);   // comspec 96,N,8,1 (baud rate) 
  attachInterrupt(0, pin2event, FALLING);  // Geiger event on pin 2 triggers interrupt
  attachInterrupt(1, pin3event, FALLING);  // Geiger event on pin 3 triggers interrupt
}

// ___________________________________________________________________________
//
//                               Main loop
// ___________________________________________________________________________

void loop()
{
  if (millis() - lastSecond >= 1000) { // every second
    lastSecond = millis();
    Serial.println(String("Mod-1 ") + pin2count + String(" ") + pin3count);
    pin2count = 0;
    pin3count = 0;
  }
}

// ___________________________________________________________________________
//
//                               Event Set
// ___________________________________________________________________________

void pin2event()
{
  pin2count++;
}

void pin3event()
{
  pin3count++;
}
