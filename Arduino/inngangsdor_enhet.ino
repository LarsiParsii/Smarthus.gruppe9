#include <CircusESP32Lib.h> 

// Opperette oppkobling for CoT
char ssid[] = "Njål sin iPhone (2)"; 
char password[] =  "njalert123";
char server[] = "www.circusofthings.com";
char doorKey[] = "55";
char trackingKey_1[] = "27533";
char trackingKey_2[] = "13945";
char dingDong[] = "17423";
char token[] = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NzQ1In0.Qaa1HRun8lFNpWUQLYHew32WjxhEt9-gGFa7RoFBKNE"; 
char token_1[] = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI0OTA1In0.FqhA0PdOWJeK0jbwW6_MtgJD7rZBQD3lA8ibur2BG6Y";
char token_2[] = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NzQ1In0.Qaa1HRun8lFNpWUQLYHew32WjxhEt9-gGFa7RoFBKNE"; 
CircusESP32Lib circusESP32(server,ssid,password);

// Oppretter oppgavene
TaskHandle_t Task1;
TaskHandle_t Task2;

// Konfigurere pins
const int led1 = 26;
const int led2 = 27;

const int potPin = 34;
const int button = 35;
const int doorBell = 14;

const int A = 32;
const int B = 33;
const int C = 25;
const int D = 19;
const int E = 18;
const int F = 5;
const int G = 17;

// Kode konstanter
int code_0 = 0;
int code_1 = 0;
int code_2 = 0;
int code_3 = 0;
int inputCode = 0;
const int usercode_1 = 6351;
const int usercode_2 = 1234;

// Forskjellige andre konstanter
int potValue = 0;
int currentPot = 0;
int State = 0;
int timer = 250;
int resetTimer = 250;

// Starter prosseser og konfigurerer INN og OUT pins
void setup() {
  circusESP32.begin();
  Serial.begin(115200);
   
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(A, OUTPUT);
  pinMode(B, OUTPUT);
  pinMode(C, OUTPUT);
  pinMode(D, OUTPUT);
  pinMode(E, OUTPUT);
  pinMode(F, OUTPUT);
  pinMode(G, OUTPUT);
  pinMode(button, INPUT);
  pinMode(potPin, INPUT);
  pinMode(doorBell, INPUT);

  //Oppretter en oppgave som skal kjøres på kjerne 0
  xTaskCreatePinnedToCore(
                    Task1code,   
                    "Task1",    
                    10000,       
                    NULL,        
                    1,           
                    &Task1,      
                    0);                            
  delay(500); 

  //Oppretter en oppgave som skal kjøres på kjerne 1
  xTaskCreatePinnedToCore(
                    Task2code, 
                    "Task2",    
                    10000,       
                    NULL,       
                    1,           
                    &Task2,     
                    1);          
    delay(500); 
}

