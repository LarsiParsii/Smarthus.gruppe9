import PowerFunc as PF
import datetime as dt
import csv
import os
import signal_info as SI

def CheckCsvExists(filename, header):
    '''Takes a CSV file name and header and checks if the file exists. It does not exist
       it creates the file with the header (list of column names) given as a parameter.'''
       
    file_exists = os.path.isfile(filename)
    
    if not file_exists:
        print(f'Oppretter filen "{filename}"')
        with open(filename, 'w+', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(header)



def CheckBooking(request_room, request_start_time, request_end_time):
    '''Checks if an entry matching the given room in the given time period
       already exists in bookings.csv file.'''
    
    Counter = 0
    # Her angis hvor mange kan være i hvert rom
    MaxGuestsInRoom = {'Bad': 1, 'Kjokken': 2, 'Stue': 3}
    
    # Sjekk om rommet ikke allerede er booket
    with open('bookings.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        
        # Gå gjennom hver rad i bookingfila
        for row in reader:
            
            # Det er kun oppføringer i samme rom som skal sammenlignes
            if row['room'] == request_room:
                               
                lookup_start_time = dt.datetime.strptime(row['start_time'], '%H:%M').time()
                lookup_end_time = dt.datetime.strptime(row['end_time'], '%H:%M').time()
                
                # Overlappende bookinger, returner False dersom det er flere enn
                # maks antall tilatte i rommet.
                if not (request_end_time <= lookup_start_time or request_start_time >= lookup_end_time):
                    Counter += 1
                    
                    if Counter >= MaxGuestsInRoom[request_room]:
                        return False
        
        #Ingen overlappende bookinger, returner True
        return True


def CheckRoomsNow():
    '''Checks how many residents are in the living room, kitchen or bathroom at
       any given time and writes this to CoT.'''
    
    # print("Oppdaterer romstatus...")
    BathroomCounter   = 0
    KitchenCounter    = 0 
    LivingRoomCounter = 0
    CheckCsvExists('bookings.csv', ['room', 'start_time', 'end_time', 'duration', 'user'])
    
    with open('bookings.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        
        # Gå gjennom hver rad i bookingfila
        for row in reader:
            lookup_start_time = dt.datetime.strptime(row['start_time'], '%H:%M').time()
            lookup_end_time = dt.datetime.strptime(row['end_time'], '%H:%M').time()
            TimeNow = dt.datetime.now().time()
            
            # sjekker stue, bad og kjøkken om de er booket dette øyeblikket, deretter skriver til COT 0 eller 1. 
            # 0 = ledig , 1 = en person, 2 = to person, 3 = tre person 
            if row['room'] == "Bad":
                if not (TimeNow  <= lookup_start_time or TimeNow >= lookup_end_time):
                    BathroomCounter += 1 

            elif row['room'] == "Kjokken":
                if not (TimeNow  <= lookup_start_time or TimeNow >= lookup_end_time):
                    KitchenCounter += 1 

            elif row['room'] == "Stue":     
                if not (TimeNow  <= lookup_start_time or TimeNow >= lookup_end_time):
                    LivingRoomCounter += 1 

        SI.BathroomState.write(BathroomCounter)
        SI.LivingRoomState.write(LivingRoomCounter)
        SI.KitchenState.write(KitchenCounter)




def DishwasherUsage(start_time):    
    '''Determines how full the dishwasher is after each booking of the kitchen.
       Fill level of dishwasher is dependent on the start time of the booking.'''
    
    BreakfastStartTime = dt.time(5)
    LunchStartTime = dt.time(10)
    DinnerStartTime = dt.time(15)
    SupperStartTime = dt.time(20)
    add_usage = 0 
        
    if BreakfastStartTime <= start_time < LunchStartTime:
        # Frokost
        add_usage = 10
    elif LunchStartTime <= start_time < DinnerStartTime:
        # Lunsj
        add_usage = 15
    elif DinnerStartTime <= start_time < SupperStartTime:
        # Middag
        add_usage = 20
    elif SupperStartTime <= start_time < dt.time(23,59,59):
        # Kvelds-/nattmat (før midnatt)
        add_usage = 10
    elif dt.time(0) <= start_time < BreakfastStartTime:
        # Kvelds-/nattmat (etter midnatt)
        add_usage = 10
    
    print(f"Added {add_usage}% to dishwasher fill level.")
    PF.DishWasherFile(add_usage)


def AddBooking(room, start_time, end_time, request_duration, user):
    '''Adds an entry to the bookings.csv file. Time paramters are given as
       datetime objects.'''
       
    with open('bookings.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([room, start_time.strftime('%H:%M'), end_time.strftime('%H:%M'), request_duration, user])


def Booking(request):
    '''Takes a signal class instance as a parameter and decomposes the signal,
       checking it against the bookings.csv file. The request is added if the
       room is available at the requested time.
    '''
    
    # Lag booking-filen om den ikke eksisterer
    CheckCsvExists('bookings.csv', ['room', 'start_time', 'end_time', 'duration', 'user'])
    
    room_list = {'1':'Bad', '2':'Kjokken', '3':'Stue'}    
    request_room = room_list[request.value[0]]    
    request_start_time = dt.datetime.strptime(''.join(request.value[1:5]), '%H%M').time()
    request_end_time = dt.datetime.strptime(''.join(request.value[5:9]), '%H%M').time()
    
    
    request_duration = round((((dt.datetime.combine(dt.datetime.today(), request_end_time) -
                        dt.datetime.combine(dt.datetime.today(), request_start_time)).seconds) / 3600), 2)
    
    print("------[Bookingforespørsel mottat]------")
    print(f"\
          Beboer:\t {request.user} \n\
          Rom:\t\t {request_room} \n\
          Starttid:\t {request_start_time} \n\
          Sluttid:\t {request_end_time} \n\
          Varighet:\t {request_duration} timer")
    
    if CheckBooking(request_room, request_start_time, request_end_time):
        AddBooking(request_room, request_start_time, request_end_time,
                   request_duration, request.user)
        print("------[BOOKING VELLYKKET]------")
        
        #Loggfør energiforbruk
        PF.KWHConsumed(request.name, request_room, request_duration)
        
        #Hvis kjøkkenet er booket, legg til bruk av oppvaskmaskinen
        if request_room == 'Kjokken':
            DishwasherUsage(request_start_time)
        
        # Oppdater antall perosner i hvert rom
        CheckRoomsNow()
        
        #Send "OK"-signal tilbake
        request.write(91)
    
    else:
        print("------[BOOKING MISLYKKET]------")
        
        #Send feilkode tilbake
        request.write(92)


def QuickBooking(request):
    '''Creates an "emergency booking" for the bathroom with a duration of 10 min.'''
    
    # Lag booking-filen om den ikke eksisterer
    CheckCsvExists('bookings.csv', ['room', 'start_time', 'end_time', 'duration', 'user'])
    
    request_room = 'Bad'    # Quick booking gjelder kun på bad
    request_duration = 0.166   # Quick booking gjelder kun 10 min = 0,166... timer
    
    request_start_time = dt.datetime.now()
    request_end_time = (request_start_time + dt.timedelta(hours=request_duration)).time()
    request_start_time = request_start_time.time()
    
    if CheckBooking(request_room, request_start_time, request_end_time):
        
        AddBooking(request_room, request_start_time, request_end_time,
                   request_duration, request.user)
        print("----[NØDBOOKING VELLYKKET]----")
        
        #Loggfør energiforbruk
        PF.KWHConsumed(request.name, request_room, request_duration)
        #Send "OK"-signal tilbake
        request.write(91)
    
    else:
        print("----[NØDBOOKING MISLYKKET]----")
        #Send feilkode tilbake
        request.write(92)
    


def CheckGuests(request_user, request_date, request_start_time, request_end_time):
    '''Checks if a resident already has a visitor in the given time period.'''
    
    # Sjekk om brukeren ikke allerede har lagt inn besøk i det gitte tidsrommet
    with open('GuestTracker.csv', 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        
        # Gå gjennom hver rad i fila
        for row in reader:
            # Det er kun oppføringene til brukeren som skal sjekkes
            if row['user'] == request_user:
                lookup_date = row['date']
                lookup_start_time = dt.datetime.strptime(row['start_time'], '%H:%M').time()
                lookup_end_time = dt.datetime.strptime(row['end_time'], '%H:%M').time()
                            
                # Besøk er allered lagt til, returner False
                if request_date == lookup_date:
                    if not (request_end_time <= lookup_start_time or
                            request_start_time >= lookup_end_time):
                        return False
        
        #Ingen overlappende bookinger, returner True
        return True


def AddGuests(user, date, start_time, end_time, duration, guests):
    '''Adds an entry to the GuestTracker.csv file. Time parameters are given as
       datetime objects.'''
    
    with open('GuestTracker.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([user, date, start_time.strftime('%H:%M'), end_time.strftime('%H:%M'), duration, guests])


def GuestTracking(request):
    '''Takes a signal class instance as a parameter and decomposes the signal,
       checking it against the GuestTracker.csv file. The request is added if
       there are no other visits assigned to the resident at the requested time.
    '''
    
    # Opprett smittesporingsfilen dersom den ikke eksisterer
    CheckCsvExists('GuestTracker.csv', ['user', 'date', 'start_time',
                     'end_time', 'duration', 'guests'])
    
    guest_dict          = {'5': '1 gjest', '6': '2 gjester', '7': '3 gjester'}
    request_guests      = guest_dict[request.value[0]]
    request_date        = dt.datetime.strftime(dt.date.today(), '%Y-%m-%d')
    request_start_time  = dt.datetime.strptime(''.join(request.value[1:5]), '%H%M').time()
    request_end_time    = dt.datetime.strptime(''.join(request.value[5:9]), '%H%M').time()
    request_duration    = round((((dt.datetime.combine(dt.datetime.today(), request_end_time) -
                                   dt.datetime.combine(dt.datetime.today(), request_start_time)).seconds) / 3600), 2)
        
    print("------[Besøksforespørsel mottat]------")
    print(f"\
          Beboer:\t {request.user} \n\
          Antall:\t {request_guests} \n\
          Starttid:\t {request_start_time} \n\
          Sluttid:\t {request_end_time} \n\
          Varighet:\t {request_duration} timer \n\
          Dato:\t\t {request_date}")
    
    if CheckGuests(request.user, request_date, request_start_time, request_end_time):
        AddGuests(request.user, request_date, request_start_time, request_end_time, request_duration, request_guests)
        print("-----------[BESØK LAGT TIL]-----------")
        # Send "OK"-signal tilbake
        request.write(91)
    
    else:
        print("-----[BESØK ALLEREDE LAGT TIL]-----")
        # Send feilkode tilbake
        request.write(92)


def DeleteFile(filename):
    '''Deletes given file'''
    if os.path.exists(filename):
      os.remove(filename)


def DeleteOldListing():
    '''Deletes entries older than 14 days'''
    
        # Ta vare på oppføringer under 14 dager
    day_limit = dt.date.today() - dt.timedelta(days=14)
    
    with open('GuestTracker.csv', 'r', newline='', encoding='utf-8') as file:
        rows = list(csv.reader(file, delimiter=';'))
    
    with open('GuestTracker.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['user', 'date', 'start_time', 'end_time', 'duration', 'guests'])
        
        for row in rows[1:]:
            lookup_date = dt.datetime.strptime(row[1], '%Y-%m-%d').date()
            if lookup_date >= day_limit:
                print(row)
                writer.writerow(row)



        
        
        
