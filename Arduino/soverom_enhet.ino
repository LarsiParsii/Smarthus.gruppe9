#include <CircusESP32Lib.h> // Biblioteket til Circus of Things
#include <Servo.h> // Bibloteket til Servostyring
Servo servo; // setter navn på bibloteket
int i; // startverdien til servo

char ssid[] = ""; //navnet til ruteren
char password[] = ""; //passordet til ruteren
char server[] = "www.circusofthings.com"; // Her ligger serveren.
char token[] = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI0OTA1In0.FqhA0PdOWJeK0jbwW6_MtgJD7rZBQD3lA8ibur2BG6Y"; //bruker nøkkel i CoT
char keyServo[] = "8746"; // Nøkkel-informasjon om konsollet for styring av Servo hos CoT
char keyMotor[] = "20023";// Nøkkel-informasjon om konsollet for styring av Motor hos CoT
char keyTracking[] = "27533";// Nøkkel-informasjon om konsollet for styring av Lys hos CoT
//char keyNightday[] = "";// Nøkkel-informasjon om konsollet for styring av NattDag hos CoT
char keyDoorbell[] = "30614";// Nøkkel-informasjon om konsollet for styring av ringeklokke hos CoT
char keyTemp[] = "25341";// Nøkkel-informasjon om konsollet for styring av Temperatur hos CoT

CircusESP32Lib circusESP32(server, ssid, password); //leser nettadressen

void setup() {
  Serial.begin (115200);
  circusESP32.begin();
}

void loop() {
  //henting av signaler fra CoT
  int SignalServo = circusESP32.read(keyServo, token);
  int SignalTracking = circusESP32.read(keyTracking, token);
  int SignalMotor = circusESP32.read(keyMotor, token);
  int SignalDoorBell = circusESP32.read(keyDoorbell, token);
  int SignalWantedTemp = circusESP32.read(keyTemp, token);

  // henting av interne verdier
  int Measuredtemp = MeasuredTemp();
  int LightValue = functionReadLight();
  int LightSwitch = functionLightSwitch();
  //------------------------------
  //------------------------------
  //kjøring av functioner og printing av verdier
  functionRunMotorManually(SignalMotor);

  functionRunMotorAuto (SignalWantedTemp, Measuredtemp, SignalMotor);

  functionRunServoManually(SignalServo);
  
  functionRunServoAuto(SignalWantedTemp, Measuredtemp, SignalServo);
  
  functionPanelOven(SignalWantedTemp, Measuredtemp);
  
  functionDoorBell (SignalDoorBell);
  
  functionControllLight(LightSwitch, LightValue, SignalTracking);

  Serial.println("Servo" + String(SignalServo));
  Serial.println("Motor" + String (SignalMotor));
  Serial.println( "Wanted Temp" + String (SignalWantedTemp));
  Serial.println("Read Temp" + String (Measuredtemp));
  Serial.println("Door" + String(SignalDoorBell));
}


//--------------------functionER--------------------

