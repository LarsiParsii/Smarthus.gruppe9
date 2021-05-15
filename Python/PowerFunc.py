import signal_info as SI 
import requests
import json
import time 
import pandas as pd
import csv
from datetime import date 
from datetime import datetime
import os.path
from re import findall



# funksjonen nedenfor regner ut en teoretisk strøm generert av solcellepanel
# den er avhengig av funksjonen Cloud() for å finne ut hvor overskyet det er ute
# den regner at solcellepanelene står på ntnu Gløshaugnen. 
def PowerGenKWH():
    """Calculates a theoretical value for solar panels."""
    AnualSun = (200000/(365*24))            # i norge 200k/ (365*24)  får time KWH 
    Area = 109.11                           # total areal kvm med solcellepanel
    Efficiency = (19.7/100)                 # 19,7%  effektfaktor 
    PreformanceRatio = 1                    # minus cloud()  pf,  Performance ratio 
    
    kilo = 1000                             
    
    CloudPercentage = 0 
    LimitCloud = 0.8
    
    if Cloud() > LimitCloud:
        CloudPercentage = LimitCloud
    elif Cloud() < LimitCloud:
        CloudPercentage = Cloud()
        
    Energy = (AnualSun*Area*Efficiency*(PreformanceRatio - CloudPercentage))
    return (Energy/kilo)                   # dividert på kilo for å få KWH 

# funksjonen nedenfor sletter en fil om den eksisterer
def DeleteFile(filename):
    '''Deletes given file'''
    if os.path.exists(filename):
      os.remove(filename)



# funksjonen nedenfor er for å hente strømpriser
# den henter dagspriser og skal kun kjøres 1 gang per dag. 
# den addere nettleia i strømprisen
# kode snutten ble laget med Harald. studass
def PowerPrice():
    """Gets daily Power price kr per kWh."""
    timestr = time.strftime("%Y-%m-%d") ##timesbasert 
    getcurrenttime=time.strftime("%Y-%m-%dT%H:00:00+02:00") #for og indeksere i det store dictet som vi får tilbake
    param={'zone':"NO3","date":timestr} 
    a=requests.get("https://norway-power.ffail.win",params=param)
    
    
    g=a.content.decode('utf-8') #bruker decode for og få vekk b' 
    k=json.loads(g)             #laster inn som ett dict
    
    a=k[getcurrenttime] 
    
    price = a ["NOK_per_kWh"]

    SI.PowerPrice.write(price)


# funksjonen nedenfor ser på strøm brukt iløpe av dagen vs generert
# deretter mulitpliserer dette med strømprisen (kr per KWH)

def Bill():
    """Calculates the bill with respect to power used vs generated, with a dynamic price."""
    
    GridUse = 0.24            #kr, dette er nettleie per forbruk av KWH 
    GridConst = (150*12/365)  #kr, tar 150kr som er fast per mnd, multipliserer 
                              #for å få or og dividere med antall dager for å få dagspris
    
    data = pd.read_csv("TempDayFile.csv",sep=";",error_bad_lines=False)
    data0 = float (data["Power generated"].iloc[-1])
    data1 = float (data["Total power consumption"].iloc[-1]) 
    
    KWH   = data1 - data0
    Price   = GridConst +  KWH * (float (SI.PowerPrice.read_int()) + GridUse)             
    TempDay("bill",Price)
    


# funksjonen nedenfor er for å regne ut forbruk av lyspærene
# hvert rom har 3 lyspærer,. 3*0.009   
# soverom har dimming og bruker derfor prosent av pæren ut etter hvor skyet lyst det er ute
# blir multiplisert med sky % om det er 100% overskyet står pærene på fult. 
def Lightbulb():
    """Calculates power with dimming, dims with respect to how cloudy."""
    bulb = 0.027                   # KWH
    KWHConsumed  = (bulb * 1/60)   # multipliserer med 1/60 for å få kwh hvert min, beholder KWH
    KWHConsumed  = (KWHConsumed * Cloud())
    return KWHConsumed


# funksjonen skal sjekke om det er noen hjemme + om det er kveld eller ikke og om personen er hjemme
# egentlig skal det være en per rom men rom 1,3,5 og rom 2,4,6 deler signal for enkelhetsskyld 
def CheckifLight():
    """Checks if bedroom has light on or off and calculates power use if on."""
    if SI.NightSignal == 0  and SI.Tracking1_3_5.read_int() == 1:
        TempDay("room1",Lightbulb())
        TempDay("room3",Lightbulb())
        TempDay("room5",Lightbulb())

    if SI.NightSignal == 0  and SI.Tracking2_4_6.read_int() == 1:
        TempDay("room2",Lightbulb())
        TempDay("room4",Lightbulb())    
        TempDay("room6",Lightbulb())



# funksjonen nedenfor sjekker om vifta står på og hvilket nivå den er på
def CheckFan():
    """Checks if fan is on in any of the bedroms and calculates power use with respect to the speed it is on."""
    FanLow    = 0.026            #kwh
    FanMedium = 0.038            #kwh
    FanHigh   = 0.058            #kwh
    
    Mintohour = 1/60   # koden kjører hvert min, derfor må den gjøres om til min, er fortsatt KWH
    CheckRoom1_3_5 = SI.FanRoom1_3_5.read_int()
    CheckRoom2_4_6 = SI.FanRoom2_4_6.read_int()
    
    if CheckRoom1_3_5 == 11 or CheckRoom1_3_5 == 1:
        FanLowValue = (FanLow * Mintohour )                
        
        TempDay("room1",FanLowValue)
        TempDay("room3",FanLowValue)
        TempDay("room5",FanLowValue)
        
    if CheckRoom1_3_5 == 12 or CheckRoom1_3_5 == 2:
        FanMediumValue = (FanMedium * Mintohour )           

        TempDay("room1",FanMediumValue)
        TempDay("room3",FanMediumValue)
        TempDay("room5",FanMediumValue)
    
    if CheckRoom1_3_5 == 13 or CheckRoom1_3_5 == 3:
        FanHighValue = (FanHigh * Mintohour )               
      
        TempDay("room1",FanHighValue)
        TempDay("room3",FanHighValue)
        TempDay("room5",FanHighValue)


    if CheckRoom2_4_6 == 11 or CheckRoom1_3_5 == 1:
        FanLowValue = (FanLow * Mintohour )                
       
        TempDay("room2",FanLowValue)
        TempDay("room4",FanLowValue)
        TempDay("room6",FanLowValue)

    if CheckRoom2_4_6 == 12 or CheckRoom1_3_5 == 2:
        FanMediumValue = (FanMedium * Mintohour )         
        
        TempDay("room2",FanMediumValue)
        TempDay("room4",FanMediumValue)
        TempDay("room6",FanMediumValue)
        
    if CheckRoom2_4_6 == 13 or CheckRoom1_3_5 == 3:
        FanHighValue = (FanHigh * Mintohour )              
        
        TempDay("room2",FanHighValue)
        TempDay("room4",FanHighValue)
        TempDay("room6",FanHighValue)
    
    

