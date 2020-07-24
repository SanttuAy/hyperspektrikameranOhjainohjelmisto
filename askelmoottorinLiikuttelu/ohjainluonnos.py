# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 09:59:45 2020
Askelmoottorin lineaarisiirtimen ohjainohjelmiston ensimmäinen versio.
@author: Santtu
"""
import sys # komentorivikutsut
import numpy as np # Numpy Array
import pyfirmata # Arduinon käyttö
import time # Arduinon käyttö



""" Luokka yhden moottorin tietojen hallinnointia varten. 
    Luokka huolehtii yksittäisen moottorin tietojen (kytkennät, askelta 
    kierroksella, rajakytkimet, sijainti) kokoamisesta ja ylläpidosta.
"""
class Moottori:
    
    
    """ Konstruktori. Parametrit: moottorin nimi (x, y tai z), arduinokytkennöistä
        dirpin ja steppin, moottorin steps 
        per revolution -tieto ja moottorin akselin rajakytkimien pinnit Arduinossa - ensin 0-päädyn 
        kytkin, sitten toisen pään. """
    def __init__(self, nimi, dirPin, stepPin, askeltaKierroksella, rajakytkin_0, rajakytkin_1):
#    def __init__(self, nimi, dirPin, stepPin, askeltaKierroksella):
        self.nimi = nimi
        self.dirPin = dirPin
        self.dirPin_Tila = 0 #False  
        self.stepPin = stepPin
        self.askeltaKierroksella = askeltaKierroksella
        self.sijainti = 0
        self.rajakytkin_0 = rajakytkin_0
        self.rajakytkin0_Tila = 0
        self.rajakytkin_1 = rajakytkin_1
        self.rajakytkin1_Tila = 0
        self.voiLiikkua = True
        self.palaamassa = False


    """ Suunta False (0, vastapäivään) tai True (1, myötäpäivään)"""
    def setSuunta(self, suunta):
        self.dirPin_Tila = suunta


    """ Setteri 0-rajakytkimen tilan muuttamiseksi"""
    def setRajakytkin0_Tila(self, tila):
        self.rajakytkin0_Tila = tila

    
    """ Setteri 1-rajakytkimen tilan muuttamiseksi"""
    def setRajakytkin1_Tila(self, tila):
        self.rajakytkin1_Tila = tila


    """ Setteri joka kieltää mottorilta luvan liikkua. Käytetään Moottorit-oliossa
        liikuttelumetodeissa rajakytkimien yhteydessä."""
    def estaLiike(self):
        self.voiLiikkua = False


    """ Setteri joka sallii mottorin liikkua. Käytetään Moottorit-oliossa
        liikuttelumetodeissa rajakytkimien yhteydessä."""
    def salliLiike(self):
        self.voiLiikkua = True


    """ Askellaskurin toimintaan liittyvä setteri, jonka avulla tiedetään, tuleeko
        askeleet plussata vai miinustaa kokonaismäärästä."""
    def lahtee(self):
        self.palaamassa = False
        
        
    """ Laskurin toimintaan liittyvä setteri. Ks. edellinen. """
    def palaa(self):
        self.palaamassa = True
        

    """ Metodi jolla printataan konsoliin tieto siitä, miten kyseisen moottorin
        kytkennät on asetettu."""
    def printKytkennat(self):
#        print("{0}: dirpin: {1}, stepPin: {2}, askelta per kierros: {3}, rajakytkin_0 pinnissä: {4}, rajakytkin_1 pinnissä: {5}".format(self.nimi, self.dirPin, self.stepPin, self.askeltaKierroksella, self.rajakytkin_0), self.rajakytkin_1)
        print("{0}: dirpin: {1}, stepPin: {2}, askelta per kierros: {3}".format(self.nimi, self.dirPin, self.stepPin, self.askeltaKierroksella))


    """ Metodi joka nollaa moottorin ohjaaman kelkan sijaintia laskevan 
        askelmittarin"""
    def nollaaSijainti(self):
        self.sijainti = 0

    
    """ Metodi jolla kasvatetaan askelmittarin lukemaa"""
    def kasvataSijaintia(self):
        self.sijainti += 1


    """ Metodi jolla vähennetään askelia askelmittarista. Käytetään akselin 
        ääripäästä (jolloin x/y/z > 0) palatessa."""
    def vahennaSijaintia(self):
        self.sijainti -= 1

    
    """ Metodi joka palauttaa askellaskurin lukeman moottorin ohjaaman kelkan 
        oletetusta sijainnista. Huom! Todellista sijaintia ei tiedetä. Laskelma kertoo
        0-sijainnin rajakytkimeltä käskytettyjen askelten määrän, jotka otettu 
        silloin kun salliLiike oli True."""
    def getSijainti(self):
        return self.sijainti
    
        
        
""" Luokka ohjaimen kolmen moottorin säilömistä sekä kortin ja portin 
    kytkentöjen määrittämistä varten. Oletetaan, että laitteistokokoonpanossa 
    lähinnä usb-portin vaihtelulle saattaa tulla tarvetta (tällöinkin tulee 
    luoda kokonaan uusi moottorit-olio). Ohjaimen Arduinokokoonpano kolmen 
    moottorin kytkentöjen osalta toteutetaan 
    kerroMoottorienKytkennät()-metodin kuvaamalla tavalla. Luokka
    huolehtii rajakytkimien seurannasta ja moottorien liikuttelusta.
