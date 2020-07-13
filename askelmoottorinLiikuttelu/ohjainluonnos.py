# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 09:59:45 2020
Ohjaimen ensimmäinen versio.
@author: Santtu
"""
import sys # komentorivikutsut
import numpy as np # Numpy Array
import pyfirmata # Arduinon käyttö
import time # Arduinon käyttö




""" Kytkentöjen luominen. Lähdetään oletuksesta, että tätä ei tehdä usein
    uudestaan, joten vain portin vaihtelulle tarvetta.
"""
class Kytkennat:
    
    def __init__(self, portti):
        self.portti = portti
        self.kortti = pyfirmata.Arduino(portti)
        x = {
            "dirPin" : 4, # x-moottorin suuntatieto, output oletuksena
            "stepPin" : 3, # x-moottorin liikutteluteito, output oletuksena
            "stepsPerRevolution" : 200, # x-moottori kierrosmäärä
            "steps" : 0 #x-moottorin askeleet, aluksi 0, SIIRTO KUVAUKSIIN?
            }
        self.moottoriX = x
        y = {
            "dirPin" : None,
            "stepPin" : None, 
            "stepsPerRevolution" : 200, 
            "steps" : 0 
            }
        self.moottoriY = y
        z = {
            "dirPin" : None,
            "stepPin" : None, 
            "stepsPerRevolution" : 200, 
            "steps" : 0 
            }
        self.moottoriZ = z
        
        
    """ Kerrotaan käyttöön otetun portin tiedot """
    def kerroPortti(self):
        print("Käytössä oleva portti:", self.portti)
    
    def kerroMottorienKytkennat(self):
        print("x-moottori: ", self.moottoriX, "\ny-moottori: ", self.moottoriY, "\nz-moottori: ", self.moottoriZ)
    

#class Kuvaus:
    


# VÄLIAIKAISESTI sijaintitiedot = np.arange(3) #arange-funktio luo Numpy-arrayn
#print("Login tallennusmuoto: ", sijaintitiedot.shape) # tarkistustulostus


# moottoreiden kytkennät ja askellaskurit
 

#dirPinY = ??? # output oletuksena, y-moottorin suunta
#stepPinY = ??? # output oletuksena, y-moottorin liikuttelu
#stepsPerRevolutionY = 200 # y-moottori kierrosmäärä
#stepsY = 0 # y-moottorin askeleet 

#dirPinZ = ??? # output oletuksena, z-moottorin suunta
#stepPinZ = ??? # output oletuksena, z-moottorin liikuttelu
#stepsPerRevolutionZ = 200 # z-moottori kierrosmäärä???
#stepsZ = 0 # z-moottorin askeleet 



""" Kerrotaan aloituspisteen tiedot x, y ja z-akselin suhteen. """
#def tellStartingPoint():
#    #print('Aloituspisteeksi on asetettu x{0}, y{1}, z{2}'.format(alkukohtaX, alkukohtaY, alkukohtaZ))
#tällä kävi ilmi etteivät alkukohtien arvot pysyneet uusissa arvoissa vaan palasivat nolliksi!
#    print('Aloituspisteeksi on asetettu x{0}, y{1}, z{2}'.format(sijaintitiedot[0], sijaintitiedot[1], sijaintitiedot[2]))


""" Alustetaan moottorille aloituskohta.
Parametrit: 
moottori: moottori jolle aloituspiste asetetaan
kohta: piste moottorin edustamalla akselilla, asetetaan aloituspisteeksi """
#def asetaAloituskohta(moottori, kohta):    
#    if moottori in aloituskohta.keys():
#        aloituskohta[moottori] = kohta
#    else:
#        print("Moottorivaihtoehdot ovat x, y ja z")


#TODO: funktioiden kutsuminen komentoriviltä...
def main():
    testi = Kytkennat('COM4') # katsoin käyttämäni portin Arduinon kautta
    testi.kerroPortti()
    testi.kerroMottorienKytkennat()
#    aloituskohta : { #oletusaloituskohta on (x0, y0, z0)
#        "x" : 0,
#        "y" : 0,
#        "z" : 0
#        }
#    asetaAloituskohta('x', 0)
#    asetaAloituskohta('y', 5)
#    asetaAloituskohta('z', 1.2) #sijoitti tarkan arvon, tulosti ykkösen
#    tellGate()
#    tellStartingPoint()
#    print(sijaintitiedot)

if __name__ == "__main__":
    main()
        
        