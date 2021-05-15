from time import sleep 
from datetime import date
import PowerFunc as PF # PF = hentet fra PowerFunc.py 


#starter med å lage alle variablene til dagens dato, ukenummer, mnd, år.  
Day = date.today()                               #YYYY-MM-DD 
WeekNumber = date.today().isocalendar()[1]       #Ukenumer 1-52 
MonthNumber = date.today().strftime("%m")        #MM  
Year = date.today().year                         #YYYY
 
CurrentHour = 0                                  # setter klokka til 0
CurrentMin  = 0                                  # setter klokka til 0 


#lager filer med en satt overskrift og kolonner



while True:
    PF.MakeFilesPower()                                                        #lager filer med en satt overskrift og kolonner
    
    if Day != date.today():
        Day = date.today()  
        PF.SaveDay()                                                           # lagrer i CSV fil                                    
        PF.KWHSaveWeek()                                                       # lagrer ukers forbruket i en midlertidig  fil
        PF.KWHSaveMonth()                                                      # lagrer måneds forbruket  i en midlertidig fil 
        PF.KWHSaveYear()                                                       # lagrer års forbruket i en midlertidig fil 

        PF.PowerPrice()                                                        # henter nye strømpriser og skriver til COT        
        PF.ResetTempHeadDay()                                                  # resetter alle dagsverdiene til Cot til 0 
     
   
        if WeekNumber != date.today().isocalendar()[1]:                           
            WeekNumber = date.today().isocalendar()[1] 
            PF.SaveWeek()                                                      # lagrer uke verdien til en Csv fil, gjør dette hver uke
            PF.WashingDryer()                                                  # starter uka med at "alle" kommer til å bruke vaskemaskin + tørketrommel
                                                 
            PF.ResetTempHeadlineWeek()                                         # resetter den midlertidige csv filen til å ta opp data for en ny uke
                                                         

        if MonthNumber != (date.today().strftime("%m")):
            MonthNumber = (date.today().strftime("%m"))
            PF.SaveMonth()                                                     # lagrer mnd verdien til en csv fil, gjør dette hver mnd
           
            PF.ResetTempHeadlineMonth()                                        # resetter den midlertidige csv filen til å ta opp data for en ny mnd 
                                                              
    
        
        if Year != date.today().year:    
            Year = date.today().year
            PF.SaveYear()                                                      # lagrer år verdien til en csv fil, gjør dette hvert år
            
       
            PF.ResetTempHeadlineYear()                                         # resetter den midlertidige csv filen til å ta opp data for en ny mnd 
          
       
    
   
    
    if CurrentMin !=PF.MinCheck():
        CurrentMin = PF.MinCheck() 
        PF.CheckifLight()
        PF.CheckLivingroomKitchenLight()                                       # funksjonen sjekker om lyset på kjøkken/stue er på
        PF.CheckBathroomLight()
        PF.PowerConsumeTemp()                                                  # funksjon som sjekker ønsket temperatur og legger til KWH
        PF.CheckFan()                                                          # sjekker om viften står på, og hvilket nivå. legger til KWH
        PF.Bill()                                                              # oppdaterer strømruket så langt 
        # print("powerconsume kjørte " +  str(PF.Now()) )                        # forbruk deretter. 
        
    if CurrentHour != PF.HourCheck():    
        CurrentHour = PF.HourCheck()    
        PF.PowerFridgeFreezerBathroom()                                        #  legger til KWH forbruk kjøleskap og fryser til delt KWH COT 
        PF.PowerGen()                                                          # funksjon som sjekker om det er sol, og regner ut,
        PF.WriteToCot()                                                        # teoretisk verdi etter forholdene 
        print ("currenttime linja ble kjørt "+ str (PF.Now()))                    
  
    
    sleep(1)                                                                   #en kort beauty sleep for RPI 
        
    
    
    


