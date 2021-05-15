# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 15:13:46 2021

@author: Marius
"""
from print_func import TimePrint
import requests
import json

class Signal:
    def __init__(self, name, key, token, user=None):
        self.name = str(name)
        self.key = str(key)
        self.token = str(token)
        self.user = str(user)
        self.value = list(str(json.loads(requests.get('https://circusofthings.com/ReadValue',
                                params = {'Key':self.key,
                                          'Token':self.token}).content)['Value']))
        self.last_value = self.value
        TimePrint(f"Signal instance {self.name} created with key {self.key}.")
    
    
    def refresh(self):
        old_val = self.value
        # Leser av signalet og oppdaterer objektets 'value'.
        response = requests.get('https://circusofthings.com/ReadValue',
                                params = {'Key':self.key,
                                          'Token':self.token})
        response = json.loads(response.content)
        self.value = list(str(response['Value']))
        
        if self.value != old_val:
            self.last_value = old_val
    
    
    def read(self):
        # Leser av signalet og returnerer det som en liste med siffere.
        response = requests.get('https://circusofthings.com/ReadValue',
                                params = {'Key':self.key,
                                          'Token':self.token})
        response = json.loads(response.content)
        return list(str(response['Value']))
    
    def read_int(self):
        # Leser av signalet og returnerer det som en int.
        response = requests.get('https://circusofthings.com/ReadValue',
                                params = {'Key':self.key,
                                          'Token':self.token})
        response = json.loads(response.content)
        return response['Value']
    
    def write(self, val):
        # Skriver en verdi til signalet
        data = {'Key': self.key, 'Token': self.token, 'Value': val}
        requests.put('https://circusofthings.com/WriteValue',
                    data = json.dumps(data),
                    headers = {'Content-Type': 'application/json'})
        self.refresh()
        TimePrint(f"Value '{val}' written to {self.name}.")

