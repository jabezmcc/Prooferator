/* Proofing Box Temperature controller using
 *  DS18S20 Temperature Sensor
 *  HW-482 relay module
 *
 * Jabez McClelland jabezmcc1@yahoo.com
 * Modified 6/8/2024 for new setup.
    
*/
#include <OneWire.h>
int tempinPin=11; // define D11 as input pin connecting to DS18S20 S pin
int pwrPin=12; //Use pin 12 as power for the DS18S20.
int relayPin=8; // Use pin 8 for relay control
int gndPin=7; //Use pin 7 as GND for LEDs
int pwrLEDPin=6; //Use pin 6 for power LED
int onLEDPin=5; //Use pin 5 for relay ON LED

// set up DS18S20
int incomingByte = 0;
OneWire ds(tempinPin); 

// float setPoint_F = 80.0;  //Use these for hard coding set point 
// float setPoint = (setPoint_F-32.0)*5.0/9.0;
float setPoint = 27.22;
float marginC = 0.5;

void setup(void) {
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);
  pinMode(pwrPin, OUTPUT); 
  digitalWrite(pwrPin, HIGH);  
  pinMode(gndPin, OUTPUT); 
  digitalWrite(gndPin, LOW);
  pinMode(pwrLEDPin, OUTPUT); 
  digitalWrite(pwrLEDPin, HIGH);
  pinMode(onLEDPin, OUTPUT); 
  digitalWrite(onLEDPin, LOW);
   
  Serial.begin(9600);
}
 
void loop(void) {
  int HighByte, LowByte, TReading, SignBit, Tc_100, Whole, Fract;
  byte i;
  byte present = 0;
  byte data[12];
  byte addr[8];
  String tempstr = "";
 
  if ( !ds.search(addr)) {
      ds.reset_search();
      return;
  }
  // Retrieve temperature reading and write to serial port
  ds.reset();
  ds.select(addr);
  ds.write(0x44,1); 
  delay(1000); //Check temp once per second 
  present = ds.reset();
  ds.select(addr);    
  ds.write(0xBE);  
  for ( i = 0; i < 9; i++) { 
    data[i] = ds.read();
  }
  LowByte = data[0];
  HighByte = data[1];
  TReading = (HighByte << 8) + LowByte;
  SignBit = TReading & 0x8000;  
  if (SignBit)
  {
    TReading = (TReading ^ 0xffff) + 1;
  }
  Tc_100 = (6 * TReading) + TReading / 4; 
  Whole = Tc_100 / 100; 
  Fract = Tc_100 % 100;
  if (SignBit)
  {
     Serial.print("-");
     tempstr += "-";
  }
  Serial.print(Whole);
  tempstr += String(Whole);
  Serial.print(".");
  tempstr +=".";
  if (Fract < 10)
  {
     Serial.print("0");
     tempstr += "0";
  }
  Serial.print(Fract);
  tempstr += String(Fract);
  Serial.print("\n");
  
  // Compare temp to setpoint and switch relay accordingly
  if (tempstr.toFloat() <= setPoint - marginC/2.)
  {
    digitalWrite(relayPin, HIGH);
    digitalWrite(onLEDPin, HIGH);
  }
  if (tempstr.toFloat() > setPoint + marginC/2.)
  {
    digitalWrite(relayPin, LOW);
    digitalWrite(onLEDPin, LOW);
  }
}
