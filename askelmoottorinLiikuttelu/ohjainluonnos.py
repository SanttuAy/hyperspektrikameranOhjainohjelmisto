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


""" Luokka yhden moottorin tietojen hallinnointia varten. 
"""
class Moottori:
    
    def __init__(self, nimi, dirPin, stepPin, askeltaKierroksella):
        self.nimi = nimi
        self.dirPin = dirPin
        self.stepPin = stepPin
        self.askeltaKierroksella = askeltaKierroksella
        self.sijainti = 0
        self.voikoLiikkua = False


    def printKytkennat(self):
        print("{0}: dirpin: {1}, stepPin: {2}, askelta per kierros: {3}".format(self.nimi, self.dirPin, self.stepPin, self.askeltaKierroksella))


    def nollaaSijainti(self):
        self.sijainti = 0
    
    
    def kasvataSijaintia():
        self.sijainti = self.sijainti + 1


    def vahennaSijaintia():
        self.sijainti = self.sijainti - 1

    
    def pysayta(self):
        self.voikoLiikkua = False


    def salliLiike(self):
        self.voikoLiikkua = True
        

""" Luokka ohjaimen kolmen moottorin säilömistä sekä kortin ja portin 
    kytkentöjen määrittämistä varten. Oletetaan, että laitteistokokoonpanossa 
    lähinnä usb-portin vaihtelulle saattaa tulla tarvetta (tällöinkin tulee 
    luoda kokonaan uusi kytkennät-olio). Ohjaimen Arduinokokoonpano 
    toteutetaan kerroMoottorienKytkennät()-metodin kuvaamalla tavalla. Luokka
    huolehtii siitä, että liikuttelukäskyt lähetetään oikealle moottorille.
""" 
class Moottorit:
    
    def __init__(self, portti, moottoriX, moottoriY, moottoriZ):
        self.portti = portti
        self.kortti = pyfirmata.Arduino(portti)
        self.moottoriX = moottoriX
        self.moottoriY = moottoriY
        self.moottoriZ = moottoriZ
        it = pyfirmata.util.Iterator(self.kortti)
        it.start()

    """ Printtaa käyttöön otetun portin tiedot """
    def kerroPortti(self):
        print("Käytössä oleva portti:", self.portti)
    
    
    """ Printtaa mottorien kytkentätiedot"""
    def kerroMottorienKytkennat(self):
        print("Moottoreiden määritykset:")
        self.moottoriX.printKytkennat()
        self.moottoriY.printKytkennat()
        self.moottoriZ.printKytkennat()


    """ Metodi jolla asetetaan suunta halutun moottorin liikuttamista varten. 
        Parameterinä
        annetaan 1, jonka merkitys on myötäpäivään, tai 0, jonka merkitys 
        vastapäivään."""
    def suunta(self, moottorinNimi, myotaVaiVasta):
        if moottorinNimi == 'x':
            dirPin = self.moottoriX.dirPin
        elif moottorinNimi == 'y':
            dirPin = self.moottoriY.dirPin
        elif moottorinNimi == 'z':
            dirPin = self.moottoriZ.dirPin
        else: print("Moottorin nimen tulee olla x, y tai z")
        if myotaVaiVasta == 0:
            self.kortti.digital[dirPin].write(0) # LOW-arvolla vastapäivään
        elif myotaVaiVasta == 1:
            self.kortti.digital[dirPin].write(1) # HIGH-arvolla myötäpäivään
        else: print("Suunta-arvoksi tulee antaa 0 (vastapäivään) tai 1 (myötäpäivään)")


""" Metodi jolla... halutun moottorin liikuttelua varten
"""
# Mieti liikuttelun toteutus

             
"""
    Luokka kuvaustapahtuman hallitaa varten.
"""        
class Kuvaus:
    def __init__(self, moottorit):
        self.moottorit = moottorit
        self.aloituskohta = { #oletusaloituskohta on (x0, y0, z0)
        "x" : 0, # 000-sijainnissa rajakytkimet, joissa sijaitsee laskurien 0
        "y" : 0,
        "z" : 0
        }

        self.loki = { # loki sijaintitiedoille
            "alku" : (0,0,0)
            }
    
#TODO: toteutus
#    def lisaaLogiin(self):
        
        
    """ Palauttaa Numpy Arrayna kulloisenkin sijaintitiedon"""
#    def kerroSijainti(self):
#        sijaintitiedot = np.arange(3) #arange-funktio luo Numpy-arrayn
#TODO: lisää sijainti taulukkoon!
#        print("Login tallennusmuoto: ", sijaintitiedot.shape) # tarkistustulostus
#        return sijaintitiedot

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
    moottoriX = Moottori('x', 4, 3, 200)
    moottoriY = Moottori('y', None, None, 200)
    moottoriZ = Moottori('z', None, None, 200)
    moottorit = Moottorit('COM6', moottoriX, moottoriY, moottoriZ) # katso portti Arduinon kautta
    moottorit.kerroPortti()
    moottorit.kerroMottorienKytkennat()
    kuvaus = Kuvaus(moottorit)

if __name__ == "__main__":
    main()
        
        