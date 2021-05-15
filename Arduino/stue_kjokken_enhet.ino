//enhet Stue/kjøkken
#include <CircusESP32Lib.h> // Biblioteket til Circus of Things


//kjerne 0 innformasjon
int SwitchStatus;
TaskHandle_t Task1; // setter navn på oppgaven til kjerne 0
const int SwitchPin = 25; // setter pinnen til bryteren
//--------------

const int LightPin = 32; // setter pinnen til lysdiode
const int TMPsensorPin = 34; // setter pinnen til temperatursensoren
const int HeatingDevice = 18; // setter pinnen til varmeelementet 

char ssid[] = "-------"; //navnet til ruteren
char password[] = "-------"; //passordet til ruteren
char server[] = "www.circusofthings.com"; // Her ligger serveren.
char token[] = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NzQ1In0.Qaa1HRun8lFNpWUQLYHew32WjxhEt9-gGFa7RoFBKNE "; //bruker nøkkel i CoT
char keyLightLivingroomKitchen[] = "12361"; // Nøkkel-informasjon om tilstanden til lysdioden
char keyTempLivingroomKitchen[] = "11649";// Nøkkel-informasjon om ønsket Temperatur fra CoT
char keyNightday[] = "4783";// Nøkkel-informasjon om Natt eller Dag fra CoT

CircusESP32Lib circusESP32(server, ssid, password); //leser nettadressen

//til Lysfunksjonen
unsigned long Interval = 15000; //tidsintervallet melom på og av for lys
unsigned long timeBefore = 0; // startverdien for tiden
int LEDState = 0; //statverdien for lysdiode

//--------------kjerne 0 program------------
//oppgaven til kjerne 0 er å kontinuelig se om bryter blir trykket inn eller ikke 
void Task1code( void * pvParameters ) {
  
  for (;;) {
     SwitchStatus = functionLightSwitch(SwitchPin);// funksjon som registrerer bryterstatus
     if (SwitchStatus == 1){
      delay (20000);// delay for at tillstanden skal holde til programmet på andre kjernen har blitt kjørt
     }
  }
}

void setup() {
  Serial.begin (115200);
  circusESP32.begin();


  xTaskCreatePinnedToCore(
    Task1code,   //funksjonen til oppgaven
    "Task1",     //navnet til oppgaven 
    10000,       //størrelsen på oppgaven
    NULL,        //parameter til kjernen
    1,           //prioriteringen til oppgaven
    &Task1,      //oppgaven sit navn hvis en vil følle med på den
    0);          //kjernen oppgaven skal foregå på
  delay(500);
}

//void loop fungerer innen kjerne 1
void loop() {
  //henting av signaler fra CoT
  //signal for ønsket temperatur i rommet
  int SignalWantedTemp = circusESP32.read(keyTempLivingroomKitchen, token);
  //signal for om det er natt eller dag
  int SignalNightDay = circusESP32.read(keyNightday, token);

  int TempReading = MeasuredTemp(TMPsensorPin); //funksjon som leser temperatur i rommet

  int signalLight = functionLightControll(SignalNightDay, Interval, SwitchStatus, LightPin);// kontrolerer lys og sender ut signal
  
  circusESP32.write(keyLightLivingroomKitchen, signalLight, token); //sender signal til CoT om lys tilstand 
  
  functionControlHeating(SignalWantedTemp, TempReading, HeatingDevice);//kontrolerer varmeelemetet
}




//------------------------FUNKSJONER------------


//function for henting av Temperatur fra TMP-sensor
int MeasuredTemp(int ChosenPin) {
  int TMPsensorPin = ChosenPin; //setter pinnen til TMP-sensoren
  pinMode (TMPsensorPin, INPUT);

  int readingFromTemp = analogRead(TMPsensorPin); //Leser verdi fra TMP sensor
  float Volts = (readingFromTemp * 5.0) / 1023.0; // omdanner verdien til en volt verdi
  float temp = (Volts - 0.5) * 100; // omdanner verdien fra volt til temperatur i celcius
  return temp;
}

//------------------------------------------
//function for start og stopp av ovn basert på ønsket temperatur
void functionControlHeating(int WantedTemp, int ReadTemp, int ChosenPin) {
  int HeatingDevice = ChosenPin;
  pinMode (HeatingDevice, OUTPUT);
  //hvis ønsket temperatur er mindre en Lest temperatur skal ovnen slå seg på
  if (WantedTemp > ReadTemp) {
    digitalWrite (HeatingDevice, HIGH);
  }
  //hvis ønsket temperatur er større eller lik den leste temperaturen skal ovnen være av
  else if (WantedTemp <= ReadTemp) {
    digitalWrite (HeatingDevice, LOW);
  }
}

//------------------------------------------
//registerer om knapp er trykket inn
int functionLightSwitch(int ChosenPin) {
  pinMode (ChosenPin, INPUT);
  int ReadingFromSwitch = digitalRead (ChosenPin);
  return ReadingFromSwitch;
}

//--------------------------------------------
int functionLightControll(int DayNight, unsigned long interval, int ButtonState, int ChosenPin) {
  //funksjon for å registrere bryter status og bruke denne til å
  //sette lyset på i en ønsket periode
  // ser også på om det er dag eller nattsignal og justerer så lysstyrken
  const int Lightpin = ChosenPin; //pinnen lyset er koblet til
  //ledc-verdiene
  const int Channel = 2;
  const int Frequency = 5000;
  const int DutyCycle = 8;
  //------
  int SignalOut; //signal som sender om lys er av eller på
  int LightLevel; //lysnivået til lysdioden
  int LightMax = 255;// lysdiode helt på
  ledcSetup(Channel, Frequency, DutyCycle); //PMW funksjonaliteter
  ledcAttachPin(Lightpin, Channel);// setter hvilken kanal pinnen skal høre til
  noInterrupts();//gjør at tidssensetiv kode ikke blir avbrytt
  unsigned long timeCurrent = millis(); //henter tiden
  interrupts();//slår på bakgrunns kode igjen
  //if (Tracking == 0){return;}
  //justerer lystyrken til lysdioden basert på om det er nattt eller dag
  if (DayNight == 0) {
    LightLevel = LightMax; // på dagtid står lyset helt på
  }
  else if (DayNight == 1) {
    LightLevel = LightMax / 2; //nattsenking gjør at lysstyrken blir halvert
  }

  //ser om tidsintervallet er stort nokk
  if (timeCurrent - timeBefore >= interval) {
    LEDState = 0;//setter tilstanden på led til 0
    SignalOut = 0;
  }

  //når signal for at knappen er trykket er høy,
  //vil lysverdien gå fra 0 til verdi bestemt av natt/dag
  if (ButtonState == 1) {
    LEDState = LightLevel;
    timeBefore = timeCurrent;//setter ny start tid
    SignalOut = 1;
  }
  ledcWrite (Channel, LEDState);//setter lysverdien
  return SignalOut;
}
