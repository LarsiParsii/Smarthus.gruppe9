#include <LiquidCrystal.h>
#include <CircusESP32Lib.h> 
#define inputCLK 34
#define inputDT 35
#define inputSW 32
#define backLight 25

// Starter med CoT informasjonen 
char ssid[] = "Njål sin iPhone (2)"; 
char password[] =  "njalert123";
char server[] = "www.circusofthings.com";

// Dette er signalene som er felles mellom alle brukerene
char doorKey[] = "55";
char bathroomKey[] = "10990";
char kitchenKey[] = "3344";
char livingroomKey[] = "17737";

// Dette er signalene som til et enkelt konsoll
char bookingKey[] = "15685";
char windowKey[] = "8746"; 
char tempKey[] = "25341";
char fanKey[] = "20023";

// Her blir alle sporings signalene hentet inn, de blir brukt for å sjekke
//hvem som er hjemme lenger nede i koden
char trackingKey_1[] = "27533";
char trackingKey_2[] = "28655";

// De forskjellige tokens som ble brukt under dette prosjektet
char token_1[] = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI0OTA1In0.FqhA0PdOWJeK0jbwW6_MtgJD7rZBQD3lA8ibur2BG6Y";
char token_2[] = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI2MTg4In0.SrE-Gnlav_MVEO8Tv54Leg0j5Sec7WmS18ZvAvXiLBU";
char tokenMain[] = "eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NzQ1In0.Qaa1HRun8lFNpWUQLYHew32WjxhEt9-gGFa7RoFBKNE";
CircusESP32Lib circusESP32(server,ssid,password);

// Navnene til de forskjellige beboerene
char user1Name[] = "Lars";
char user2Name[] = "Dennis";
char user3Name[] = "Per";
char user4Name[] = "Paal";
char user5Name[] = "Espen";
char user6Name[] = "Askeladden";

// Konfigurerer LCD- skjermen, det ene konsollet benyttet seg av en I2C tilkobling
// Dette oppsettet er for en standard 16-pins skjerm
LiquidCrystal lcd(19, 23, 18, 17, 16, 15);

// Oppretter variabelene som tilhører rotary encoderen
 int counter = 0; 
 int stilling = 0;
 int currentStateCLK;
 int previousStateCLK; 
 int state;
 int menu = 0;
 int State = 0;
 int maxValue = 16;
 const int mainMax = 17;
 String encdir ="";

// Disse variabelene blir benyttet når brukeren av konsollet skal legge inn
// en spesifisert booking
 int fromTimeHour = 0;
 int fromTimeMinutes = 0;
 int tooTimeMinutes = 0;
 int tooTimeHour = 0;
 int bookingSignal;
 int guestCounter = 0;

 // Diverse variabler
 int tempGoal = 0;
 int tempVar = 22;
 int fanSpeed;
 int windowAngle;
 int sek = 1;

 // Timeren som blir brukt for å få konsollet i deep sleep
 int timer = 10000;
 int timerReset = 25000;
 
 // Disse variabelene forteller om de forskjellige rommene er ledige eller ikke
 int bathroomState = 0;
 int livingroomState = 0;
 int kitchenState = 0;

 // Disse variabelene forteller om de forskjellige brukerene er hjemme
 int user1State = 0;
 int user2State = 0;

// Dette er forskjellige tegn som blir benyttet av LCD skjermen
// Dette blir gjort fordi LCD-skjermen har et begrenset utvalg av tegn
// men den har muligheten for å legge inn "custom-characters"
 byte arrow[8] = {
  B00000,
  B00100,
  B00110,
  B11111,
  B00110,
  B00100,
  B00000,
 };
  byte dot[8] = {
  B00110,
  B01001,
  B01001,
  B00110,
  B00000,
  B00000,
  B00000,
 };
 byte backArrow[8] = {
  B00000,
  B00100,
  B01100,
  B11111,
  B01101,
  B00101,
  B00001, 
};




 void setup() {  

// Ganske standard pinMode
pinMode (inputSW, INPUT);
pinMode (inputCLK,INPUT);
pinMode (inputDT,INPUT); 
pinMode (backLight, OUTPUT);
previousStateCLK = digitalRead(inputCLK);

//Starter diverse funksjoner
Serial.begin (115200);
circusESP32.begin();
lcd.begin(16, 2);

// Oppretter "custom characters"
lcd.createChar(1, arrow);
lcd.createChar(2, backArrow);
lcd.createChar(4, dot);

//Printer en startmelding og skrur på backlight
lcd.print("Welcome!");
digitalWrite(backLight, HIGH);
delay(2000);
lcd.clear();
stilling = 1;
 } 


 
