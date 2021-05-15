from PowerFunc import HourCheck
from PowerFunc import MakeFilesPower
from print_func import TimePrint
import booking_func
import signal_info as SI
import schedule
import time

MakeFilesPower() # denne må være her om du ikke ønsker feilmeldning ved start
# den funksjonen ovenfor lager filer som trengs. 

def CheckConsoles():
    '''Reads all booking/guest tracking signals and stores their values.
       The first digit in each signal decides what function to run.'''
    
    for signal in SI.all_consoles:
        signal.refresh()
        
        if signal.value[0] in ['1','2','3']:
            # Bookingfunksjon
            TimePrint("\n[KJØRER BOOKING]")
            booking_func.Booking(signal)
        
        elif signal.value[0] in ['5','6','7']:
            # Loggføring av gjester
            TimePrint("\n[KJØRER SMITTESPORING]")
            booking_func.GuestTracking(signal)
        
        elif signal.value[0] == '8':
            # Nødbooking av bad (15 min)
            TimePrint("\n[KJØRER NØDBOOKING]")
            booking_func.QuickBooking(signal)

def SetDay():
    '''Increases temperatures and sets NightSignal to "0".'''
    
    TimePrint("Det er nå DAG.")
    SI.NightSignal.write(0)
    SI.TempBathroom.write(23)
    SI.TempSharedSpace.write(23)



def SetNight():
    '''Decreases temperatures and sets NightSignal to "1".'''
    
    TimePrint("Det er nå NATT.")
    SI.NightSignal.write(1)
    SI.TempBathroom.write(18)
    SI.TempSharedSpace.write(18)

def CheckLogs():
    '''Deletes the bookings.csv file, and iterates over the GuestTracker.csv file,
       removing entries older than 14 days.'''
       
    TimePrint("Sletter bookingfil.")
    booking_func.DeleteFile('bookings.csv')
    booking_func.DeleteOldListing()


# Kjører riktig dag-/nattfunksjon ved oppstart.
if 6 <= int(HourCheck()) < 23:
    SetDay()
else:
    SetNight()

# Oppgaver som må bli kjørt .
schedule.every(5).seconds.do(CheckConsoles)
schedule.every(1).minutes.do(booking_func.CheckRoomsNow)
schedule.every().day.at("23:00").do(SetNight)
schedule.every().day.at("06:00").do(SetDay)
schedule.every().day.at("23:59").do(CheckLogs)


def run_main():
    '''Hovedprogrammet som kjører oppgaver definert ovenfor.'''
    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    run_main()