# funksjonen tar inn konsollnummer ("identifikasjon"), rom som er booket og hvor lang tid den er booket, i timer.
# deretter multipliserer den tid med en konstant, på bad så er tanken at man bruker varmtvann og derfor multipliserer etter et vist antall min
# på bad 
def KWHConsumed (console, room, duration) : 
    """"Calculates the power use on booking, (console thats booking, room you want to book, duration in hours"""
    consumption_per_room = {'Bad': 25.1, 'Kjokken':4.9, 'Stue': 0.0220}   # konstantene er i KWH. 
    ConstBathroom  = 0.17        #10 min = 0.1667 timer, kan forandre 10 min til en annen ønsket verdi. alt over 10 min bruker varmtvann
    ConstKitchen   = 0.17        #10 min = 0.1667 timer, kan forandre 10 min til en annen ønsket verdi. alt over 10 min bruker ovn/panne og ligdene
    
    
    consumption = consumption_per_room[room] * duration
 
    if room =="Bad":
        NewDurationBathroom = duration - ConstBathroom                                     
        if NewDurationBathroom <= 0:
            return 
        elif NewDurationBathroom > 0:
            consumption = consumption_per_room[room] * NewDurationBathroom 
            
    if room =="Kjokken":
        NewDurationKitchen = duration - ConstKitchen
        if NewDurationKitchen <= 0:
            return
        elif NewDurationKitchen >0:
            consumption = consumption_per_room[room] * NewDurationKitchen
        
    if console == "Console1":        
        TempDay("room1",consumption)
        
        
    elif console == "Console2":
        TempDay("room2",consumption)
        
        
    elif console == "Console3":
        TempDay("room3",consumption)

    
    elif console == "Console4":
        TempDay("room4",consumption)
      
             
        
    elif console == "Console5":
        TempDay("room5",consumption)
     

    elif console == "Console6":
     TempDay("room6",consumption)
     
    else:
        print ("nå gikk noe galt kjære venn")
        return
    
    print(f"[Added {consumption}kWh to {console}]")
    

# funksjonen nedenfor sjekker om det er bevegelse på badet og slår på lyset
# må kjøres hvert min 

# 1 er på og 0 er av 
# har 5 lys bruker 0.009 kwh per lys
# om det er kveld så brukes lyset på halv effekt
def CheckBathroomLight():
    """Checks if bathroom light is on, if its on, calculates power consumed with respect if its night or day."""
    Lightbulbconsume = 0.009 # per lyspære bruker 0.009 kWh 
    AmountLightbulbs = 5 
    Mintohour  = 1/60        # koden kjører hvert min, derfor må den gjøres om til min, er fortsatt KWH
    Halfpower  = 1/2         # om natt er lyspærene på halv effekt
    
    if SI.NightSignal == 0  and SI.BathroomLight.read_int() == 1:
        kwh = (AmountLightbulbs * Lightbulbconsume) 
        kwh = (kwh * Mintohour)
        TempDay("shared", kwh) 

    if SI.NightSignal == 1  and SI.BathRoomLight.read_int() == 1:
        kwh = (AmountLightbulbs *Lightbulbconsume) 
        kwh = (kwh * Mintohour * Halfpower) 
        TempDay("shared", kwh) 
        

# det er  12 lyspærer tilsammen på stue og kjøkken 

def CheckLivingroomKitchenLight():
    """Checks if  kitchen light is on, if its on, calculates power consumed."""
    Lightbulbconsume = 0.009 # per lyspære bruker 0.009 kWh 
    Lightbulbs = 12 
    Mintohour  = 1/60   # koden kjører hvert min, derfor må den gjøres om til min, er fortsatt KWH
    Halfpower  = 1/2    # om natt er lyspærene på halv effekt
    
   
    if SI.NightSignal == 0  and SI.LivingRoomKitchenLight.read_int() == 1:
        kwh = (Lightbulbs * Lightbulbconsume) 
        kwh = (kwh * Mintohour)
        TempDay("shared", kwh) 

    if SI.NightSignal == 1  and SI.LivingRoomKitchenLight.read_int() == 1:
        kwh = (Lightbulbs * Lightbulbconsume) 
        kwh = (kwh * Mintohour * Halfpower) 
        TempDay("shared", kwh) 

       

    
# funksjonen nedenfor tar inn foreløpig KWH brukt og adderer det med hvor mye KWH man har brukt med ønsket temperatur iforhold til ute temp 
# kjøkken og stue er dobbelt så stor som ett soverom, derfor multiplisert med 2 

def PowerConsumeTemp ():
   """Checks the tempertaure set with outside temperature and calculates energy used to keep that temperature."""

   TempDay("shared",( 2* PowerConsHeat(SI.TempSharedSpace)))

   TempDay("room1",PowerConsHeat(SI.TempRoom1_3_5))
   TempDay("room2",PowerConsHeat(SI.TempRoom2_4_6))
   TempDay("room3",PowerConsHeat(SI.TempRoom1_3_5))
   TempDay("room4",PowerConsHeat(SI.TempRoom2_4_6))
   TempDay("room5",PowerConsHeat(SI.TempRoom1_3_5))
   TempDay("room6",PowerConsHeat(SI.TempRoom2_4_6))



# funksjonen nedenfor er for å regne ut energi forbruk på varmekabler
# kjøres hver time
def BathroomConsume():
    """Checks the temperature on the bathroom every min, calculates energy used."""
    BathroomSize = 6                    #kwm
    ConsumeLow   = 0.12 *  BathroomSize #kwh
    ConsumeHigh  = 0.15 *  BathroomSize #kwh 
    Temp = SI.TempBathroom.read_int()
    
    if  Temp >= 19:
        ConsumeHighMin = (ConsumeHigh)
        return (ConsumeHighMin)
    if  Temp <  19:
        ConsumeLowMin = (ConsumeLow)
        return (ConsumeLowMin)
    
    
    
    
# funksjonen nedenfor er for å regne ut 
def WashingDryer():
    """Calculates the use of washing machine and dyer one use per room plus one time with shared expense."""
    Washingmachine = 1 #kwh
    Dryer          = 1 #kwh
    
    total  = Washingmachine + Dryer 
    
    TempDay("shared",total)
    TempDay("room1",total)
    TempDay("room2",total)
    TempDay("room3",total)
    TempDay("room4",total)
    TempDay("room5",total)
    TempDay("room6",total)