//function for kjøring av motor
void functionRunMotorManually (int MotorSig) {
  const int MotorSpeedPin = 26; // utgang til fartsverdi
  const int MotorHighPin = 33; // utgang til motor av på
  // De tre forskjellige hastighetene til motoren
  const int SpeedHigh = 30;
  const int SpeedMed = 20;
  const int SpeedLow = 15;
  // elementene til ledcsetup
  const int Channel = 1;
  const int Frequency = 50;
  const int DutyCycle = 8;

  pinMode (MotorSpeedPin, OUTPUT);
  pinMode (MotorHighPin, OUTPUT);
  ledcSetup(Channel, Frequency, DutyCycle);
  ledcAttachPin(MotorSpeedPin, Channel); //designert pinne til hastighetsstyring
  //--------styring av motor--------------
  digitalWrite (MotorHighPin, HIGH); //motor står på
  //ser om styring er i auto eller manuell.
  //Hvis MotorSig er større en 9, betyr dette at motoren skal kjøre automatisk.
  //Derfor vil denne functionen avsluttes
  if (MotorSig > 9) {
    return;
  }
  // Bestemmer farten på mototen ut fra signalet som kommer inn
  if (MotorSig == 1 ) {
    ledcWrite (Channel, SpeedLow);
  }
  else if (MotorSig == 2) {
    ledcWrite (Channel, SpeedMed);
  }
  else if (MotorSig == 3) {
    ledcWrite (Channel, SpeedHigh);
  }
}
//function for Henting av Temperatur fra TMP-sensor
int MeasuredTemp() {
  int TMPsensorPin = 34; //setter pinnen til TMP-sensoren
  pinMode (TMPsensorPin, INPUT);

  int readingFromTemp = analogRead(TMPsensorPin); //Leser verdi fra TMP sensor
  float Volts = (readingFromTemp * 5.0) / 1023.0; // omdanner verdien til en volt verdi
  float temp = (Volts - 0.5) * 100; // om danner verdien fra volt til temperatur i celcius
  return temp;
}
//function for kjøring av servo til åpening av vindu automatisk
//basert på ønsket temperatur fra bruker og lest temperatur fra TMP-sensor
void functionRunServoAuto (int WantedTemp, int ReadTemp, int ServoSig) {
  const int ServPin = 2;
  int DiffereceInTemp;
  int servoDegree;

  servo.attach (ServPin); //setter pinnen servoen skal ta verdien fra

  if (ServoSig == 81) { //sjekker at servo skal kjøre automatisk
    DiffereceInTemp = ReadTemp - WantedTemp; //finner differiansen i temperatur
    // Setter antall grader servoen skal stå på, basert på forskjellen mellom ønsket og lest temperatur
    if (DiffereceInTemp >= 5) {
      servoDegree = 80;
    }
    else if (DiffereceInTemp >= 2 && DiffereceInTemp < 5 ) {
      servoDegree = 45;
    }
    else if (DiffereceInTemp < 2) {
      servoDegree = 0;
    }
    //kjører servoen opp/ned til bestemt verdi en grad om gangen
    if (i < servoDegree) {
      for (i = 0; i != servoDegree; i ++) {
        servo.write (i);
        delay (20);
      }
    }
    else if (i > servoDegree) {
      for (i = 80; i != servoDegree; i --) {
        servo.write (i);
        delay (20);
      }
    }
  }
}
//function for kjøring av servo til åpening av vindu manuelt
void functionRunServoManually(int ServoSignal) {
  const int ServPin = 2;
  //ser om sevo sin verdi overgår 80 grader.
  //hvis den gjør det skal functionen avbrytes
  if (ServoSignal >= 81) {
    return;
  }
  //Ser om servosignalet er blitt forandret siden siste loop
  //har det blitt forandret vil functionen avbrytes
  if (i == ServoSignal) {
    return;
  }
  servo.attach (ServPin);//setter pinnen servoen skal ta verdien fra
  //ser om forrige servosignal er større eller mindre en det nåværende servosignalet
  if (i < ServoSignal) {
    //teller opp gradene på servosignalet til det er likt ønsket verdi
    for (i = 0; i != ServoSignal; i ++) {
      servo.write (i);
      delay (20);
    }
  }
  else if (i > ServoSignal){
    //teller opp gradene på servosignalet til det er likt ønsket verdi
    for (i = 80; i != ServoSignal; i --) {
      servo.write (i);
      delay (20);
    }
  }
}
//function kjøring av ringeklokke basert på av og på signal fra CoT
//setter signal for ringeklokke tilbake til 0
void functionDoorBell (int DoorBellSig) {
  // elementene til ledcsetup
  const int Channel = 3;
  const int Frequency = 8000;
  const int DutyCycle = 12;
  ledcSetup(3, 8000, 12);
  ledcAttachPin(32, 3);
  //tonen som spiller når signal for ringeklokke er 1
  if (DoorBellSig == 1) {
    ledcWriteTone(3, 500);
    delay(350);
    ledcWriteTone(3, 0);
    delay(30);
    ledcWriteTone(3, 400);
    delay(700);
    ledcWriteTone(3, 0);
  }
  else if (DoorBellSig == 0) {
    return;
  }
  circusESP32.write(keyDoorbell, 0, token); //resetter signalet for ringeklokke
}