""" 
class Moottorit:
    
    
    """ Konstruktori. Parametreinä usb-kaapelin käyttämä pc:n portti ja x-, y-
        ja z-akseleilla kelkkaa liikuttelevat moottorit."""
    def __init__(self, portti, moottoriX, moottoriY, moottoriZ):
 #   def __init__(self, portti, moottoriX): #POISTA TÄMÄ!
 #   def __init__(self, portti, moottoriX, moottoriZ): #POISTA, väliaikainen
        self.portti = portti
        self.kortti = pyfirmata.Arduino(portti)
        self.moottoriX = moottoriX
        self.moottoriY = moottoriY
        self.moottoriZ = moottoriZ 
        it = pyfirmata.util.Iterator(self.kortti)
        it.start()
        self.kortti.digital[moottoriX.rajakytkin_0].mode = pyfirmata.INPUT #OUTPUT oletuksena?
        self.kortti.digital[moottoriX.rajakytkin_1].mode = pyfirmata.INPUT
        self.kortti.digital[moottoriY.rajakytkin_0].mode = pyfirmata.INPUT #OUTPUT oletuksena?
        self.kortti.digital[moottoriY.rajakytkin_1].mode = pyfirmata.INPUT
        self.kortti.digital[moottoriZ.rajakytkin_0].mode = pyfirmata.INPUT #OUTPUT oletuksena?
        self.kortti.digital[moottoriZ.rajakytkin_1].mode = pyfirmata.INPUT
            
            
    """ Metodi joka tarkistaa parametrissä nimetyn moottorin osalta, onko tultu
        jommalle kummalle sen rajakytkimistä. Jos tullaan kytkimelle, asetetaan
        moottorin liikkumissuunta valmiiksi päinvastaiseksi."""
    def tarkistaKytkimet(self, moottorinNimi):
        if moottorinNimi == 'x':
#            kytkimenTila0 = self.kortti.digital[self.moottoriX.rajakytkin_0].read()
#            self.moottoriX.setRajakytkin0_Tila(kytkimenTila0)
#            kytkimenTila1 = self.kortti.digital[self.moottoriX.rajakytkin_1].read()
#            self.moottoriX.setRajakytkin1_Tila(kytkimenTila1)
            self.moottoriX.setRajakytkin0_Tila(self.kortti.digital[self.moottoriX.rajakytkin_0].read())
            self.moottoriX.setRajakytkin1_Tila(self.kortti.digital[self.moottoriX.rajakytkin_1].read())
            if self.moottoriX.rajakytkin0_Tila == 1:
#                self.moottoriX.estaLiike()
                self.moottoriX.nollaaSijainti()
                self.vaihdaSuunta(moottorinNimi)
                self.moottoriX.lahtee()
                print("x tuli 0-kytkimelle")
            elif self.moottoriX.rajakytkin1_Tila == 1:
 #               self.moottoriX.estaLiike()
                self.vaihdaSuunta(moottorinNimi)
                self.moottoriX.palaa()
                print("x tuli 1-kytkimelle") 
            elif self.moottoriX.rajakytkin0_Tila == 0 and self.moottoriX.rajakytkin1_Tila == 0:
                print("x voi liikkua")
            else:
 #               self.moottoriX.estaLiike()
                print("x:n rajakytkimien lukemisessa ongelmia")
        elif moottorinNimi == 'y':
            self.moottoriY.setRajakytkin0_Tila(self.kortti.digital[self.moottoriY.rajakytkin_0].read())
            self.moottoriY.setRajakytkin1_Tila(self.kortti.digital[self.moottoriY.rajakytkin_1].read())
            if self.moottoriY.rajakytkin0_Tila == 1:
 #               self.moottoriY.estaLiike()
                self.moottoriY.nollaaSijainti()
                self.vaihdaSuunta(moottorinNimi)
                self.moottoriY.lahtee()
                print("y tuli 0-kytkimelle")
            elif self.moottoriY.rajakytkin1_Tila == 1:
 #               self.moottoriY.estaLiike()
                self.vaihdaSuunta(moottorinNimi)
                self.moottoriY.palaa()
                print("y tuli 1-kytkimelle")
            elif self.moottoriY.rajakytkin0_Tila == 0 and self.moottoriY.rajakytkin1_Tila == 0:
                print("y voi liikkua")
            else: 
 #               self.moottoriY.estaLiike()
                print("y:n rajakytkimien lukemisessa ongelmia")
        elif moottorinNimi == 'z':
            self.moottoriZ.setRajakytkin0_Tila(self.kortti.digital[self.moottoriZ.rajakytkin_0].read())
            self.moottoriZ.setRajakytkin1_Tila(self.kortti.digital[self.moottoriZ.rajakytkin_1].read())
            if self.moottoriZ.rajakytkin0_Tila == 1:
 #               self.moottoriZ.estaLiike()
                self.moottoriZ.nollaaSijainti()
                self.vaihdaSuunta(moottorinNimi)
                self.moottoriZ.lahtee()
                print("z tuli 0-kytkimelle")
            elif self.moottoriZ.rajakytkin1_Tila == 1:
 #               self.moottoriZ.estaLiike()
                self.vaihdaSuunta(moottorinNimi)
                self.moottoriZ.palaa()
                print("z tuli 1-kytkimelle")
            elif self.moottoriZ.rajakytkin0_Tila == 0 and self.moottoriZ.rajakytkin1_Tila == 0:
                print("z voi liikkua")
            else: 
 #               self.moottoriZ.estaLiike()
                print("z:n rajakytkimien lukemisessa ongelmia")
        else: 
 #           self.moottoriX.estaLiike()# TODO eli jos tulee kutsuttua väärin, kaikkien moottoreiden liike estetty, kun täältä palataan
 #           self.moottoriY.estaLiike()
 #           self.moottoriZ.estaLiike()
            print("Kytkimiä tarkastettaessa moottorin nimi oltava x, y tai z.")


    """ Metodi jolla asetetaan suunta halutun moottorin liikuttamista varten. 
    Parametereinä moottorin nimi ja 1 tai 0, 
    missä 0= vastapäivään, 1= myötäpäivään."""
    def setSuunta(self, moottorinNimi, myotaVaiVasta):
        print("setSuunta sai suunta-arvoksi: ", myotaVaiVasta)
        if moottorinNimi == 'x':
            moottori = self.moottoriX
            dirPin = self.moottoriX.dirPin
        elif moottorinNimi == 'y':
            moottori = self.moottoriY
            dirPin = self.moottoriY.dirPin
        elif moottorinNimi == 'z':
            moottori = self.moottoriZ
            dirPin = self.moottoriZ.dirPin
        else: print("Moottorin nimen tulee olla x, y tai z")
        if myotaVaiVasta == 0:
            self.kortti.digital[dirPin].write(0) # LOW-arvolla vastapäivään
            moottori.setSuunta(False)
        elif myotaVaiVasta == 1:
            self.kortti.digital[dirPin].write(1)
            moottori.setSuunta(True)
        else: print("SetSuunnan suunta-arvoksi tulee antaa 0 (vastapäivään) tai 1 (myötäpäivään)")


    """ Metodi jolla käyttäjä voi vaihtaa parametrinä annetun moottorin nykyisen 
    liikkumasuunnan päinvastaiseksi."""
    def vaihdaSuunta(self, moottorinNimi):
        if moottorinNimi == 'x':
            moottori = self.moottoriX
            dirPin = self.moottoriX.dirPin
        elif moottorinNimi == 'y':
            moottori = self.moottoriY
            dirPin = self.moottoriY.dirPin
        elif moottorinNimi == 'z':
            moottori = self.moottoriZ
            dirPin = self.moottoriZ.dirPin
        else: print("Suuntaa vaihdettaessa moottorin nimen tulee olla x, y tai z")
        if moottori.dirPin_Tila == 0:
            self.kortti.digital[dirPin].write(1)
        elif moottori.dirPin_Tila == 1:
            self.kortti.digital[dirPin].write(0)
        else: 
            print("vaihdaSuunta dirPin: ", dirPin)
            print("Suunta-arvoksi tulee antaa 0 (vastapäivään) tai 1 (myötäpäivään)")


    def laskuri(self, moottori):
        if moottori.palaamassa == False:
            moottori.kasvataSijaintia()
        else:
            moottori.vahennaSijaintia()


    """ Metodi jolla liikutetaan valittua moottoria asetettu askelmäärä. Jos
    kesken matkan tullaan rajakytkimelle, moottori pystähtyy siihen, eikä käytä
    jäljellä olevia askelia palaamiseen."""
    def liikuAskelta(self, moottorinNimi, montakoAskelta):
        if moottorinNimi == 'x':
            moottori = self.moottoriX
            stepPin = self.moottoriX.stepPin           
        elif moottorinNimi == 'y':
            stepPin = self.moottoriY.stepPin
            moottori = self.moottoriY
        elif moottorinNimi == 'z':
            stepPin = self.moottoriZ.stepPin
            moottori = self.moottoriZ
        else: print("Moottorin nimen tulee olla x, y tai z")
        for i in range(montakoAskelta):
            self.tarkistaKytkimet(moottorinNimi)
            if moottori.voiLiikkua == True:
                self.kortti.digital[stepPin].write(1) 
                time.sleep(2000 * 10**(-6)) # hidas liike. Nopean kerroin esim.500
                self.kortti.digital[stepPin].write(0)
                time.sleep(2000 * 10**(-6))
                self.laskuri(moottori)
            else: 
                print("Moottori {0} ei voi liikkua enempää tähän suuntaan.".format(moottorinNimi))
                break
        print('Liikutettiin {0}-moottoria sijaintiin {1}.'.format(moottorinNimi, moottori.sijainti))


# POISTA JOS TURHA
    """ Metodi jolla liikutetaan valittua moottoria asetettu määrä 
    kokonaisia kierroksia TÄSSÄ EI KYTKINTEN TARKASTELUA TAI LASKURIA...
    """
    def liikuKierrosta(self, moottorinNimi, montakoKierrosta):
        if moottorinNimi == 'x':
            stepsPerRevolution = self.moottoriX.askeltaKierroksella
            stepPin = self.moottoriX.stepPin
        elif moottorinNimi == 'y':
            stepsPerRevolution = self.moottoriY.askeltaKierroksella
            stepPin = self.moottoriY.stepPin
        elif moottorinNimi == 'z':
            stepsPerRevolution = self.moottoriZ.askeltaKierroksella
            stepPin = self.moottoriZ.stepPin
        else: print("Moottorin nimen tulee olla x, y tai z")
        for j in range(montakoKierrosta):
            for i in range(stepsPerRevolution):
                self.kortti.digital[stepPin].write(1) # LOW-HIGH -impulssi saa moottorin liikkumaan
                time.sleep(2000 * 10**(-6)) # hidas liike...
                self.kortti.digital[stepPin].write(0)
                time.sleep(2000 * 10**(-6))
         #   steps += 1 #muuta tähän toteutukseen sopivaksi #HUOMAA LASKURISTA! Laskee oletettuja askeleita Laskenta jatkuu vaikkei moottori saisi virtaa ollenkaan
        print('Liikutettiin {0}-moottoria {1} kierrosta.'.format(moottorinNimi, montakoKierrosta))
        

    """ Metodi kaikkien moottoreiden palauttamista varten, palauttaa Numpy arrayn"""
    def getSijainnit(self):
#        sijainti = np.arange(3) #arange-funktio luo Numpy-arrayn
        sijainti = np.array([self.moottoriX.sijainti, self.moottoriY.sijainti, self.moottoriZ.sijainti])        
        return sijainti


    """ Printtaa konsoliin käyttöön otetun portin nimen. 
    Nimi löytyy esim. Arduinon kautta"""
    def printPortti(self):
        print("Käytössä oleva portti:", self.portti)
    
    
    """ Metodi joka printtaa konsoliin kolmen mottorin kytkentätiedot sekä
    moottoriominaisuuksista steps per revolution -tiedon"""
    def printMoottorienKytkennat(self):
        print("Moottoreiden määritykset:")
        self.moottoriX.printKytkennat()
        self.moottoriY.printKytkennat()
        self.moottoriZ.printKytkennat()

        
"""
    Luokka kuvaustapahtuman hallintaa varten. Luokka käyttää moottorit-oliota
    ja huolehtii yksittäistä kuvaustapahtumaa varten asetettavista tiedoista ja 
    lokitiedoista.