# funksjonen nedenfor skal kjøres hver  time for å få inn delt forbruk på kjøleskap og fryser.
# den leser av delt forbruk og deretter legger inn hvor mye kjøleskap og fryser bruker hver time.
def PowerFridgeFreezerBathroom():    
    """Calculates the use of fridge, freezer and heating on bathroomfloor, sends it to TempDayFile"""
    fridge = 0.0164     #kwh
    freezer = 0.0305    #kwh
    #må skrive inn strøm forbruk på varmekabler bad. husk forskjell på dag og natt me kor varmt.
    
    HeatingBathroomFloor = BathroomConsume()                       
    total = HeatingBathroomFloor + fridge + freezer     
    TempDay("shared",total)
    

    
    
# funksjonen tar inn ønsket temperatur fra soverommene og finner differansen mellom ønsket VS temperatur
# om differansen er negativ retunerer den 0 KWH
# om differansen er positiv blir den multiplisert med en konstant for å lage en teoretisk verdi (ikke særlig nøyaktig), 
# og avrundet. man må bruke denne med et cotsignal så KWH blir lagt til "den personen som har den ønsket temperaturen" 

def PowerConsHeat(Cotsignal):
    """Calculates the energy used to keep the bedrooms a temperature compared to outside temperature."""
    PowerHeat      = 0 
    Wattused       = (60/1000)
    RoomSizeKWh    = (12 * Wattused )                           #rommene er på 12kvaderatmeter og bruker ca 60 watt per kvm, deler på 1000 for å få KWH                                          
    TemporaryCloud = 0 
    CloudLimit     = 0.3
    MintoHour      = 1/60                         # KWH konstanten ganges med 1min / 60 for å beholde KWH, siden programmet kjører hvert min
    if Cloud() < CloudLimit:                      # om det er mer enn  30 % sky så varmer ikke sola taket (sier vi )
        TemporaryCloud = 0.1                      # om det er mindre enn 30% skyer så bruker den 0.1 KWH mindre forbruk på oppvarming
    
    IdealTemperature= Cotsignal.read_int()           
    difference = IdealTemperature - OutsideTemp()      # tar ønsket temperatur(hentet fra COT) - ute tempratur (hentet fra met.no)
    if difference <= 0:                                # om ønsket er lavere enn utetemp, retuner 0 (0 kwh brukt)
        return 0
    
    elif  1 <= int ( difference) & int (difference) <= 5:        #om diffreansen er mellom 1 til 5. bruker 20% av effekten
        PowerHeat = ((RoomSizeKWh - TemporaryCloud) * 0.20)                
         
    elif 5 < int ( difference) & int (difference) <= 10:         #om diffreansen er mellom 5 til 10. bruker 30% av effekten
        PowerHeat = ((RoomSizeKWh - TemporaryCloud) * 0.30)            
        
    elif 10 < int ( difference) & int (difference) <= 15:        #om diffreansen er mellom 10 til 15. bruker 40% av effekten
        PowerHeat = ((RoomSizeKWh - TemporaryCloud) * 0.40)
    
    elif 15 < int (difference):
        PowerHeat = ((RoomSizeKWh - TemporaryCloud) * 0.50)      #om diffreansen er mer enn 15. bruker 50% av effekten
    
    PowerHeatMin = (PowerHeat * (MintoHour))
    return round((PowerHeatMin),6)   #hvor mye KWH som trenges for å varme det rommet, avrunder med 6 desimal





# funksjonen min og hour check sjekker om hvilket minutt man er i, eller hvilken time man er i. 
# blir brukt som en egen planlegger for å få funksjoner til å kjøre hver time og minutt 

def MinCheck():
    """Gives the current min,MM"""
    now = datetime.now()
    return now.minute


def HourCheck():
    """Gives the current hour, HH"""
    now = datetime.now()
    return now.hour

def Now():
    """gives the date, time right now"""
    now = datetime.now()
    return now

# funksjonen henter nåværende time fra met.no , dvs er klokka 15.40 får man tiden 15.00-16.00
def GetDataThisHour():
    """Gets data from met.no with values for the hour you use the function"""
    from metno_locationforecast import Place, Forecast #bibloteket for å hente fra met
    Trondheim = Place("Trondheim", 63.42, 10.40, 50)  #gløshaugen 
    USER_AGENT = "metno_locationforecast/1.0 marmarth@stud.ntnu.no" #viktig ikke bytt
    tr_forecast = Forecast(Trondheim, USER_AGENT)
    tr_forecast.update()
    interval = tr_forecast.data.intervals [2]
    return interval


# funksjonen henter ut cloud data fra  skydataen til met.no, den er egentlig i prosent derfor blir den gjort om til float,
# deretter dividert  med 100 for å få det til desimal, float.

def Cloud():
    """Gives the precentage of cloud in decimal for the hour you run the function"""
    interval = GetDataThisHour()
    cloud = str (interval.variables["cloud_area_fraction"])
    temporary = findall('\d*\.?\d+',cloud)
    res = float('.'.join(str(ele) for ele in temporary))
    cloud = (res/100)
    
    return  cloud



# funksjonen henter ut lufttemperaturen utenfor og gjør denne om til float. 
def OutsideTemp():
    """Gvies the outside temperature as a float"""
    interval = GetDataThisHour()
    temp = str (interval.variables["air_temperature"])
    temporary = findall('\d*\.?\d+',temp)
    res = float('.'.join(str(ele) for ele in temporary))
    temp = res
    return temp



# funksjonen sjekker om solen har stått opp, eller har gått ned. 
# om det er en time etter den har stått opp, og en time før den har gått ned ( for den genererer ikke like mye rett etter og rett før soloppgang/nedgang)
# om den er en time etter og eller en time før, da regner den i snitt KWH generert av solcellepanelene "opp på taket" 
# den tar inn nå tids data om sola er oppe eller ned, nå tidsdata om hvor overskyet. 
# funksjonen tar inn verdien, leser av COT (gammelverdi) og adderer gammel verdi med ny verdi (det som blir generert i timen man er i)
# funksjonen bruker sky % og om det er sol. dette er ikke veldig nøyaktig.

def PowerGen():
    """Checks if the sun is up or down, and calculate power generated if sun is up."""
    if SunRise() < int (HourCheck()) & int (HourCheck()) < SunDown():
                                                                           
        #print("nå kjøres dag") #temporarary print for meg  
                             
        TempDay("Generation",PowerGenKWH()) 







# funksjonen nedenfor er fra kumar_satyam 29.12.2020 
# hentet fra https://www.geeksforgeeks.org/create-a-gui-to-get-sunset-and-sunrise-time-using-python/ den 28/04/2021
# hele koden er hentet fra kilden bare forandret for å passe inn. 
def SunRiseDown():
    """checks when goes up or down in Trondheim"""
    # import required modules
    from suntime import Sun
    from geopy.geocoders import Nominatim  #nominatim API 
      
    # Nominatim API to get latitude and longitude
    geolocator = Nominatim(user_agent="geoapiExercises")
      
    # input place
    place = "Trondheim"
    location = geolocator.geocode(place)
      
    # latitude and longitude fetch
    latitude = location.latitude
    longitude = location.longitude
    sun = Sun(latitude, longitude)
    return sun