// Task1code: sjekker potmeterets stilling og viser et tall på 7-segmentet
void Task1code( void * pvParameters ){
  Serial.print("Task1 running on core ");
  Serial.println(xPortGetCoreID());
// Benytter en for(;;) for at koden skal køre hele tiden
  for(;;){

 int  buttonState = digitalRead(button);
 potValue = map(analogRead(potPin), 0, 4095, 0, 9);
  delay(100);
    switch(potValue){
// case;switch, forandrer tallet på 7-segmentet alt etter hvilken verdi potmeteret har
  case 0:
  digitalWrite(A, HIGH);
  digitalWrite(B, HIGH);
  digitalWrite(C, HIGH);
  digitalWrite(D, LOW);
  digitalWrite(E, HIGH);
  digitalWrite(F, HIGH);
  digitalWrite(G, HIGH);
  break;
  
    
  case 1:
  digitalWrite(A, LOW);
  digitalWrite(B, LOW);
  digitalWrite(C, HIGH);
  digitalWrite(D, LOW);
  digitalWrite(E, LOW);
  digitalWrite(F, LOW);
  digitalWrite(G, HIGH);
  break;

  
  case 2:
  digitalWrite(A, HIGH);
  digitalWrite(B, HIGH);
  digitalWrite(C, LOW);
  digitalWrite(D, HIGH);
  digitalWrite(E, LOW);
  digitalWrite(F, HIGH);
  digitalWrite(G, HIGH);
  break;
  
  case 3:
  digitalWrite(A, LOW);
  digitalWrite(B, HIGH);
  digitalWrite(C, HIGH);
  digitalWrite(D, HIGH);
  digitalWrite(E, LOW);
  digitalWrite(F, HIGH);
  digitalWrite(G, HIGH);
  break;
  
  case 4:
  digitalWrite(A, LOW);
  digitalWrite(B, LOW);
  digitalWrite(C, HIGH);
  digitalWrite(D, HIGH);
  digitalWrite(E, HIGH);
  digitalWrite(F, LOW);
  digitalWrite(G, HIGH);
  break;
  
  case 5:
  digitalWrite(A, LOW);
  digitalWrite(B, HIGH);
  digitalWrite(C, HIGH);
  digitalWrite(D, HIGH);
  digitalWrite(E, HIGH);
  digitalWrite(F, HIGH);
  digitalWrite(G, LOW);
  break;
  
  case 6:
  digitalWrite(A, HIGH);
  digitalWrite(B, HIGH);
  digitalWrite(C, HIGH);
  digitalWrite(D, HIGH);
  digitalWrite(E, HIGH);
  digitalWrite(F, LOW);
  digitalWrite(G, LOW);
  break;
  
  case 7:
  digitalWrite(A, LOW);
  digitalWrite(B, LOW);
  digitalWrite(C, HIGH);
  digitalWrite(D, LOW);
  digitalWrite(E, LOW);
  digitalWrite(F, HIGH);
  digitalWrite(G, HIGH);
  break;
  
  case 8:
  digitalWrite(A, HIGH);
  digitalWrite(B, HIGH);
  digitalWrite(C, HIGH);
  digitalWrite(D, HIGH);
  digitalWrite(E, HIGH);
  digitalWrite(F, HIGH);
  digitalWrite(G, HIGH);
  break;
  
  case 9:
  digitalWrite(A, LOW);
  digitalWrite(B, LOW);
  digitalWrite(C, HIGH);
  digitalWrite(D, HIGH);
  digitalWrite(E, HIGH);
  digitalWrite(F, HIGH);
  digitalWrite(G, HIGH);
  break;
}
if (currentPot != potValue){
  timer = resetTimer;
}

// Denne delen sjekker om knappen for inngangskoden blir trykket
// Dersom den blir det blir et siffer av koden angitt

if(buttonState == HIGH && State == 0){
  code_0 = potValue;
  State = 1;
  delay(500);
}else if(buttonState == HIGH && State == 1){
  code_1 = potValue;
  State = 2;
  delay(500);
}else if(buttonState == HIGH && State == 2){
  code_2 = potValue;
  State = 3;
  delay(500);
}else if(buttonState == HIGH && State == 3){
  code_3 = potValue;
  inputCode = (code_0*1000 + code_1*100 + code_2*10 + code_3);
  Serial.println(inputCode);
  if (inputCode == usercode_1){
    digitalWrite(led1, HIGH);
    circusESP32.write(trackingKey_1,1,token_1);
    delay(5000);
    digitalWrite(led1, LOW);
  }else if(inputCode == usercode_2){
     digitalWrite(led1, HIGH);
    circusESP32.write(trackingKey_2,1,token_2);
    delay(5000);
    digitalWrite(led1, LOW);
  }
  else{
    digitalWrite(led2, HIGH);
    delay(5000);
    digitalWrite(led2, LOW);
  }
  State = 0;
  inputCode = 0;
}

// Her blir ringeklokkesignlet HIGH(1) dersom noen trykker på ringeklokken
if(digitalRead(doorBell) == HIGH){
  circusESP32.write(dingDong,1,token);
}
// Timer som teller ned, når denne blir null starter deep sleep
  timer = timer -1;
  Serial.println(timer);
  if (timer <= 0){
    esp_sleep_enable_ext0_wakeup(GPIO_NUM_35, 1);
    esp_deep_sleep_start();
 } 
currentPot = potValue; 
}
}


//Denne oppgaven søker konstant etter forandringer på dørsignalet
// Dette er gjort på kjerne 1, slik at de forskellige kjernene kan kjøres sepparat.

void Task2code( void * pvParameters ){
  Serial.print("Task2 running on core ");
  Serial.println(xPortGetCoreID());

  for(;;){
    if(circusESP32.read(doorKey, token) == 1){
    digitalWrite(led1, HIGH);
    }else{
    digitalWrite(led1, LOW); 
    }
  }
}

void loop() {
  
}