"""        
class Kuvaus:
    
    """ Konstruktori. Parametrinä moottorit-olio. Lokitieto ei sisällä kaikkia 
    kuvaus-olion sijaintitietoja, vaan "riitävän" määrän askeltietoja, jotta voidaan
    päätellä, kummassako päässä kutakin akselia ollaan liikkumassa (ja mihin päin
    oltiin menossa?)."""
    def __init__(self, moottorit):
        self.moottorit = moottorit
        self.aloituskohta = { #oletusaloituskohta on (x0, y0, z0)
        "x" : 0, # (0, 0, 0)-sijainnissa rajakytkimet, joissa sijaitsee laskurien 0
        "y" : 0, # erotetaan ääripään rajakytkimistä viimeisimmän lokitiedon perusteella?
        "z" : 0 # vai kytkentätiedon?
        }

        self.loki = { # loki sijaintitiedoille
            "alku" : (0,0,0)
            }
    
#TODO: toteutus
        """ Metodi lokitiedon lisäämiseksi. Lokiin kerätään X-määrä edeltäviä sijaintieja."""
#    def lisaaLokiin(self):
        
        
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
    moottoriX = Moottori('x', 4, 3, 200, 2, 13) #KÄYTÄ NÄITÄ KUN KYTKIMIEN PINNIT TIEDOSSA
    moottoriY = Moottori('y', 10, 8, 200, 5, 6)
    moottoriZ = Moottori('z', 12, 11, 400, 7, 9)
 #   moottoriX = Moottori('x', 4, 3, 200)
 #   moottoriY = Moottori('y', 10, 8, 200)
 #   moottoriZ = Moottori('z', 12, 11, 400)
    moottorit = Moottorit('COM6', moottoriX, moottoriY, moottoriZ) # katso portti Arduinon kautta
#    moottorit.lueKytkimet('x')
#    moottorit.lueKytkimet('y')
#    moottorit.lueKytkimet('z')
  #  moottorit = Moottorit('COM6', moottoriX)#POISTA TÄMÄ
  #  moottorit = Moottorit('COM6', moottoriX, moottoriZ) #väliaikainen, kunnes y toimii
#    moottorit.printPortti()
#    moottorit.printMoottorienKytkennat()
    moottorit.setSuunta('x', 1) # True
    moottorit.setSuunta('y', 0) # False
    moottorit.setSuunta('z', 1) # True
#    moottorit.liikuKierrosta('x', 1)
#    moottorit.liikuKierrosta('y', 1)
#    moottorit.liikuKierrosta('z', 1)
 #   moottorit.setSuunta('z', 1)
 #   moottorit.liikuKierrosta('z', 1)
#    moottorit.setSuunta('x', 0)
#    moottorit.liikuKierrosta('x', 1)
    moottorit.liikuAskelta('x', 300)
    moottorit.liikuAskelta('y', 300)
    moottorit.liikuAskelta('z', 600)
#    kuvaus = Kuvaus(moottorit)
#    while True:
#        it = pyfirmata.util.Iterator(moottorit.kortti)
#        it.start()                                    # EI LOOPPIIN...
#        rajakytkin0_Tila = moottorit.kortti.digital[moottorit.moottoriX.rajakytkin_0].read()
#        if rajakytkin0_Tila == 1:
#            print("x tuli 0-kytkimelle")
#        elif rajakytkin0_Tila == 0: # auki
#            print("x voi liikkua.")
#        else: 
#            print("x-moottorin 0-kytkintä ei voitu lukea.  Kytkimen tila: {0}".format(rajakytkin0_Tila))
if __name__ == "__main__":
    main()
        
        