def SunRise():
    """gives the time hour, HH, when the sun rise, in Trondheim"""
    from datetime import datetime
    sun = SunRiseDown()
    time_zone = datetime.date(datetime.now())
    SunRise = sun.get_local_sunrise_time(time_zone)
    return int((SunRise.strftime('%H')))  #tar ut timen den står opp som int

    
    
def SunDown():
    """gives the time hour, HH, when the sun sets, in Trondheim"""
    from datetime import datetime
    sun = SunRiseDown()
    time_zone = datetime.date(datetime.now())
    
    SunDown = sun.get_local_sunset_time(time_zone)
    return int((SunDown.strftime('%H')))  # tar ut timen den går ned som int 
#------------------------------------------------------------------------------



#alle funksjonene nedenfor sjekker gårsdagen og deretter gir dag, uketall, mnd nummer eller årstall.
def YesterDayDate():
    """Gives out yesterdays date"""
    from datetime import date
    from datetime import timedelta 
    today = date.today()
    return today - timedelta(days=1)


def LastWeekNumber():
    """Gives last week number by checking yesterdays date and using that date to give out that week number, very specific use"""    
    LastWeek = YesterDayDate()
    
    Week_Number = LastWeek.isocalendar()[1]
    return Week_Number


def LastMonthNumber():
    """Gives last month by checking yesterdays date and using that date to give out that month, very specific use"""  
    from datetime import date
    from datetime import timedelta 
    today = date.today()
    today - timedelta(days=1)
    return today.strftime("%m")

def LastYear():
    """Gives last year by checking yesterdays date and using that date to give out that year, very specific use""" 
    from datetime import date
    from datetime import timedelta 
    today = date.today()
    today - timedelta(days=1)
    return today.strftime("%Y")



#funksjoner for å lagre ---------------------------


# funksjonen nedenfor sjekker om DishwasherFilledLevel eksistere, og om ikke så oppretter den det.
def CheckDishwasherFile():
    """Makes the file for dishwasher filled level"""
    if os.path.isfile('DishwasherFilledLevel.csv'):
            return
    else:
        with open('DishwasherFilledLevel.csv', 'w', newline='', encoding='utf-8') as file:
           writer = csv.writer(file, delimiter=';')
           writer.writerow(["percentage filled"])
           writer.writerow([0])
           