//function for start og stopp av ovn basert på ønsket temperatur
void functionPanelOven(int WantedTemp, int ReadTemp) {
  const int HeatingDevice = 18;
  pinMode (HeatingDevice, OUTPUT);
  //hvis ønsket temperatur er mindre en Lest temperatur skal ovnen slå seg på
  if (WantedTemp < ReadTemp) {
    digitalWrite (HeatingDevice, HIGH);
  }
  //hvis ønsket temperatur er større eller lik den leste temperaturen skal ovnen være av
  else if (WantedTemp >= ReadTemp) {
    digitalWrite (HeatingDevice, LOW);
  }
}

//function for om bryter er av eller på
int functionLightSwitch() {
  const int SwitchPin = 25;
  pinMode (SwitchPin, INPUT);
  int ReadingFromSwitch = digitalRead (SwitchPin);
  return ReadingFromSwitch;
}

//function for lesing av lysstyrke fra photoresistor og omgjøring til en prosentandel
int functionReadLight() {
  const int LightSensorPin = 4;
  int LightInn = analogRead(LightSensorPin); //leser verdien fra lyssensoren
  //omgjør verdien fra lyssensoren til en prosentandel
  int LightInPercent = (LightInn * 100) / 4095;
  return LightInPercent;
}

// function for styring av lyset på rommet ut fra eksisterende lystyrke
void functionControllLight(int Switch, int PercentLight, int Tracking){
  const int Light = 32;
  const int Channel = 2;
  const int Frequency = 5000;
  const int DutyCycle = 8;
  pinMode (Light, OUTPUT);
  
  ledcSetup(Channel, Frequency, DutyCycle);
  ledcAttachPin(Light, Channel);
  //Sjekker signal fra CoT som viser om personene er inne i huset 
  //hvis 0 er personen ikke tilstede og funksjonen avbrytes
  if (Tracking == 0){
    return;
  }
  if (Switch == 1) {
    int LightInnRoom = 100 - PercentLight;
    LightInnRoom = (LightInnRoom * 255) / 100;
    ledcWrite (Channel, LightInnRoom);
  }
}

//function for kjøring av motor automatisk
void functionRunMotorAuto (int WantedTemp, int ReadTemp, int MotorSig) {
  const int MotorSpeedPin = 26; // utgang til fartsverdi
  const int MotorHighPin = 33; // utgang til motor av på
  // De tre forskjellige hastighetene til motoren
  const int SpeedHigh = 30;
  const int SpeedMed = 20;
  const int SpeedLow = 15;
  // elementene til ledcsetup
  const int Channel = 1;
  const int Frequency = 50;
  const int DutyCycle = 8;
  int DiffereceInTemp;

  pinMode (MotorSpeedPin, OUTPUT);
  pinMode (MotorHighPin, OUTPUT);
  ledcSetup(Channel, Frequency, DutyCycle);
  ledcAttachPin(MotorSpeedPin, Channel); //designert pinne til hastighetsstyring
  //--------styring av motor--------------
  digitalWrite (MotorHighPin, HIGH); //motor står på
  //ser om styring er i auto eller manuell.
  //Hvis MotorSig er mindre en 10, betyr dette at motoren skal kjøre manuelt.
  //Derfor vil denne functionen avsluttes
  if (MotorSig < 10) {
    return;
  }

  DiffereceInTemp = ReadTemp - WantedTemp; //finner differiansen i temperatur
  // Setter hastigheten motoren skal ha, basert på forskjellen mellom ønsket og lest temperatur
  //hvis forskjellen er større eller lik 5 grader settes motoren på høy hastighet
  if (DiffereceInTemp >= 5) {
    ledcWrite (Channel, SpeedHigh);
  }
  //hvis forskjellen er mellom 2 og 5 kjører motoren på middels hastighet
  else if (DiffereceInTemp >= 2 && DiffereceInTemp < 5 ) {
    ledcWrite (Channel, SpeedMed);
  }
  //hvis forskjellen er mellom 0 og 2 kjører motoren på lav hastighet
  else if (DiffereceInTemp > 0 && DiffereceInTemp < 2) {
    ledcWrite (Channel, SpeedLow);
  }
  //hvis forskjellen er 0 eller mindre står motoren i ro
  else if (DiffereceInTemp <= 0){
    ledcWrite (Channel, 0);
  }
}
