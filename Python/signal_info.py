from classes import Signal
TokenShared     = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1NzQ1In0.Qaa1HRun8lFNpWUQLYHew32WjxhEt9-gGFa7RoFBKNE'  #token til fellessignalene-COT
TokenConsole1   = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI0OTA1In0.FqhA0PdOWJeK0jbwW6_MtgJD7rZBQD3lA8ibur2BG6Y'  #token til konsoll 1-COT
TokenConsole2   = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI2MTg4In0.SrE-Gnlav_MVEO8Tv54Leg0j5Sec7WmS18ZvAvXiLBU'  #token til konsoll 2-COT
TokenGen        = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI0ODk4In0.tYZTfap3G90Kgd3Zj7-kckkdDAqYkrHZIejeeBphlCA'  #token til strømgenererings-COT 
TokenConsume    = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1OTUzIn0.mwPCKQyglMAkg3pPKcbTCp2Uu2xIfWbbc716p2DEvQ0'  #token til strømforbruk-COT 


# Signaler som bruker fellesbrukeren i CoT
NightSignal     = Signal('NightSignal','25120',TokenShared)         # Nattsignal som forteller om det er dag/natt (0/1).
BathroomLight   = Signal('BathroomLight','16834',TokenShared)       # Om lyset er på på badet
TempBathroom    = Signal('TempBathroom','3828',TokenShared )        # Temperaturen på badet

# Signaler som viser om et rom er opptatt eller ikke
LivingRoomState = Signal("LivingRoomState","17737",TokenShared)     # Om det er noen i stua
KitchenState    = Signal("KitchenState", "3344",TokenShared)        # Om det er noen på kjøkkenet
BathroomState   = Signal("BathroomState","10990",TokenShared)       # Om det er noen på badet
TempSharedSpace = Signal('TempSharedSpace','11649',TokenShared)     # Temperaturen i stua og på kjøkkenet
SharedSpaceLight= Signal("SharedSpaceLight", "12361",TokenShared)   # Om lyset er på i stua og på kjøkkenet
                                 
# Signaler som bruker CoT-brukeren til konsoll 1
Console1        = Signal('Console1','15685',TokenConsole1,'Lars')   # Booking-/smittesporingssignal til konsoll 1
Tracking1_3_5   = Signal('Tracking1_3_5','27533',TokenConsole1)     # Forteller om beboer 1 er hjemme
TempRoom1_3_5   = Signal('TempRoom1_3_5','25341',TokenConsole1)     # Temperaturen på soverom 1, 3 og 5
FanRoom1_3_5    = Signal('FanRoom1_3_5','20023',TokenConsole1)      # Gir info om viften på soverom 1, 3 og 5

# Signaler som bruker CoT-brukeren til konsoll 2
Console2        = Signal('Console2','13576',TokenConsole2,'Dennis') # Booking-/smittesporingssignal til konsoll 2
Tracking2_4_6   = Signal('Tracking2_4_6','28655',TokenConsole2)     # Forteller om beboer 2 er hjemme
TempRoom2_4_6   = Signal('TempRoom2_4_6','13945',TokenConsole2)     # Temperaturen på soverom 2, 4 og 6
FanRoom2_4_6    = Signal('FanRoom2_4_6','19908',TokenConsole2)      # Gir info om viften på soverom 1, 3 og 5

# Bruker kun to konsoller, men resterende fire konsoller kan legges til slik:
# Console3        = Signal('Console3','',TokenShared,'Marius H.')
# Console4        = Signal('Console4','',TokenShared,'Marius M.')
# Console5        = Signal('Console5','',TokenShared,'Njal')
# Console6        = Signal('Console6','',TokenShared,'Jonas')

# Liste som holder alle konsollene
all_consoles = [Console1, Console2]


# Nedenfor er for å skrive/lese strøm generert til COT
PowerGenWeek  = Signal('GenWeek','26596',TokenGen)

# Nedenfor er for å skrive/lese strøm brukt til COT 
PowerConsumeWeek    = Signal('PowerConsumeWeek','22509',TokenConsume)
PowerConsumeShare   = Signal('PowerConsumeShare','4782',TokenConsume)
PowerConsole1       = Signal('PowerConsole1','25229',TokenConsume)
PowerConsole2       = Signal('PowerConsole2','17296',TokenConsume)
PowerConsole3       = Signal('PowerConsole3','1523',TokenConsume)
PowerConsole4       = Signal('PowerConsole4','14136',TokenConsume)
PowerConsole5       = Signal('PowerConsole5','19972',TokenConsume)
PowerConsole6       = Signal('PowerConsole6','18420',TokenConsume)

# Her skal det bli en COT som har strømpriser/strømregning
PowerBill           = Signal('PowerBill','15092',TokenGen)      # her skal strøm regninga stå , resetter hver dag
PowerPrice          = Signal('PowerPrice','30760',TokenGen)     # her skal timepris for strømregning stå  
LastWeekBill        = Signal('LastWeekBill','23738',TokenGen)   # forrige ukers strømregning                                                  
                                                        
                                                        
                                                        
                                                        
                                                        
                                                        