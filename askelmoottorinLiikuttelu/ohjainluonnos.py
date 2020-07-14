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




""" Luokka ohjaimen moottorien kytkentöjen määrittämistä varten. 
    Oletetaan, että laitteistokokoonpanossa lähinnä usb-portin vaihtelulle 
    saattaa tulla tarvetta (tällöinkin tulee luoda kokonaan uusi kytkennät-olio). 
    Ohjaimen Arduinokokoonpano toteutetaan kerroMoottorienKytkennät()-metodin 
    kuvaamalla tavalla.
"""
class Moottorit:
    
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
            "dirPin" : None, #lisätään myöhemmin
            "stepPin" : None, 
            "stepsPerRevolution" : 200, 
            "steps" : 0 
            }
        self.moottoriY = y
        z = {
            "dirPin" : None, #lisätään myöhemmin
            "stepPin" : None, 
            "stepsPerRevolution" : 200, 
            "steps" : 0 
            }
        self.moottoriZ = z
        it = pyfirmata.util.Iterator(kortti)
        it.start()
        
        
    """ Printtaa käyttöön otetun portin tiedot """
    def kerroPortti(self):
        print("Käytössä oleva portti:", self.portti)
    
    
    """ Printtaa mottorien kytkentätiedot"""
    def kerroMottorienKytkennat(self):
        print("x-moottori: ", self.moottoriX, "\ny-moottori: ", self.moottoriY, "\nz-moottori: ", self.moottoriZ)
    
        
"""
    Luokka kuvaustapahtumaa varten.
"""        
class Kuvaus:
    def __init__(self, moottorit):
        self.moottorit = moottorit
        self.aloituskohta = { #oletusaloituskohta on (x0, y0, z0)
        "x" : 0, # 000-sijainnissa rajakytkimet, joissa sijaitsee laskurien 0
        "y" : 0,
        "z" : 0
        }
        self.stepsX = 0 # laskuri x-moottorin askelille
        self.stepsY = 0 # laskuri y-moottorin askelille
        self.stepsZ = 0 # laskuri z-moottorin askelille
        self.logi = { # logi sijaintitiedoille
            "alku" : (0,0,0)
            }
    
#TODO: toteutus
    def lisaaLogiin(self):
        
        
    """ Palauttaa Numpy Arrayna kulloisenkin sijaintitiedon"""
    def kerroSijainti(self):
        sijaintitiedot = np.arange(3) #arange-funktio luo Numpy-arrayn
#TODO: lisää sijainti taulukkoon!
        print("Login tallennusmuoto: ", sijaintitiedot.shape) # tarkistustulostus
        return sijaintitiedot

""" Kerrotaan aloituspisteen tiedot x, y ja z-akselin suhteen. """
#def tellStartingPoint():
#    #print('Aloituspisteeksi on asetettu x{0}, y{1}, z{2}'.format(alkukohtaX, alkukohtaY, alkukohtaZ))
#tällä kävi ilmi etteivät alkukohtien arvot pysyneet uusissa arvoissa vaan palasivat nolliksi!
#    print('Aloituspisteeksi on asetettu x{0}, y{1}, z{2}'.format(sijaintitiedot[0], sijaintitiedot[1], sijaintitiedot[2]))


# MIHIN?
""" Alustetaan moottorille aloituskohta.
Parametrit: 
moottori: moottori jolle aloituspiste asetetaan
kohta: piste moottorin edustamalla akselilla, asetetaan aloituspisteeksi """
#def asetaAloituskohta(moottori, kohta):    
#    if moottori in aloituskohta.keys():
#        aloituskohta[moottori] = kohta
#    else:
#        print("Moottorivaihtoehdot ovat x, y ja z")



#TODO: funktioiden kutsuminen komentoriviltä, vaatiiko plugin?
def main():
    moottorit = Moottorit('COM4') # katsoin käyttämäni portin Arduinon kautta
    moottorit.kerroPortti()
    moottorit.kerroMottorienKytkennat()
    kuvaukset = Kuvaukset(moottorit)

if __name__ == "__main__":
    main()
        
        