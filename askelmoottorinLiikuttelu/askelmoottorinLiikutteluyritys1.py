# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 17:36:49 2020
Kokeillaan muuntaa Arduino-koodi askelmoottorin liikuttelu 
pyFirmataa hyödyntävälle pythonille.
@author: Santtu
"""
#import sys #tarvetta?
#import serial #poikkeuksen käsittelyyn
import pyfirmata
import time

# määritellään yhteydet arduinoon ja 
# moottorin askelmäärä per kierros (steps per revolution)
board = pyfirmata.Arduino('COM4')
dirPin = 4 # output oletuksena
stepPin = 3 # output oletuksena
stepsPerRevolution = 200 # bipolaarisen moottorin tiedoista
steps = 0

it = pyfirmata.util.Iterator(board)
it.start()
while True:
  #  try:
        board.digital[dirPin].write(1) # HIGH-arvolla myötäpäivään
        # liikutetaan moottoria hitaasti
        for i in range(stepsPerRevolution):
            board.digital[stepPin].write(1) # LOW-HIGH -impulssi saa moottorin liikkumaan
            time.sleep(2000 * 10**(-6)) # hidas liike...
            board.digital[stepPin].write(0)
            time.sleep(2000 * 10**(-6))
            steps += 1 #HUOMAA LASKURISTA! Laskee oletettuja askeleita Laskenta jatkuu vaikkei moottori saisi virtaa ollenkaan
        time.sleep(1)
        print(steps)
        board.digital[dirPin].write(0) # LOW-arvolla vastapäivään
        # liikutetaan moottoria nopeammin
        for i in range(stepsPerRevolution):
            board.digital[stepPin].write(1) # LOW-HIGH -impulssi saa moottorin liikkumaan
            time.sleep(500 * 10**(-6)) # nopea liike...
            board.digital[stepPin].write(0)
            time.sleep(500 * 10**(-6))
            steps += 1
        time.sleep(1)
        print(steps)
   # except SerialTimeoutException as err1: # ei toimi, koska nimi ei määritelty
   #     print("kirjoitusaikakatkaisuun liittyvä poikkeus", err1)
   # except SerialException as err2:
    #    print("Onko kaapeli sarjaportissa?", err2)