void loop() { 
  
// Dette er funksjonen som sjekker verdien til rotary encoderen
currentStateCLK = digitalRead(inputCLK); 
 if (currentStateCLK != previousStateCLK){
   if (digitalRead(inputDT) != currentStateCLK) { 
       counter = counter -1;
       stilling = counter/2;
       timer = timerReset;
       lcd.clear();
     } else {
       counter = counter + 1;
       stilling = counter/2;
       timer = timerReset;
       lcd.clear();
     }
     Serial.print(" -- Value: ");
     Serial.println(stilling);
     
   } if (digitalRead(inputSW) != HIGH){
    state = counter/2;
    Serial.print("Sate: ");
    Serial.println(state);
    lcd.clear();
    delay(100);
 }
 // Her blir grensesnittene til rotary encoderen opprettet
  if (counter > maxValue){
     counter= 0;
  } if (counter < 0){
     counter = maxValue + 1;
  } else {
    previousStateCLK = currentStateCLK; 
   }

//-----------------------------------------------------------------------------------
// Dette er den første meny loopen
// Her blir kun to av alternativene vist
// Dersom brukeren roterer på encoderen blir to nye valg vist
// Dersom brukeren trukker inn knappen, blir valget som pilen peker på valgt
// Når en ny meny er valgt, får maxValue, stilling og menu nye verdier
if(stilling==1 && menu ==0){
  
  lcd.setCursor(0, 0);
  lcd.write(1);
  lcd.print("Booking");
  lcd.setCursor(0, 1);
  lcd.print(" Temperature");
  if(digitalRead(inputSW) != HIGH){
    menu = 1;
    stilling = 1;
    maxValue = 7;
    delay(100);
  }
}
else if(stilling==2 && menu ==0){
  
  lcd.setCursor(0, 0);
  lcd.write(1);
  lcd.print("Temperature");
  lcd.setCursor(0, 1);
  lcd.print(" Fan speed");
  if(digitalRead(inputSW) != HIGH){
    menu = 5;
    stilling = tempVar;
    counter = 44;
    maxValue = 60;
    delay(100);
  }
  
}
else if(stilling==3 && menu ==0){
  
  lcd.setCursor(0, 0);
  lcd.write(1);
  lcd.print("Fan speed");
  lcd.setCursor(0, 1);
  lcd.print(" Ventilation");
  if(digitalRead(inputSW) != HIGH){
    lcd.clear();
    menu = 6;
    stilling = 1;
    counter = 1;
    maxValue = 8;
    delay(100); 
  } 
}
else if(stilling==4 && menu ==0){
  
  lcd.setCursor(0, 0);
  lcd.write(1);
  lcd.print("Ventilation");
  lcd.setCursor(0, 1);
  lcd.print(" Tracking");
  if(digitalRead(inputSW) != HIGH){
    menu = 7;
    stilling = 0;
    counter = 0;
    maxValue = 2;
    delay(100);
  }
}
else if(stilling==5 && menu ==0){
  
  lcd.setCursor(0, 0);
  lcd.write(1);
  lcd.print("Tracking");
  lcd.setCursor(0, 1);
  lcd.print(" Open Door");
  if(digitalRead(inputSW) != HIGH){
    menu = 8;
    stilling = 0;
    counter = 0;
    maxValue = 2;
    delay(100);
  }
}
else if(stilling==6 && menu ==0){
  
  lcd.setCursor(0, 0);
  lcd.write(1);
  lcd.print("Open Door");
  lcd.setCursor(0, 1);
  lcd.print(" Quick booking");
  if(digitalRead(inputSW) != HIGH){
    menu = 9;
    delay(100);
  }
}
else if((stilling==7 && menu ==0)){
  
  lcd.setCursor(0, 0);
  lcd.write(1);
  lcd.print("Quick booking");
  lcd.setCursor(0, 1);
  lcd.print(" Status");
  if(digitalRead(inputSW) != HIGH){
    menu = 10;
    delay(100);  
}
}else if((stilling>=8 && menu ==0) or (stilling == 0 && menu == 0)){
  
  lcd.setCursor(0, 0);
  lcd.write(1);
  lcd.print("Status");
  lcd.setCursor(0, 1);
  lcd.print(" Booking");
  if(digitalRead(inputSW) != HIGH){
    menu = 11;
    stilling = 0;
    counter = 0;
    maxValue = 4;
    delay(100); 
  }
}

//-----------------------------------------------------------------------------------
// Dette er booking hovedmenyen
// Her kan brukeren velge hvilket rom som skal bookes: kjøkken, stue eller bad
// Brukeren kan også velge å gå tilbake til hovedmenyen
else if(stilling==1 && menu ==1){ 
  lcd.setCursor(0, 0);
  lcd.print(" Choose Booking:");
  lcd.setCursor(0, 1);
  lcd.write(1);
  lcd.print("  Bathroom");
  if(digitalRead(inputSW) != HIGH){
    menu = 2;
    stilling = 1;
    maxValue = 48;
    counter = 24;
    delay(100);
  }
  
}  
else if(stilling==2 && menu ==1){ 
  lcd.setCursor(0, 0);
  lcd.print(" Choose Booking:");
  lcd.setCursor(0, 1);
  lcd.write(1);
  lcd.print("  Kitchen");
  if(digitalRead(inputSW) != HIGH){
    menu = 3;
    stilling = 1;
    maxValue = 48;
    counter = 24;
    delay(100);
}  
}
else if(stilling==3 && menu ==1){ 
  lcd.setCursor(0, 0);
  lcd.print(" Choose Booking:");
  lcd.setCursor(0, 1);
  lcd.write(1);
  lcd.print("  Living room");
  if(digitalRead(inputSW) != HIGH){
    menu = 4;
    stilling = 1;
    maxValue = 48;
    counter = 24;
    delay(100);
}
}
else if(stilling==4 && menu ==1){ 
  lcd.setCursor(0, 0);
  lcd.print(" Choose Booking:");
  lcd.setCursor(0, 1);
  lcd.write(2);
  lcd.print("  Go back");
  if(digitalRead(inputSW) != HIGH){
    menu = 0;
    stilling = 1;
    maxValue = mainMax;
    counter = 0;
    delay(100);
  }
}

//-----------------------------------------------------------------------------------
// Her starter booking interfacet for for å booke kjøkkenet
// Brukeren starter med å velge starttiden
// Den starter på kl:12.00
//Minuttene har en stigning på 5 for hvert steg på encoderen
else if(menu == 2 && State == 0){
  lcd.setCursor(0, 0);
  lcd.print("Start time:");
  lcd.setCursor(0, 1);
  if(counter/2 < 10){
  lcd.print("0");
  lcd.setCursor(1, 1);  
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }else{
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }
  if(digitalRead(inputSW) != HIGH){
    fromTimeHour = counter/2;
    State = 1; 
    counter = 0;
    delay(100);
    }
}
else if(menu ==2 && State == 1){
  maxValue = 24;
  lcd.setCursor(0, 0);
  lcd.print("Start time:");
  lcd.setCursor(0, 1);
  if(fromTimeHour<10){
    lcd.print("0");
    lcd.setCursor(1,1);
    lcd.print(fromTimeHour);
  }else{
  lcd.print(fromTimeHour);
  }
  lcd.print(":");
  lcd.setCursor(3, 1);
  
  if(counter*5/2 < 10){
    lcd.print("0");
    lcd.setCursor(4, 1);  
    lcd.print(counter*5/2); 
 }else{
    lcd.print(counter*5/2); 
  }
if(digitalRead(inputSW) != HIGH){
    fromTimeMinutes = counter*5/2;
    State = 3; 
    counter = 24;
    delay(100);
    }
}

//Her velger brukeren sluttiden for bookingen
else if(menu ==2 && State == 3){
  
  maxValue=48;
  lcd.setCursor(0, 0);
  lcd.print("End time:");
  lcd.setCursor(0, 1);
  if(counter/2 < 10){
  lcd.print("0");
  lcd.setCursor(1, 1);  
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }else{
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }
  if(digitalRead(inputSW) != HIGH){
    tooTimeHour = counter/2;
    State = 4; 
    counter = 0;
    delay(100);
    }
}

else if(menu ==2 && State == 4){
  maxValue = 24;
  lcd.setCursor(0, 0);
  lcd.print("End time:");
  lcd.setCursor(0, 1);
  if(tooTimeHour<10){
    lcd.print("0");
    lcd.setCursor(1,1);
    lcd.print(tooTimeHour);
  }else{
  lcd.print(tooTimeHour);
  }
  lcd.print(":");
  lcd.setCursor(3, 1);
  
  if(counter*5/2 < 10){
    lcd.print("0");
    lcd.setCursor(4, 1);  
    lcd.print(counter*5/2); 
 }else{
    lcd.print(counter*5/2); 
  }
if(digitalRead(inputSW) != HIGH){
    tooTimeMinutes = counter*5/2;
    State = 8; 
    counter = 0;
    delay(100);
    }
}

// Dersom brukeren har valgt en sluttid som er mindre enn starttiden, vil det dukke opp en feilmelding
else if(menu == 2 && State == 8){
if (fromTimeHour > tooTimeHour or (fromTimeHour == tooTimeHour && fromTimeMinutes >= tooTimeMinutes)){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Please select a");
  lcd.setCursor(0,1);
  lcd.print("valid time");
  delay(4000);
  lcd.clear();
  menu= 0 ;
  stilling = 1;
  State = 0;
  maxValue = mainMax;     
}else{
  State = 5;
}
}

// Brukeren blir vist tiden som ble tastet inn, deretter kommer muligheten for å bekrefte om dette er riktig eller ikke
else if(menu == 2 && State == 5){
  lcd.setCursor(0,0);
  lcd.print("Selected time:");
  lcd.setCursor(0,1);
  if(fromTimeHour < 10){
    lcd.print("0");
    lcd.print(fromTimeHour);
  }else {
    lcd.print(fromTimeHour);
  }
  lcd.print(":");
  if(fromTimeMinutes < 10){
    lcd.print("0");
    lcd.print(fromTimeMinutes);
  }else {
    lcd.print(fromTimeMinutes);
  }
  lcd.print(" - ");
  if(tooTimeHour < 10){
    lcd.print("0");
    lcd.print(tooTimeHour);
  }else {
    lcd.print(tooTimeHour);
  }
  lcd.print(":");
  if(tooTimeMinutes < 10){
    lcd.print("0");
    lcd.print(tooTimeMinutes);
  }else {
    lcd.print(tooTimeMinutes);
  }
  delay(3000);
  lcd.clear();
  State = 6;
  lcd.print("Is this correct?");
}
else if( menu==2 && State ==6){
  maxValue = 3;
  stilling = 1;
  State = 7;
  lcd.clear();

//Dersom brukeren velger at tiden er riktig, blir signalet skrivet til CoT
}else if (menu == 2 && stilling <= 1 && State == 7) {
    lcd.print("Is this correct?");
    lcd.setCursor(0,1);
    lcd.print("Yes              ");
    if(digitalRead(inputSW) != HIGH){
      bookingSignal = 100000000 + (fromTimeHour*1000000) + (fromTimeMinutes*10000) + (tooTimeHour*100) + tooTimeMinutes;
      circusESP32.write(bookingKey,bookingSignal,token_1);
      lcd.clear();
      lcd.print("Checking . . . ");
      State = 10;
      delay(100);
    }

// Deretter søker konsollet etter feedback
// Dersom RPi-en gir verdien 92, bettyr dette at tiden allerede er booket
// Dersom RPi-en gir verdien 91, bettyr dette at bookingen var vellykket
} else if(menu == 2 && State == 10 && circusESP32.read(bookingKey, token_1) == 92){
       lcd.clear();
       lcd.setCursor(0,0);
       lcd.print("   Error");
       circusESP32.write(bookingKey,0,token_1);
       lcd.clear();
       menu= 0 ;
       stilling = 1;
       State = 0;
       maxValue = mainMax;
      delay(100);
      
      } else if(menu == 2 && State == 10 && circusESP32.read(bookingKey, token_1) == 91){
       lcd.clear();
       lcd.setCursor(0,0);
       lcd.print("Booking successful");
       circusESP32.write(bookingKey,0,token_1);
       lcd.clear();
       menu= 0 ;
       stilling = 1;
       State = 0;
       maxValue = mainMax;
      delay(100);

// Dersom brukeren velger at inntastet tid ikke stemmer, blir den sendt tilbake til bookingmenyen
}else if(menu == 2 && stilling >= 2 && State == 7){
    lcd.print("Is this correct?");
    lcd.setCursor(0,1);
    lcd.print("No             ");
    if(digitalRead(inputSW) != HIGH){
      menu= 1 ;
      stilling = 1;
      State = 0;
      maxValue = 8;
      delay(100);
 }
}  
//-----------------------------------------------------------------------------------
// Denne koden er lik den over, men den sender ut et signal med indexen for kjøkkenet
else if(menu ==3 && State == 0){
  
  lcd.setCursor(0, 0);
  lcd.print("Start time:");
  lcd.setCursor(0, 1);
  if(counter/2 < 10){
  lcd.print("0");
  lcd.setCursor(1, 1);  
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }else{
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }
  if(digitalRead(inputSW) != HIGH){
    fromTimeHour = counter/2;
    State = 1; 
    counter = 0;
    delay(100);
    }
}
else if(menu ==3 && State == 1){
  maxValue = 24;
  lcd.setCursor(0, 0);
  lcd.print("Start time:");
  lcd.setCursor(0, 1);
  if(fromTimeHour<10){
    lcd.print("0");
    lcd.setCursor(1,1);
    lcd.print(fromTimeHour);
  }else{
  lcd.print(fromTimeHour);
  }
  lcd.print(":");
  lcd.setCursor(3, 1);
  
  if(counter*5/2 < 10){
    lcd.print("0");
    lcd.setCursor(4, 1);  
    lcd.print(counter*5/2); 
 }else{
    lcd.print(counter*5/2); 
  }
if(digitalRead(inputSW) != HIGH){
    fromTimeMinutes = counter*5/2;
    State = 3; 
    counter = 24;
    delay(100);
    }
}
else if(menu ==3 && State == 3){
  
  maxValue=48;
  lcd.setCursor(0, 0);
  lcd.print("End time:");
  lcd.setCursor(0, 1);
  if(counter/2 < 10){
  lcd.print("0");
  lcd.setCursor(1, 1);  
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }else{
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }
  if(digitalRead(inputSW) != HIGH){
    tooTimeHour = counter/2;
    State = 4; 
    counter = 0;
    delay(100);
    }
}
else if(menu ==3 && State == 4){
  maxValue = 24;
  lcd.setCursor(0, 0);
  lcd.print("End time:");
  lcd.setCursor(0, 1);
  if(tooTimeHour<10){
    lcd.print("0");
    lcd.setCursor(1,1);
    lcd.print(tooTimeHour);
  }else{
  lcd.print(tooTimeHour);
  }
  lcd.print(":");
  lcd.setCursor(3, 1);
  
  if(counter*5/2 < 10){
    lcd.print("0");
    lcd.setCursor(4, 1);  
    lcd.print(counter*5/2); 
 }else{
    lcd.print(counter*5/2); 
  }
if(digitalRead(inputSW) != HIGH){
    tooTimeMinutes = counter*5/2;
    State = 8; 
    counter = 0;
    delay(100);
    }
}
else if(menu == 3 && State == 8){
if (fromTimeHour > tooTimeHour or (fromTimeHour == tooTimeHour && fromTimeMinutes >= tooTimeMinutes)){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Please select a");
  lcd.setCursor(0,1);
  lcd.print("valid time");
  delay(4000);
  lcd.clear();
  menu= 0 ;
  stilling = 1;
  State = 0;
  maxValue = mainMax;     
}else{
  State = 5;
}
}
else if(menu == 3 && State == 5){
  lcd.setCursor(0,0);
  lcd.print("Selected time:");
  lcd.setCursor(0,1);
  if(fromTimeHour < 10){
    lcd.print("0");
    lcd.print(fromTimeHour);
  }else {
    lcd.print(fromTimeHour);
  }
  lcd.print(":");
  if(fromTimeMinutes < 10){
    lcd.print("0");
    lcd.print(fromTimeMinutes);
  }else {
    lcd.print(fromTimeMinutes);
  }
  lcd.print(" - ");
  if(tooTimeHour < 10){
    lcd.print("0");
    lcd.print(tooTimeHour);
  }else {
    lcd.print(tooTimeHour);
  }
  lcd.print(":");
  if(tooTimeMinutes < 10){
    lcd.print("0");
    lcd.print(tooTimeMinutes);
  }else {
    lcd.print(tooTimeMinutes);
  }
  delay(3000);
  lcd.clear();
  State = 6;
  lcd.print("Is this correct?");
}
else if( menu==3 && State ==6){
  maxValue = 3;
  stilling = 1;
  State = 7;
  lcd.clear();
}
 else if (menu == 3 && stilling <= 1 && State == 7) {
    lcd.print("Is this correct?");
    lcd.setCursor(0,1);
    lcd.print("Yes              ");
    if(digitalRead(inputSW) != HIGH){
      bookingSignal = 200000000 + (fromTimeHour*1000000) + (fromTimeMinutes*10000) + (tooTimeHour*100) + tooTimeMinutes;
      circusESP32.write(bookingKey,bookingSignal,token_1);
      lcd.clear();
      lcd.print("Checking . . . ");
      State = 10;
      delay(100);
    }
      
 } else if(menu == 3 && State == 10 && circusESP32.read(bookingKey, token_1) == 92 ){
       lcd.clear();
       lcd.setCursor(0,0);
       lcd.print("   Error");
       circusESP32.write(bookingKey,0,token_1);
       lcd.clear();
       menu= 0 ;
       stilling = 1;
       State = 0;
       maxValue = mainMax;
      delay(100);
      
} else if( menu == 3 && State == 10 && circusESP32.read(bookingKey, token_1) == 91){
       lcd.clear();
       lcd.setCursor(0,0);
       lcd.print("Booking successful");
       circusESP32.write(bookingKey,0,token_1);
       lcd.clear();
       menu= 0 ;
       stilling = 1;
       State = 0;
       maxValue = mainMax;
      delay(100);
      
  } else if(menu == 3 && stilling >= 2 && State == 7){
    lcd.print("Is this correct");
    lcd.setCursor(0,1);
    lcd.print("No              ");
    if(digitalRead(inputSW) != HIGH){
      menu= 1 ;
      stilling = 1;
      State = 0;
      maxValue = 8;
      delay(100);
    }
  }

  
//-----------------------------------------------------------------------------------
// Denne koden er lik den over, men den sender ut et signal med indexen for TV-stua
else if(menu ==4 && State == 0){
  
  lcd.setCursor(0, 0);
  lcd.print("Start time:");
  lcd.setCursor(0, 1);
  if(counter/2 < 10){
  lcd.print("0");
  lcd.setCursor(1, 1);  
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }else{
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }
  if(digitalRead(inputSW) != HIGH){
    fromTimeHour = counter/2;
    State = 1; 
    counter = 0;
    delay(100);
    }
}
else if(menu ==4 && State == 1){
  maxValue = 24;
  lcd.setCursor(0, 0);
  lcd.print("Start time:");
  lcd.setCursor(0, 1);
  if(fromTimeHour<10){
    lcd.print("0");
    lcd.setCursor(1,1);
    lcd.print(fromTimeHour);
  }else{
  lcd.print(fromTimeHour);
  }
  lcd.print(":");
  lcd.setCursor(3, 1);
  
  if(counter*5/2 < 10){
    lcd.print("0");
    lcd.setCursor(4, 1);  
    lcd.print(counter*5/2); 
 }else{
    lcd.print(counter*5/2); 
  }
if(digitalRead(inputSW) != HIGH){
    fromTimeMinutes = counter*5/2;
    State = 3; 
    counter = 24;
    delay(100);
    }
}
else if(menu ==4 && State == 3){
  
  maxValue=48;
  lcd.setCursor(0, 0);
  lcd.print("End time:");
  lcd.setCursor(0, 1);
  if(counter/2 < 10){
  lcd.print("0");
  lcd.setCursor(1, 1);  
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }else{
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }
  if(digitalRead(inputSW) != HIGH){
    tooTimeHour = counter/2;
    State = 4; 
    counter = 0;
    delay(100);
    }
}

else if(menu ==4 && State == 4){
  maxValue = 24;
  lcd.setCursor(0, 0);
  lcd.print("End time:");
  lcd.setCursor(0, 1);
  if(tooTimeHour<10){
    lcd.print("0");
    lcd.setCursor(1,1);
    lcd.print(tooTimeHour);
  }else{
  lcd.print(tooTimeHour);
  }
  lcd.print(":");
  lcd.setCursor(3, 1);
  
  if(counter*5/2 < 10){
    lcd.print("0");
    lcd.setCursor(4, 1);  
    lcd.print(counter*5/2); 
 }else{
    lcd.print(counter*5/2); 
  }
if(digitalRead(inputSW) != HIGH){
    tooTimeMinutes = counter*5/2;
    State = 8; 
    counter = 0;
    delay(100);
    }
}
else if(menu == 4 && State == 8){
if (fromTimeHour > tooTimeHour or (fromTimeHour == tooTimeHour && fromTimeMinutes >= tooTimeMinutes)){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Please select a");
  lcd.setCursor(0,1);
  lcd.print("valid time");
  delay(4000);
  lcd.clear();
  menu= 0 ;
  stilling = 1;
  State = 0;
  maxValue = mainMax;     
}else{
  State = 5;
}
}

else if(menu == 4 && State == 5){
  lcd.setCursor(0,0);
  lcd.print("Selected time:");
  lcd.setCursor(0,1);
  if(fromTimeHour < 10){
    lcd.print("0");
    lcd.print(fromTimeHour);
  }else {
    lcd.print(fromTimeHour);
  }
  lcd.print(":");
  if(fromTimeMinutes < 10){
    lcd.print("0");
    lcd.print(fromTimeMinutes);
  }else {
    lcd.print(fromTimeMinutes);
  }
  lcd.print(" - ");
  if(tooTimeHour < 10){
    lcd.print("0");
    lcd.print(tooTimeHour);
  }else {
    lcd.print(tooTimeHour);
  }
  lcd.print(":");
  if(tooTimeMinutes < 10){
    lcd.print("0");
    lcd.print(tooTimeMinutes);
  }else {
    lcd.print(tooTimeMinutes);
  }
  delay(3000);
  lcd.clear();
  State = 6;
  lcd.print("Is this correct?");
}
else if( menu==4 && State ==6){
  maxValue = 3;
  stilling = 1;
  State = 7;
  lcd.clear();
}
 else if (menu == 4 && stilling <= 1 && State == 7) {
    lcd.print("Is this correct?");
    lcd.setCursor(0,1);
    lcd.print("Yes              ");
    if(digitalRead(inputSW) != HIGH){
      bookingSignal = 300000000 + (fromTimeHour*1000000) + (fromTimeMinutes*10000) + (tooTimeHour*100) + tooTimeMinutes;
      circusESP32.write(bookingKey,bookingSignal,token_1);
      lcd.clear();
      lcd.print("Checking . . . ");
      State = 10;
      delay(100);
    }
      
} else if(menu == 4 && State == 10 && circusESP32.read(bookingKey, token_1) == 92){ 
       lcd.clear();
       lcd.setCursor(0,0);
       lcd.print("   Error");
       circusESP32.write(bookingKey,0,token_1);
       lcd.clear();
       menu= 0 ;
       stilling = 1;
       State = 0;
       maxValue = mainMax;
      delay(100);
      
} else if(State == 10 && menu == 4 && circusESP32.read(bookingKey, token_1) == 91){  
       lcd.clear();
       lcd.setCursor(0,0);
       lcd.print("Booking successful");
       circusESP32.write(bookingKey,0,token_1);
       lcd.clear();
       menu= 0 ;
       stilling = 1;
       State = 0;
       maxValue = mainMax;
      delay(100);
      
} else if(menu == 4 && stilling >= 2 && State == 7){
    lcd.print("Is this correct?");
    lcd.setCursor(0,1);
    lcd.print("No              ");
    if(digitalRead(inputSW) != HIGH){
      menu= 1 ;
      stilling = 1;
      State = 0;
      maxValue = 8;
      delay(100);
    }
  }
 
//-----------------------------------------------------------------------------------
// Denne menyen lar brukeren bestemme temperaturen på rommet
// Her velges en verdi mellom 0 og 30
// Menyen starter med en verdi på 22 grader

else if( menu == 5 && State == 0){
  lcd.setCursor(0,0);
  lcd.print("Room temperature:");
  lcd.setCursor(0,1);
  lcd.print("    ");
  lcd.write(1);
  lcd.print(stilling);
  lcd.write(4);
  lcd.print("C");
  if(digitalRead(inputSW) != HIGH){
    State= 1;
    tempGoal = stilling;
    tempVar = stilling;    
  }
}
// Skriver verdien til CoT
else if(menu == 5 && State == 1){
  lcd.setCursor(0,0);
  lcd.print("Room temperature");
  lcd.setCursor(0,1);
  lcd.print("is set to: ");
  lcd.print(tempGoal);
  lcd.write(4);
  lcd.print("C");
  delay(4000);
  lcd.clear();
  menu = 0;
  State = 0;
  maxValue = mainMax;
  counter = 0;
  stilling= 1;
  circusESP32.write(tempKey,tempGoal,token_1);
}

//-----------------------------------------------------------------------------------
// Her kan brukeren velge hastigheten til vifta på rommet
// Den har 5 moduser: av, lav, medium, høy og automatisk

else if(menu == 6 && State == 0){
  if(digitalRead(inputSW) != HIGH){
    State =1;
    fanSpeed = stilling;
  }
    if(stilling==1){
    lcd.setCursor(0,0);
    lcd.print("Fan speed:");
    lcd.setCursor(0,1);
    lcd.write(1);
    lcd.print(" Low");
    }
    else if(stilling==2){
    lcd.setCursor(0,0);
    lcd.print("Fan speed:");
    lcd.setCursor(0,1);
    lcd.write(1);
    lcd.print(" Medium");
    }
    else if(stilling==3){
    lcd.setCursor(0,0);
    lcd.print("Fan speed:");
    lcd.setCursor(0,1);
    lcd.write(1);
    lcd.print(" High");
    }
    else if(stilling==0){
    lcd.setCursor(0,0);
    lcd.print("Fan speed:");
    lcd.setCursor(0,1);
    lcd.write(1);
    lcd.print(" Off");
    }
    else if(stilling==4){
    lcd.setCursor(0,0);
    lcd.print("Fan speed:");
    lcd.setCursor(0,1);
    lcd.write(1);
    lcd.print(" Automatic");
}
}
else if(menu == 6 && State == 1){
  lcd.setCursor(0,0);
  lcd.print("Speed choosen:");
  lcd.setCursor(0,1);
  if(fanSpeed == 1){
    lcd.print("    Low");
  }else if(fanSpeed == 2){
    lcd.print("  Medium");
  }else if(fanSpeed == 3){
    lcd.print("   High");
  }else if(fanSpeed == 0){
    lcd.print("   Off");
  }else if(fanSpeed == 4){
    lcd.print("  Automatic");
}
delay(3000);
menu = 0;
State = 0;
maxValue = mainMax;
counter = 1;
stilling = 1;
lcd.clear();
if (fanSpeed <= 3){
circusESP32.write(fanKey,fanSpeed,token_1);
} else {
 circusESP32.write(fanKey,10,token_1); 
}
}


//-----------------------------------------------------------------------------------
// Her kan brukeren velge en vinkel for luftevinduet
// Den kan settes manuelt mellom 0 og 80 grader
// Eller den kan bestemmes automatisk basert på temperaturen på brukerens soverom

else if (menu == 7 && State == 0){
  if(stilling == 0){
    lcd.setCursor(0,0);
    lcd.write("Ventilation:");
    lcd.setCursor(0,1);
    lcd.write(1);
    lcd.print(" Automatic");
    
    if(digitalRead(inputSW) != HIGH){
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print("Ventilation is ");
      lcd.setCursor(0,1);
      lcd.print("now Automatic");
      circusESP32.write(windowKey,81,token_1);
      delay(2000);
      lcd.clear(); 
      menu = 0;
      State = 0;
      maxValue = mainMax;
      counter = 0;
      stilling= 1;
      
    }
  }else if (stilling <= 1){
    lcd.setCursor(0,0);
    lcd.write("Ventilation:");
    lcd.setCursor(0,1);
    lcd.write(1);
    lcd.print(" Manual");

      if(digitalRead(inputSW) != HIGH){
       State =1;
       stilling = 45;
       counter = 90;
       maxValue = 160;
       delay(100);
    }
  }
  
}else if( menu == 7 && State == 1){
  lcd.setCursor(0,0);
  lcd.print("Choose angle:");
  lcd.setCursor(0,1);
  lcd.print("    ");
  lcd.write(1);
  lcd.print(stilling);
  lcd.write(4);
  if(digitalRead(inputSW) != HIGH){
    State= 2;
    windowAngle = stilling;
  }
}
else if(menu == 7 && State == 2){
  lcd.setCursor(0,0);
  lcd.print("Angle is set to:");
  lcd.setCursor(0,1);
  lcd.print("     ");
  lcd.print(windowAngle);
  lcd.write(4);
  delay(4000);
  lcd.clear();
  menu = 0;
  State = 0;
  maxValue = mainMax;
  counter = 0;
  stilling= 1;
  circusESP32.write(windowKey,windowAngle,token_1);
}


//-----------------------------------------------------------------------------------
// Dersom brukeren velger denne menyen blir ytterdøren opnet i noen sekunder før den låses igjen

else if( menu == 9 && State == 0){
  if (sek == 1){
  circusESP32.write(doorKey,1,tokenMain);
  }
  if (sek < 12){
  lcd.setCursor(0,0);
  lcd.print("The door is open");
  lcd.setCursor(0,1);
  lcd.print(11-sek);
  delay(1000);
  lcd.clear();
  sek ++;
  }else{
    State = 1;
    circusESP32.write(doorKey,0,tokenMain);
  }
}else if( menu == 9 && State == 1){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("The door is closed");
  delay(3000);
  lcd.clear();
  menu = 0;
  stilling = 1;
  State = 0;
  counter = 1;
  sek = 1;
}


//-----------------------------------------------------------
// Denne funksjonen forsøker å booke badet fra nåverende tid og 10 minutter fram
// Den skriver booking signalet til 888888888
// Etter dette venter den på feedback

else if (menu == 10 && State == 0){
  circusESP32.write(bookingKey,888888888,token_1);
  delay(100);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Checking . . .");
  if (circusESP32.read(bookingKey, token_1) == 91){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Toilet is booked");
  lcd.setCursor(0,1);
  lcd.print("for 15 min");
  circusESP32.write(bookingKey,0, token_1);
  delay(4000);
  lcd.clear();
  menu = 0;
  State = 0;
  
}else if (circusESP32.read(bookingKey,token_1) == 92){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("ERROR");
  lcd.setCursor(0,1);
  lcd.print("Toilet in use");
  circusESP32.write(bookingKey,0, token_1);
  delay(4000);
  lcd.clear();
  menu = 0;
  State = 0;
 }
}

//-------------------------------------------------------------
// Her får brukeren to valg: forlate kollektivet eller registrere gjester
// Dersom brukeren forlater kollektrivet blir trackingsignalet 0

else if (menu == 8 && State == 0){
  if (stilling == 0){
    lcd.setCursor(0,0);
    lcd.write(1);
    lcd.print("I'm leaving");
    lcd.setCursor(0,1);
    lcd.print(" Guest tracking");
    if(digitalRead(inputSW) != HIGH){
      State = 1;
      lcd.clear();
      delay(100);
    }
  }else if (stilling <= 1){
    lcd.setCursor(0,0);
    lcd.print(" I'm leaving");
    lcd.setCursor(0,1);
    lcd.write(1);
    lcd.print("Guest tracking");
    if(digitalRead(inputSW) != HIGH){
      State = 2;
      stilling = 1;
      counter = 1;
      maxValue = 6;
      lcd.clear();
      delay(100);
  } 
}

}else if (menu == 8 && State == 1){
  lcd.setCursor(0,0);
  lcd.print("    Bye Bye");
  lcd.setCursor(0,1);
  lcd.print("   Stay safe!");
  timer = 10000;
  State = 99;
  circusESP32.write(trackingKey_1, 0, token_1);

//-----------------------------------------------------------------------------------
// Dette er funksjonen som lar brukeren legge inn antall gjester (1-3) og når de er på besøk
// Den er lik Den vanlige booking funksjonen, med unntak av valget med antall gjester
  
}else if (menu == 8 && State == 2){
  lcd.setCursor(0,0);
  lcd.print("Number of guests:");
  lcd.setCursor(0,1);
  lcd.print("  ");
  if(stilling == 1){
    lcd.write(1);
    lcd.print("1");
    if(digitalRead(inputSW) != HIGH){
      guestCounter = 1;
      State = 3;
      stilling = 1;
      maxValue = 48;
      counter = 24;
      delay(100);
    }
  }else if(stilling == 2){
    lcd.write(1);
    lcd.print("2");
      if(digitalRead(inputSW) != HIGH){
       guestCounter = 2;
       State = 3;
       stilling = 1;
       maxValue = 48;
       counter = 24;
       delay(100);
      }
  }else if (stilling == 3){
    lcd.write(1);
    lcd.print("3");
      if(digitalRead(inputSW) != HIGH){
       guestCounter = 3;
       State = 3;
       stilling = 1;
       maxValue = 48;
       counter = 24;
       delay(100);
      }
  }else if (stilling == 0){
    lcd.write(2);
    lcd.print("Go back");
    if(digitalRead(inputSW) != HIGH){
    menu = 0;
    stilling = 1;
    maxValue = mainMax;
    counter = 0;
    delay(100);
  }
}


//-----------------------------------------------------------------------------------
// Her Blir starttiden lagt inn
}else if(menu == 8 && State == 3){

 lcd.setCursor(0, 0);
  lcd.print("Start time:");
  lcd.setCursor(0, 1);
  if(counter/2 < 10){
  lcd.print("0");
  lcd.setCursor(1, 1);  
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }else{
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }
  if(digitalRead(inputSW) != HIGH){
    fromTimeHour = counter/2;
    State = 4; 
    counter = 0;
    delay(100);
    }
}
else if(menu == 8 && State == 4){
  maxValue = 24;
  lcd.setCursor(0, 0);
  lcd.print("Start time:");
  lcd.setCursor(0, 1);
  if(fromTimeHour<10){
    lcd.print("0");
    lcd.setCursor(1,1);
    lcd.print(fromTimeHour);
  }else{
  lcd.print(fromTimeHour);
  }
  lcd.print(":");
  lcd.setCursor(3, 1);
  
  if(counter*5/2 < 10){
    lcd.print("0");
    lcd.setCursor(4, 1);  
    lcd.print(counter*5/2); 
 }else{
    lcd.print(counter*5/2); 
  }
if(digitalRead(inputSW) != HIGH){
    fromTimeMinutes = counter*5/2;
    State = 5; 
    counter = 24;
    delay(100);
    }
}
else if(menu ==8 && State == 5){
  
  maxValue=48;
  lcd.setCursor(0, 0);
  lcd.print("End time:");
  lcd.setCursor(0, 1);
  if(counter/2 < 10){
  lcd.print("0");
  lcd.setCursor(1, 1);  
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }else{
  lcd.print(counter/2); 
  lcd.setCursor(2, 1);  
  lcd.print(":00");
  }
  if(digitalRead(inputSW) != HIGH){
    tooTimeHour = counter/2;
    State = 6; 
    counter = 0;
    delay(100);
    }
}

else if(menu ==8 && State == 6){
  maxValue = 24;
  lcd.setCursor(0, 0);
  lcd.print("End time:");
  lcd.setCursor(0, 1);
  if(tooTimeHour<10){
    lcd.print("0");
    lcd.setCursor(1,1);
    lcd.print(tooTimeHour);
  }else{
  lcd.print(tooTimeHour);
  }
  lcd.print(":");
  lcd.setCursor(3, 1);
  
  if(counter*5/2 < 10){
    lcd.print("0");
    lcd.setCursor(4, 1);  
    lcd.print(counter*5/2); 
 }else{
    lcd.print(counter*5/2); 
  }
if(digitalRead(inputSW) != HIGH){
    tooTimeMinutes = counter*5/2;
    State = 8; 
    counter = 0;
    delay(100);
    }

}
else if(menu == 8 && State == 8){
if (fromTimeHour > tooTimeHour or (fromTimeHour == tooTimeHour && fromTimeMinutes >= tooTimeMinutes)){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Please select a");
  lcd.setCursor(0,1);
  lcd.print("valid time");
  delay(4000);
  lcd.clear();
  menu= 0 ;
  stilling = 1;
  State = 0;
  maxValue = mainMax;     
}else{
  State = 7;
}
}

else if(menu == 8 && State == 7){
  lcd.setCursor(0,0);
  lcd.print(guestCounter);
  lcd.print(" guests:");
  lcd.setCursor(0,1);
  if(fromTimeHour < 10){
    lcd.print("0");
    lcd.print(fromTimeHour);
  }else {
    lcd.print(fromTimeHour);
  }
  lcd.print(":");
  if(fromTimeMinutes < 10){
    lcd.print("0");
    lcd.print(fromTimeMinutes);
  }else {
    lcd.print(fromTimeMinutes);
  }
  lcd.print(" - ");
  if(tooTimeHour < 10){
    lcd.print("0");
    lcd.print(tooTimeHour);
  }else {
    lcd.print(tooTimeHour);
  }
  lcd.print(":");
  if(tooTimeMinutes < 10){
    lcd.print("0");
    lcd.print(tooTimeMinutes);
  }else {
    lcd.print(tooTimeMinutes);
  }
  delay(3000);
  lcd.clear();
  State = 9;
  lcd.print("Is this correct?");
}
else if( menu==8 && State ==9){
  maxValue = 3;
  stilling = 1;
  State = 10;
  lcd.clear();
}
 else if (menu == 8 && stilling <= 1 && State == 10) {
    lcd.print("Is this correct?");
    lcd.setCursor(0,1);
    lcd.print("Yes              ");
    if(digitalRead(inputSW) != HIGH){
      bookingSignal = ((guestCounter * 100000000) + 400000000) + (fromTimeHour*1000000) + (fromTimeMinutes*10000) + (tooTimeHour*100) + tooTimeMinutes;
      circusESP32.write(bookingKey,bookingSignal,token_1);
      lcd.clear();
      lcd.print("Checking . . . ");
      State = 11;
      delay(100);
    }
      
    }
 else if(menu == 8 && State == 11 && circusESP32.read(bookingKey, token_1) == 92){
       lcd.clear();
       lcd.setCursor(0,0);
       lcd.print("Error");
       circusESP32.write(bookingKey,0,token_1);
       lcd.clear();
       menu= 0 ;
       stilling = 1;
       State = 0;
       maxValue = mainMax;
      delay(100);
      
} else if(menu == 8 && State == 11 && circusESP32.read(bookingKey, token_1) == 91){
       lcd.clear();
       lcd.setCursor(0,0);
       lcd.print("     Booking ");
       lcd.setCursor(0,1);
       lcd.print("  successful");
       circusESP32.write(bookingKey,0,token_1);
       lcd.clear();
       menu= 0 ;
       stilling = 1;
       State = 0;
       maxValue = mainMax;
      delay(100);
      
    }
 else if(menu == 2 && stilling >= 2 && State == 10){
    lcd.print("Is this correct?");
    lcd.setCursor(0,1);
    lcd.print("No             ");
    if(digitalRead(inputSW) != HIGH){
      menu= 1 ;
      stilling = 1;
      State = 0;
      maxValue = 8;
      delay(100);
    }
//-----------------------------------------------------------------------------------
// Denne menyen lar brukeren sjekke statusen til forskjellige rom eller hvem som er hjemme
// Brukeren kan også gå tilbake til hovedmenyen

} else if(menu == 11 && stilling == 0 && State == 0){
  lcd.write(1);
  lcd.print("User status");
  lcd.setCursor(0,1);
  lcd.print(" Room status");
  lcd.setCursor(0,0);
   if(digitalRead(inputSW) != HIGH){
    State = 1;
    stilling = 0;
    maxValue = 12;
    lcd.clear();
    delay(100);
   }
} else if(menu == 11 && stilling == 1 && State == 0){
  lcd.write(1);
  lcd.print("Room status");
  lcd.setCursor(0,1);
  lcd.print(" Go back");
  lcd.setCursor(0,0);
   if(digitalRead(inputSW) != HIGH){
    State = 3;
    stilling = 0;
    maxValue = 7;
    lcd.clear();
    delay(100);
   }
  
} else if(menu == 11 && stilling >= 2 && State == 0){
  lcd.write(2);
  lcd.print("Go back");
  lcd.setCursor(0,1);
  lcd.print(" User status");
  lcd.setCursor(0,0);
   if(digitalRead(inputSW) != HIGH){
    lcd.clear();
    menu = 0;
    stilling = 0;
    maxValue = mainMax;
    delay(100);
   }
}else if(menu == 11 && stilling == 0 && State == 1){
  lcd.print("Updating . . .");
  lcd.setCursor(0,0);
  user1State = circusESP32.read(trackingKey_1, token_1);
  user2State = circusESP32.read(trackingKey_2, token_2);
 // user3State = circusESP32.read(trackingKey_3, token_3);
 // user4State = circusESP32.read(trackingKey_4, token_4);
 // user5State = circusESP32.read(trackingKey_5, token_5);
 // user6State = circusESP32.read(trackingKey_6, token_6);
  lcd.clear();
  State = 2;
  
}else if(menu == 11 && stilling == 0 && State == 2){
  lcd.setCursor(0,0);
  lcd.print(user1Name);
  lcd.print(":");
  lcd.setCursor(0,1);
  if (user1State == 1){
    lcd.print("is Home");
    lcd.setCursor(0,1);
  }else{
    lcd.print("is not Home");
    lcd.setCursor(0,1);
  }
  
}else if(menu == 11 && stilling == 1 && State == 2){
  lcd.setCursor(0,0);
  lcd.print(user2Name);
  lcd.print(":");
  lcd.setCursor(0,1);
  if (user2State == 1){
    lcd.print("is Home");
    lcd.setCursor(0,1);
  }else{
    lcd.print("is not Home");
    lcd.setCursor(0,1);    
}
}
  else if(menu == 11 && stilling == 2 && State == 2){
  lcd.setCursor(0,0);
  lcd.print(user3Name);
  lcd.print(":");
  lcd.setCursor(0,1);
  lcd.print("Unavaliable");
  }
  
  else if(menu == 11 && stilling == 3 && State == 2){
  lcd.setCursor(0,0);
  lcd.print(user4Name);
  lcd.print(":");
  lcd.setCursor(0,1);
  lcd.print("Unavaliable");
  }
  else if(menu == 11 && stilling == 4 && State == 2){
  lcd.setCursor(0,0);
  lcd.print(user5Name);
  lcd.print(":");
  lcd.setCursor(0,1);
  lcd.print("Unavaliable");
  }
  else if(menu == 11 && stilling == 5 && State == 2){
  lcd.setCursor(0,0);
  lcd.print(user6Name);
  lcd.print(":");
  lcd.setCursor(0,1);
  lcd.print("Unavaliable");
  }
  
  else if(menu == 11 && stilling == 6 && State == 2){
  lcd.setCursor(0,0);
  lcd.print("--  ");
  lcd.write(2);
  lcd.print("Go back  --");
     if(digitalRead(inputSW) != HIGH){
    lcd.clear();
    menu = 0;
    stilling = 0;
    State = 0;
    maxValue = mainMax;
    delay(100);
}
}
else if(menu == 11 && stilling == 0 && State == 3){
  lcd.print("Updating . . .");
  lcd.setCursor(0,0);
  bathroomState = circusESP32.read(bathroomKey, tokenMain);
  kitchenState = circusESP32.read(kitchenKey, tokenMain);
  livingroomState = circusESP32.read(livingroomKey, tokenMain);
  lcd.clear();
  State = 4;
  
}else if(menu == 11 && stilling == 0 && State == 4){
  lcd.setCursor(0,0);
  lcd.print("Bathroom:");
  lcd.setCursor(0,1);
  if(bathroomState == 0){
    lcd.print("Available");
  }else{
    lcd.print("Unavailable");
  }
}else if(menu == 11 && stilling == 1 && State == 4){
  lcd.setCursor(0,0);
  lcd.print("Kitchen:");
  lcd.setCursor(0,1);
  if(kitchenState == 0){
    lcd.print("Available");
  }else{
    lcd.print("Unavailable");
  }
}else if(menu == 11 && stilling == 2 && State == 4){
  lcd.setCursor(0,0);
  lcd.print("Living-room:");
  lcd.setCursor(0,1);
  if(livingroomState == 0){
    lcd.print("Available");
  }else{
    lcd.print("Unavailable");
  }
}  else if(menu == 11 && stilling >= 3 && State == 4){
  lcd.setCursor(0,0);
  lcd.print("--  ");
  lcd.write(2);
  lcd.print("Go back  --");
     if(digitalRead(inputSW) != HIGH){
    lcd.clear();
    menu = 0;
    stilling = 0;
    State = 0;
    maxValue = mainMax;
    delay(100);
 }
}

//-----------------------------------------------------------------------------------
// På slutten av koden finst timeren, når denne når 0 blir ESP32 deep sleep aktivert
// Brukeren kan aktivere konsollet igjen ved å trykke inn knappen i Rotary encoderen
  timer = timer -1;
  Serial.println(timer);
  if (timer <= 0){
    digitalWrite(backLight, LOW);
    lcd.clear();
    esp_sleep_enable_ext0_wakeup(GPIO_NUM_32, 0);
    esp_deep_sleep_start();
 }
}