# funksjonen nedenfor er for å lagre fyllingsnivået til oppvaskmaskinen 
def DishWasherFile(add_usage):
    CheckDishwasherFile()
    """Adds value in dishwasher file, DishwasherFilledLevel"""
    data = pd.read_csv("DishwasherFilledLevel.csv",sep=";",error_bad_lines=False)
    lastdata = int(data["percentage filled"].iloc[-1])

    with open ('DishwasherFilledLevel.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        NewValue = (lastdata + add_usage)
        writer.writerow([NewValue])
    CheckFillingLevel()     
        
def CheckFillingLevel():
    DishwasherKWH = 0.8
    """checks the value in dishwasher file, DishwasherFilledLevel, if over 80% then calulates energy use to run it once, resets file to zero."""
    data = pd.read_csv("DishwasherFilledLevel.csv",sep=";",error_bad_lines=False)
    lastdata = int(data["percentage filled"].iloc[-1])
    if lastdata >= 80:
        with open('DishwasherFilledLevel.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["percentage filled"])
            writer.writerow([0])
        TempDay("shared",DishwasherKWH)
      #  print ("Dishwasher used 0.8 KWH.")


# disse fire funksjonene lager det samme oppsette til fire forskjellige filer
# de har samme oppsett annet enn dato, ukenummer, mnd , år. 
# de sjekker også om filen allerede eksisterer, om den eksistere så lager den ikke en ny
# om filen ikke eksistere så lager den, med et satt oppsett

def HeadlineDay():
    """Checks if A_Daylog exists, create it if it does not exist."""
    if os.path.isfile('A_Daylog.csv'):
            return
    else:
        with open('A_Daylog.csv', 'w', newline='', encoding='utf-8') as file:
           writer = csv.writer(file, delimiter=';')
           writer.writerow(["Date","Power generated","Total power consumption","Electricity bill in kr","Power consumption common area","Power consumption room 1","Power consumption room 2",\
                         "Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])
    
           
def HeadlineWeek():
    """Checks if A_Weeklog exists, create it if it does not exist."""
    if os.path.isfile('A_Weeklog.csv'):
            return
    else:
        with open('A_Weeklog.csv', 'w', newline='', encoding='utf-8') as file:
           writer = csv.writer(file, delimiter=';')
           writer.writerow(["Date","Power generated","Total power consumption","Electricity bill in kr","Power consumption common area","Power consumption room 1","Power consumption room 2",\
                         "Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])
   
def HeadlineMonth():
    """Checks if A_Monthlog exists, create it if it does not exist."""
    if os.path.isfile('A_Monthlog.csv'):
           return
    else:
        with open('A_Monthlog.csv', 'w', newline='', encoding='utf-8') as file:
           writer = csv.writer(file, delimiter=';')
           writer.writerow(["Date","Power generated","Total power consumption","Electricity bill in kr","Power consumption common area","Power consumption room 1","Power consumption room 2",\
                         "Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])
       
               
def HeadlineYear():
    """Checks if A_Yearlog exists, create it if it does not exist."""
    if os.path.isfile('A_Yearlog.csv'):
            return
    else:
        with open('A_Yearlog.csv', 'w', newline='', encoding='utf-8') as file:
           writer = csv.writer(file, delimiter=';')
           writer.writerow(["Date","Power generated","Total power consumption","Electricity bill in kr","Power consumption common area","Power consumption room 1","Power consumption room 2",\
                         "Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])


#funksjonen nedenfor lager en Temp fil som blir oppdatert hvergang noe forbruker eller genererer strøm 

def TempDay(room,value):
    """Add values to the room you want, room, value."""
    data = pd.read_csv("TempDayFile.csv",sep=";",error_bad_lines=False)
    
    data0 = float (data["Power generated"].iloc[-1])
    data1 = float (data["Total power consumption"].iloc[-1]) 
    data2 = float (data["Electricity bill in kr"].iloc[-1])
    data3 = float (data["Power consumption common area"].iloc[-1])
    data4 = float (data["Power consumption room 1"].iloc[-1]) 
    data5 = float (data["Power consumption room 2"].iloc[-1])
    data6 = float (data["Power consumption room 3"].iloc[-1])
    data7 = float (data["Power consumption room 6"].iloc[-1])
    data8 = float (data["Power consumption room 5"].iloc[-1])  
    data9 = float (data["Power consumption room 6"].iloc[-1])  
    
    value = round (value,4)
    
    
    
    if room == "Generation":    
        data0 = (float (data["Power generated"].iloc[-1]) + value)
    elif room == "Consumed":
        data1 = float (data["Total power consumption"].iloc[-1]) + value
        
    elif room == "bill": 
        data2 =  value
        
    elif room == "shared":
        data3 = float (data["Power consumption common area"].iloc[-1]) + value 
        
    elif room ==  "room1": 
        data4 = float (data["Power consumption room 1"].iloc[-1]) + value
        
    elif room == "room2":     
        data5 = float (data["Power consumption room 2"].iloc[-1]) + value
        
    elif room == "room3":
        data6 = float (data["Power consumption room 3"].iloc[-1]) + value
            
    elif room == "room4":
        data7 = float (data["Power consumption room 6"].iloc[-1]) + value  
       
    elif room == "room5": 
       data8 = float (data["Power consumption room 5"].iloc[-1]) + value
    
    elif room == "room6":
        data9 = float (data["Power consumption room 6"].iloc[-1]) + value
        
    data1 = (data3 + data4 + data5 + data6 + data7 + data8 + data9)  
    data1 = round (data1,2)
    with open ('TempDayFile.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["lastUpdated :" +  str (Now()), data0,data1,data2,data3,data4,data5,data6,data7,data8,data9])
        



    
#lager filer som trengs for å lagre og regne ut strøm forbruk     
def MakeFilesPower():
    """Create all the files neccecery for PowerFunc to run."""
    HeadlineDay()                                 
    HeadlineWeek()                                
    HeadlineMonth()                               
    HeadlineYear()   
    TempHeadlineDay()
    TempHeadlineWeek()
    TempHeadlineMonth()
    TempHeadlineYear()
 #   print ("Files created.")






#  denne funksjonen lagrer verdiene rett ifra TempDayFile, ved å lese av verdiene som er nederst.
#  og skriver det til en Csv fil. 


def SaveDay():
    """Takes the last data from TempDayFile and saves it to A_DayLog"""
    data = pd.read_csv("TempDayFile.csv",sep=";",error_bad_lines=False)
 
    data0 = float (data["Power generated"].iloc[-1])
    data1 = float (data["Total power consumption"].iloc[-1]) 
    data2 = float (data["Electricity bill in kr"].iloc[-1])
    data3 = float (data["Power consumption common area"].iloc[-1])
    data4 = float (data["Power consumption room 1"].iloc[-1]) 
    data5 = float (data["Power consumption room 2"].iloc[-1])
    data6 = float (data["Power consumption room 3"].iloc[-1])
    data7 = float (data["Power consumption room 6"].iloc[-1])
    data8 = float (data["Power consumption room 5"].iloc[-1])  
    data9 = float (data["Power consumption room 6"].iloc[-1])  
    
 
    
    with open ('A_Daylog.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Day " + str (YesterDayDate()),data0,data1,data2,data3,data4,data5,data6,data7,data8,data9])
     


    
# de fire funksjonene nedenfor gjør det samme men skriver til en annen fil            
# funksjonen sjekker om alt er int før den skriver det til en uke, mnd eller år
# den lagrer ved å lese av den siste verdien i fila. 
# den siste verdien er funnet ved funksjonene  KWHSaveWeek/month/year (som leser av  sist verdi og adderer med slutten av dagens verdi)
# den lagrer dette til en permanent fil itilfelle COT går ned eller at man behøved å se på data lengre enn COT lagrer det.        
            
def SaveWeek():
    """Takes the last data from TempWeekFile and saves it to A_Weeklog"""   
     
    data = pd.read_csv("TempWeekFile.csv",sep=";",error_bad_lines=False)
 
    data0 = float (data["Power generated"].iloc[-1])
    data1 = float (data["Total power consumption"].iloc[-1]) 
    data2 = float (data["Electricity bill in kr"].iloc[-1])
    data3 = float (data["Power consumption common area"].iloc[-1])
    data4 = float (data["Power consumption room 1"].iloc[-1]) 
    data5 = float (data["Power consumption room 2"].iloc[-1])
    data6 = float (data["Power consumption room 3"].iloc[-1])
    data7 = float (data["Power consumption room 6"].iloc[-1])
    data8 = float (data["Power consumption room 5"].iloc[-1])  
    data9 = float (data["Power consumption room 6"].iloc[-1])  
    
 
    
    with open ('A_Weeklog.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Week " + str (LastWeekNumber()),data0,data1,data2,data3,data4,data5,data6,data7,data8,data9])
     
   
def SaveMonth():
    """Takes the last data from TempMonthFile and saves it to A_Monthlog"""   
    data = pd.read_csv("TempMonthFile.csv",sep=";",error_bad_lines=False)
    
    data0 = float (data["Power generated"].iloc[-1])
    data1 = float (data["Total power consumption"].iloc[-1]) 
    data2 = float (data["Electricity bill in kr"].iloc[-1])
    data3 = float (data["Power consumption common area"].iloc[-1])
    data4 = float (data["Power consumption room 1"].iloc[-1]) 
    data5 = float (data["Power consumption room 2"].iloc[-1])
    data6 = float (data["Power consumption room 3"].iloc[-1])
    data7 = float (data["Power consumption room 6"].iloc[-1])
    data8 = float (data["Power consumption room 5"].iloc[-1])  
    data9 = float (data["Power consumption room 6"].iloc[-1])
    
    with open ('A_Monthlog.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Month " + str (LastMonthNumber()),data0,data1,data2,data3,data4,data5,data6,data7,data8,data9])
    
      
    
def SaveYear():
   """Takes the last data from TempYearFile and saves it to A_Yearlog"""
    
   data = pd.read_csv("TempYearFile.csv",sep=";",error_bad_lines=False)

   data0 = float (data["Power generated"].iloc[-1])
   data1 = float (data["Total power consumption"].iloc[-1]) 
   data2 = float (data["Electricity bill in kr"].iloc[-1])
   data3 = float (data["Power consumption common area"].iloc[-1])
   data4 = float (data["Power consumption room 1"].iloc[-1]) 
   data5 = float (data["Power consumption room 2"].iloc[-1])
   data6 = float (data["Power consumption room 3"].iloc[-1])
   data7 = float (data["Power consumption room 6"].iloc[-1])
   data8 = float (data["Power consumption room 5"].iloc[-1])  
   data9 = float (data["Power consumption room 6"].iloc[-1])  

   with open ('A_Yearlog.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Year " + str (LastYear()),data0,data1,data2,data3,data4,data5,data6,data7,data8,data9])

    
 
# de fire funksjonene nedenfor gjør det samme men skriver til en annen fil
# oppgaven til funksjonene er å lage en fil med et oppsatt oppsett som er forhåndsbestemt for lett filmanipulering 
# som en bonus så skriver den også når funksjonen blir kjørt.. 
 
def TempHeadlineDay():
    """Checks if TempDayFile exist, if not, then creates it."""
  
    if os.path.isfile('TempDayFile.csv'):
            return
    else:
        with open('TempDayFile.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["date started " + str (date.today()),"Power generated","Total power consumption","Electricity bill in kr","Power consumption common area",\
                        "Power consumption room 1","Power consumption room 2","Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])
            writer.writerow(["----------",0,0,0,0,0,0,0,0,0,0])

       
def TempHeadlineWeek():
    """Checks if TempWeekFile exist, if not, then creates it."""
    if os.path.isfile('TempWeekFile.csv'):
            return
    else:
        with open('TempWeekFile.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["date started " + str (date.today()),"Power generated","Total power consumption","Electricity bill in kr","Power consumption common area",\
                        "Power consumption room 1","Power consumption room 2","Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])
            writer.writerow(["----------",0,0,0,0,0,0,0,0,0,0])
       

def TempHeadlineMonth():
    """Checks if TempMonthFile exist, if not, then creates it."""    
    if os.path.isfile('TempMonthFile.csv'):
            return
    else:
        with open('TempMonthFile.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["date started " + str (date.today()),"Power generated","Total power consumption","Electricity bill in kr","Power consumption common area",\
                        "Power consumption room 1","Power consumption room 2","Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])
            writer.writerow(["----------",0,0,0,0,0,0,0,0,0,0])


def TempHeadlineYear():
    """Checks if TempYearFile exist, if not, then creates it."""
    if os.path.isfile('TempYearFile.csv'):
            return
    else:
        with open('TempYearFile.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["date started " + str (date.today()),"Power generated","Total power consumption","Electricity bill in kr","Power consumption common area",\
                        "Power consumption room 1","Power consumption room 2","Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])
            writer.writerow(["----------",0,0,0,0,0,0,0,0,0,0])




# de fire funksjonene nedenfor gjør det samme men skriver til en annen fil
# oppgaven til funksjonen er å resette, lage blanke filer med overskrift som er lik "tempheadline",
# for å gjøre filene klar for ny uke, mnd eller år. 
# funksjonen sjekker om filen eksistere, om den ikke eksistere så lager den, den


def ResetTempHeadDay():
    """Resets TempDayFile and putting all values to zero."""
    DeleteFile("TempDayFile.csv")
    with open ("TempDayFile.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["date started " + str (date.today()),"Power generated","Total power consumption","Electricity bill in kr","Power consumption common area",\
                         "Power consumption room 1","Power consumption room 2","Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])
        writer.writerow(["----------",0,0,0,0,0,0,0,0,0,0])
    
    

def ResetTempHeadlineWeek():
    """Resets TempWeekFile and putting all values to zero."""
    DeleteFile("TempWeekFile.csv")
    with open ("TempWeekFile.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["date started " + str (date.today()),"Power generated","Total power consumption","Electricity bill in kr","Power consumption common area",\
                         "Power consumption room 1","Power consumption room 2","Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])
        writer.writerow(["----------",0,0,0,0,0,0,0,0,0,0])


def ResetTempHeadlineMonth():
    """Resets TempMonthFile and putting all values to zero."""
    DeleteFile("TempMonthFile.csv")
    with open ("TempMonthFile.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["date started " + str (date.today()),"Power generated","Total power consumption","Electricity bill in kr","Power consumption common area",\
                         "Power consumption room 1","Power consumption room 2","Power consumption room 3",   "Power consumption room 4","Power consumption room 5","Power consumption room 6"])
        writer.writerow(["----------",0,0,0,0,0,0,0,0,0,0])
      
      
def ResetTempHeadlineYear(): 
    """Resets TempYearFile and putting all values to zero."""
    DeleteFile("TempYearFile.csv")
    with open ("TempYearFile.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["date started " + str (date.today()),"Power generated","Total power consumption","Electricity bill in kr","Power consumption common area",\
                     "Power consumption room 1","Power consumption room 2","Power consumption room 3",   "Power consumption room 6","Power consumption room 5","Power consumption room 6"])
        writer.writerow(["----------",0,0,0,0,0,0,0,0,0,0])
          
        

# de tre funksjonene nedenfor gjør det samme men skriver til en annen fil
# meningen er å kjøre disse 3 funksjonene etter dagen er omme, Rett før RESET 

def KWHSaveWeek():
    """Opens up TempWeekFile, reads the last lines, adds it up with the last lines of TempDayFile and writes it to  TempWeekFile."""
    dataweek = pd.read_csv("TempWeekFile.csv",sep=";",error_bad_lines=False)
    dataday = pd.read_csv("TempDayFile.csv",sep=";",error_bad_lines=False)
   
    
    data0 = float (dataweek["Power generated"].iloc[-1]) + float (dataday["Power generated"].iloc[-1])
    data1 = float (dataweek["Total power consumption"].iloc[-1])  + float (dataday["Total power consumption"].iloc[-1])
    data2 = float (dataweek["Electricity bill in kr"].iloc[-1])            + float (dataday["Electricity bill in kr"].iloc[-1]) 
    data3 = float (dataweek["Power consumption common area"].iloc[-1])    + float (dataday["Power consumption common area"].iloc[-1])
    data4 = float (dataweek["Power consumption room 1"].iloc[-1])     + float (dataday["Power consumption room 1"].iloc[-1])
    data5 = float (dataweek["Power consumption room 2"].iloc[-1])     + float (dataday["Power consumption room 2"].iloc[-1]) 
    data6 = float (dataweek["Power consumption room 3"].iloc[-1])     + float (dataday["Power consumption room 3"].iloc[-1])
    data7 = float (dataweek["Power consumption room 6"].iloc[-1])    + float (dataday["Power consumption room 6"].iloc[-1])
    data8 = float (dataweek["Power consumption room 5"].iloc[-1])    + float (dataday["Power consumption room 5"].iloc[-1])
    data9 = float (dataweek["Power consumption room 6"].iloc[-1])    + float (dataday["Power consumption room 6"].iloc[-1])
   
    with open ('TempWeekFile.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["date updated " + str (YesterDayDate()),data0,data1,data2,data3,data4,data5,data6,data7,data8,data9])
        




def KWHSaveMonth():
    """Opens up TempMonthFile, reads the last lines, adds it up with the last lines of TempDayFile and writes it to  TempMonthFile."""
    datamonth = pd.read_csv("TempMonthFile.csv",sep=";",error_bad_lines=False)
    dataday = pd.read_csv("TempDayFile.csv",sep=";",error_bad_lines=False)
   
    
    data0 = float (datamonth["Power generated"].iloc[-1]) + float (dataday["Power generated"].iloc[-1])
    data1 = float (datamonth["Total power consumption"].iloc[-1])  + float (dataday["Total power consumption"].iloc[-1])
    data2 = float (datamonth["Electricity bill in kr"].iloc[-1])            + float (dataday["Electricity bill in kr"].iloc[-1]) 
    data3 = float (datamonth["Power consumption common area"].iloc[-1])    + float (dataday["Power consumption common area"].iloc[-1])
    data4 = float (datamonth["Power consumption room 1"].iloc[-1])     + float (dataday["Power consumption room 1"].iloc[-1])
    data5 = float (datamonth["Power consumption room 2"].iloc[-1])     + float (dataday["Power consumption room 2"].iloc[-1]) 
    data6 = float (datamonth["Power consumption room 3"].iloc[-1])     + float (dataday["Power consumption room 3"].iloc[-1])
    data7 = float (datamonth["Power consumption room 6"].iloc[-1])    + float (dataday["Power consumption room 6"].iloc[-1])
    data8 = float (datamonth["Power consumption room 5"].iloc[-1])    + float (dataday["Power consumption room 5"].iloc[-1])
    data9 = float (datamonth["Power consumption room 6"].iloc[-1])    + float (dataday["Power consumption room 6"].iloc[-1])
    
    with open ('TempMonthFile.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["date updated " + str (YesterDayDate()),data0,data1,data2,data3,data4,data5,data6,data7,data8,data9])
        
  
        
def KWHSaveYear():
    """Opens up TempYearFile, reads the last lines, adds it up with the last lines of TempDayFile and writes it to  TempYearFile."""
    datayear = pd.read_csv("TempYearFile.csv",sep=";",error_bad_lines=False)
    dataday = pd.read_csv("TempDayFile.csv",sep=";",error_bad_lines=False)
   
    
    data0 = float (datayear["Power generated"].iloc[-1]) + float (dataday["Power generated"].iloc[-1])
    data1 = float (datayear["Total power consumption"].iloc[-1])  + float (dataday["Total power consumption"].iloc[-1])
    data2 = float (datayear["Electricity bill in kr"].iloc[-1])            + float (dataday["Electricity bill in kr"].iloc[-1]) 
    data3 = float (datayear["Power consumption common area"].iloc[-1])    + float (dataday["Power consumption common area"].iloc[-1])
    data4 = float (datayear["Power consumption room 1"].iloc[-1])     + float (dataday["Power consumption room 1"].iloc[-1])
    data5 = float (datayear["Power consumption room 2"].iloc[-1])     + float (dataday["Power consumption room 2"].iloc[-1]) 
    data6 = float (datayear["Power consumption room 3"].iloc[-1])     + float (dataday["Power consumption room 3"].iloc[-1])
    data7 = float (datayear["Power consumption room 6"].iloc[-1])    + float (dataday["Power consumption room 6"].iloc[-1])
    data8 = float (datayear["Power consumption room 5"].iloc[-1])    + float (dataday["Power consumption room 5"].iloc[-1])
    data9 = float (datayear["Power consumption room 6"].iloc[-1])    + float (dataday["Power consumption room 6"].iloc[-1])
    
    with open ('TempYearFile.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["date updated " + str (YesterDayDate()),data0,data1,data2,data3,data4,data5,data6,data7,data8,data9])

    

#-------------------------------

#nedenfor er for å skrive til Cot 

def WriteToCot():
    """Writes the last line of TempDayFile to Circuit of things."""
    dataday = pd.read_csv("TempDayFile.csv",sep=";",error_bad_lines=False)
    dataweek = pd.read_csv("TempWeekFile.csv",sep=";", error_bad_lines=False)
    datalastweek = pd.read_csv("A_Weeklog.csv",sep=";", error_bad_lines=False)
    
    try: 
        datalastweek = float (datalastweek["Electricity bill in kr"].iloc[-1])  # prisen forrige uke 
    except:
        datalastweek = 0                                          # den første uka fins det ingen verdi, blir satt til 0 om  den ikke får til å hente ut en verdi
        
    data0 = float (dataweek["Power generated"].iloc[-1]) + float (dataday["Power generated"].iloc[-1])
    data1 = float (dataweek["Total power consumption"].iloc[-1])  + float (dataday["Total power consumption"].iloc[-1])
    data2 = float (dataweek["Electricity bill in kr"].iloc[-1])            + float (dataday["Electricity bill in kr"].iloc[-1]) 
    data3 = float (dataweek["Power consumption common area"].iloc[-1])    + float (dataday["Power consumption common area"].iloc[-1])
    data4 = float (dataweek["Power consumption room 1"].iloc[-1])     + float (dataday["Power consumption room 1"].iloc[-1])
    data5 = float (dataweek["Power consumption room 2"].iloc[-1])     + float (dataday["Power consumption room 2"].iloc[-1]) 
    data6 = float (dataweek["Power consumption room 3"].iloc[-1])     + float (dataday["Power consumption room 3"].iloc[-1])
    data7 = float (dataweek["Power consumption room 6"].iloc[-1])    + float (dataday["Power consumption room 6"].iloc[-1])
    data8 = float (dataweek["Power consumption room 5"].iloc[-1])    + float (dataday["Power consumption room 5"].iloc[-1])
    data9 = float (dataweek["Power consumption room 6"].iloc[-1])    + float (dataday["Power consumption room 6"].iloc[-1])
    
    
    SI.PowerGenWeek.write(round (data0,2))
    SI.PowerConsumeWeek.write(round(data1,2))
    SI.PowerBill.write(round(data2,2))
    SI.PowerConsumeShare.write(round(data3,2))
    SI.PowerConsole1.write(round(data4,2))
    SI.PowerConsole2.write(round(data5,2))
    SI.PowerConsole3.write(round(data6,2))
    SI.PowerConsole4.write(round(data7,2))
    SI.PowerConsole5.write(round(data8,2))
    SI.PowerConsole6.write(round(data9,2)) 
    SI.LastWeekBill.write(round(datalastweek,2))





# funksjonen nedenfor er kun til for å lage et unøyaktig estimat. 
# Den er kun for å skrive til cot for å vise + skrive 2 uker på A_weeklylog.
# gjentar. funksjonen bruker ikke alle variablene selve hovedprogrammet bruker
# den er utrolig unøyaktig og forenkelt kun for 

# funksjonen nedenfor skal simulerer en ukers forbruk, dette kommer ikke til å 
# være nøyaktig, den skal lagre 2 ganger, en gang uten spareløsninger og en dag med. 
# simuleringa tar ikke hensyn til alle sparefunksjonene, og er kun ment for å vise hvordan det blir vist på dashboard + lagring over tid
# og for å vise at det går ann å spare med enkle grep.
def simulation():

    # lys blir satt til 16 timer per rom, Temp blir satt til 23 grader, og 16 grader ute. (alt over 12timer går til halv effekt)
    # strøm generering blir satt til 8 timer og 50% skyer
    # alle beboerne spiser frok ost 15 min , lunch 15min , middag 20 min  og kveldsmat 15min
    # alle beboerne vasker klær 1 gang iløpe av uka, og en felles
    # lys på stue, kjøkken, bad er kun på når det er booket på sparing, alltid på om ikke
    # alle beboerne bruker badet 30 min annenhver dag og de siste tre dagene   * 15 min 
    # tv stue blir brukt 50 min hverdag av hver person 
    # størmprisen blir satt til (150 * 12)/365) * 7 +  (  0,24 + 0,53  ) * kwh tot forbruk - kwh generering= 
    # sparing på temp er 18 grader, det er "konstant 16 grader ute i disse 1-2 uker" 
    # på soverommet blir kun temp, lys tatt henyn til 
    
    MakeFilesPower()  #lager filer slik at det ikke crasher 
    #strøm genering
    AnualSun = (200000/(365*24))            # i norge 200k/ (365*24)  får time KWH 
    Area = 109.11                           # total areal kvm med solcellepanel
    Efficiency = (19.7/100)                 # 19,7%  effektfaktor 
    PreformanceRatio = 1                    # minus cloud()  pf,  Performance ratio 
    CloudPercentage = 0.5 
    kilo = 1000                             
    time = 8 * 7                            # åtte timer , sju dager uka 
                   #  blir satt til 50% overskyet  
    powergen = (AnualSun * Area *  Efficiency  * (PreformanceRatio- CloudPercentage) )
    powergen = (powergen / kilo) 
    powergen = powergen * time 


    #siden alle personer bruker alt likt kan dette copy pastes til data 
    bulbs = 0.009*3  # kwh 
    lyspower = 12 * 7 *bulbs       # tolv timer, sju dager uka 
    lyspowerspare  = 8 * 7 * bulbs + 4*7*bulbs  # 4 timer sparing 
        
    Washingmachine = 1 # kwh 
    #heating 
    Wattused       = (60/1000)
    RoomSizeKWh    = (12 * Wattused )   
    heatingbedroom  = (RoomSizeKWh  * 0.30)    # 0.3 effekt siden 7 grader differanse 
    heatingbedroomnosave = 168*heatingbedroom
    heatingbedroomsave   = 119*heatingbedroom +( 49*RoomSizeKWh*0.2) # differansen er mindre enn 5 
    
    #booking power
    shower  = 39.74 
    tv      = 0.12
    kitch   = 2.04
    booking = shower + tv + kitch 
    

    
    person = Washingmachine  + booking + heatingbedroomnosave + lyspower 
    personspar = Washingmachine + booking + heatingbedroomsave + lyspowerspare
    
    #felles 

    heatingshared = (2 *RoomSizeKWh  * 0.30)  # dobbelt så stort rom
    heatingsharednosave = 168 * heatingshared 
    heatingsharedsaved  = 119 * heatingshared + 49 * (2*RoomSizeKWh * 0.2) # diffreansen er mindre enn 5 grader med sparing på 
         
    #lys 
    totbulb = 6+6+5 
    BookedHours = 58 
    lightnosave = totbulb * 0.009 * 24 * 7
    lightsave   = totbulb * 0.009 * BookedHours
    
    #oppvaskmaskin
    # 7*frokost, 7*lunch, 7*middag, 7*kvelds
    #  70 + 105 + 140 + 70   = 385  = 4 -5 ganger kjørt 
    Dishwasher = 5 * 1 #1 kwh 
    fridge = 0.0164  * 24 * 7    #kwh
    freezer = 0.0305  * 24 * 7   #kwh    
    
    #bathroomheat 
    BathroomSize = 6
    ConsumeLow   = 0.12 *  BathroomSize #kwh
    ConsumeHigh  = 0.15 *  BathroomSize #kwh 
    
    Consumenosave = ConsumeHigh * 24*7 
    consumesave   = ConsumeHigh * 119 + 49 * ConsumeLow
    
    felles = lightnosave + Consumenosave + freezer + Dishwasher + fridge + heatingsharednosave
    fellessparing = consumesave + freezer + fridge + Dishwasher + lightsave +heatingsharedsaved
    
    
    
    
   

    
    data0 = float (powergen)
    data1 = float (0)
    data2 = float (0) 
    data3 = float (felles)   
    data4 = float (person)     
    data5 = float (person)
    data6 = float (person) 
    data7 = float (person) 
    data8 = float (person)    
    data9 = float (person)
    data1 = (data3 + data4 + data5 + data6 + data7 + data8 + data9)  
    data1 = round (data1,2)
    data2 = (float (data1)-data0)*( 0.24 + 0.5)
    data2 = data2 + ((150 * 12)/365) * 7
    with open ('TempWeekFile.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["SIMULATION without saving " ,data0,data1,data2,data3,data4,data5,data6,data7,data8,data9])
        
    SaveWeek()
    datalastweek = pd.read_csv("A_Weeklog.csv",sep=";", error_bad_lines=False)    
    datalastweek = float (datalastweek["Electricity bill in kr"].iloc[-1])
    
   
    
    
    data0 = float (powergen)
    data1 = float (0)
    data2 = float (0) 
    data3 = float (fellessparing)   
    data4 = float (personspar)     
    data5 = float (personspar)
    data6 = float (personspar) 
    data7 = float (personspar) 
    data8 = float (personspar)    
    data9 = float (personspar)
    data1 = (data3 + data4 + data5 + data6 + data7 + data8 + data9)  
    data1 = round (data1,2)
    data2 = (data1-data0)*( 0.24 + 0.5)
    data2 = data2 + ((150 * 12)/365) * 7
    with open ('TempWeekFile.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["SIMULATION saving power " ,data0,data1,data2,data3,data4,data5,data6,data7,data8,data9])
        
    SaveWeek()
    

    #skriver sparinge uka til COT for å vise 
    
    SI.PowerGenWeek.write(round (data0,2))
    SI.PowerConsumeWeek.write(round(data1,2))
    SI.PowerBill.write(round(data2,2))
    SI.PowerConsumeShare.write(round(data3,2))
    SI.PowerConsole1.write(round(data4,2))
    SI.PowerConsole2.write(round(data5,2))
    SI.PowerConsole3.write(round(data6,2))
    SI.PowerConsole4.write(round(data7,2))
    SI.PowerConsole5.write(round(data8,2))
    SI.PowerConsole6.write(round(data9,2)) 
    SI.LastWeekBill.write(datalastweek)
    
