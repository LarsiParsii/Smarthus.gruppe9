import datetime as dt

def TimePrint(msg):
    '''Takes an input and combines it with a timestamp, then prints it.'''
    
    now = dt.datetime.now().strftime('%x %X')
    print(f"[{now}] {msg}")