/* Proofing Box Temperature controller using
 *  DS18S20 Temperature Sensor
 *  KOOKYE 2-channel relay module
 *
 * Jabez McClelland jabezmcc1@yahoo.com
    
*/
#include <OneWire.h>
int inPin=10; // define D10 as input pin connecting to DS18S20 S pin
int incomingByte = 0;
OneWire ds(inPin); 

//relay connections.  Actually only need ch 1.
int IN1 = 2;
int IN2 = 3;

#define ON   0
#define OFF  1

// float setPoint_F = 80.0;  //Use these for hard coding set point 
// float setPoint = (setPoint_F-32.0)*5.0/9.0;
float setPoint = 26.67;
float marginC = 0.5;

void setup(void) {
  pinMode(13, OUTPUT); 
  digitalWrite(13, HIGH);  //Use pin 13 as power for the DS18S20
  Serial.begin(9600);
  relay_init();//Initialize the relay
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
    relay_SetStatus(ON, OFF);
  }
  if (tempstr.toFloat() > setPoint + marginC/2.)
  {
    relay_SetStatus(OFF, OFF);
  }
}

void relay_init(void)//initialize the relay
{
  //set all the relays OUTPUT
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  relay_SetStatus(OFF, OFF); //turn off all the relay
}
//set the status of relays
void relay_SetStatus( unsigned char status_1,  unsigned char status_2)
{
  digitalWrite(IN1, status_1);
  digitalWrite(IN2, status_2);
}
