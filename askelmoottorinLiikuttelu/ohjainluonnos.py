# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#!/usr/bin/env python3

"""
Created on Wed Jul  8 09:59:45 2020
Askelmoottorin lineaarisiirtimen ohjainohjelmiston ensimmäinen versio.
@author: Santtu
"""
#import sys #tuleeko tarvetta
import numpy as np # Numpy array
import pyfirmata # Arduinon käyttö
import time # Arduinon käyttö
import serial #sarjaportti
import pandas as pd # taulukko
#import pyserial



""" Luokka yhden moottorin tietojen hallinnointia varten. 
    Luokka huolehtii yksittÃ¤isen moottorin tietojen (kytkennät, askelta 
    kierroksella, rajakytkimet, sijainti) kokoamisesta ja ylläpidosta.
"""
class Moottori:
    
    
    """ Konstruktori. Parametrit: moottorin nimi (x, y tai z), arduinokytkennöistä
        dir_pin ja step_pin, moottorin steps 
        per revolution -tieto ja moottorin akselin rajakytkimien pinnit Arduinossa - ensin 0-päädyn 
        kytkin, sitten toisen pään. """
    def __init__(self, nimi, dir_pin, step_pin, askelta_kierroksella, rajakytkin_0, rajakytkin_1):
        self.nimi = nimi
        self.dir_pin = dir_pin
        self.dir_pin_tila = 0 #False, vastapäivään
        self.step_pin = step_pin
        self.askelta_kierroksella = askelta_kierroksella
        self.sijainti = 0
        self.rajakytkin_0 = rajakytkin_0
        self.rajakytkin_0_tila = None # 0
        self.rajakytkin_1 = rajakytkin_1
        self.rajakytkin_1_tila = None # 0
        self.voi_liikkua = True
        self.palaamassa = False  


    """ Suunta False (0, vastapÃ¤ivÃ¤Ã¤n) tai True (1, myötäpäivään)"""
    def set_suunta(self, suunta):
        self.dir_pin_tila = suunta


    """ Setteri 0-rajakytkimen tilan muuttamiseksi"""
    def set_rajakytkin_0_tila(self, tila):
        self.rajakytkin_0_tila = tila

    
    """ Setteri 1-rajakytkimen tilan muuttamiseksi"""
    def set_rajakytkin_1_tila(self, tila):
        self.rajakytkin_1_tila = tila


    """ Setteri joka kieltää mottorilta luvan liikkua. Käytetään Moottorit-oliossa
        liikuttelumetodeissa rajakytkimien yhteydessä."""
    def esta_liike(self):
        self.voi_liikkua = False


    """ Setteri joka sallii mottorin liikkua. Käytetään Moottorit-oliossa
        liikuttelumetodeissa rajakytkimien yhteydessä."""
    def salli_liike(self):
        self.voi_liikkua = True


    """ Askellaskurin toimintaan liittyvä setteri, jonka avulla tiedetään, tuleeko
        askeleet plussata vai miinustaa kokonaismäärään."""
    def lahtee(self):
        self.palaamassa = False
        
        
    """ Laskurin toimintaan liittyvä setteri. Ks. edellinen. """
    def palaa(self):
        self.palaamassa = True
        

    """ Metodi jolla printataan konsoliin tieto siitä, miten kyseisen moottorin
        kytkennät on asetettu."""
    def print_kytkennat(self):
        print("{0}: dir_pin: {1}, step_pin: {2}, askelta kierroksella: {3}, rajakytkin_0 pinnissä: {4}, rajakytkin_1 pinnissä: {5}".format(self.nimi, self.dir_pin, self.step_pin, self.askelta_kierroksella, self.rajakytkin_0, self.rajakytkin_1))


    """ Metodi joka nollaa moottorin ohjaaman kelkan sijaintia laskevan 
        askelmittarin"""
    def nollaa_sijainti(self):
        self.sijainti = 0

    
    """ Metodi jolla kasvatetaan askelmittarin lukemaa"""
    def kasvata_sijaintia(self):
        self.sijainti += 1


    """ Metodi jolla vähennetään askelia askelmittarista. Käytetään akselin 
        ääripäästä (x/y/z > 0) palatessa."""
    def vahenna_sijaintia(self):
        self.sijainti -= 1

    
    """ Metodi joka palauttaa askellaskurin lukeman moottorin ohjaaman kelkan 
        oletetusta sijainnista. Huom! Todellista sijaintia ei tiedetä. Laskelma kertoo
        0-rajakytkimeltä käskytettyjen askelten määrän, jotka otettu 
        silloin kun attribuutti salliLiike oli True."""
    def get_sijainti(self):
        return self.sijainti
    
        
        
""" Luokka ohjaimen kolmen moottorin säilömistä sekä kortin ja portin 
    kytkentöjen määrittämistä varten. Oletetaan, että laitteistokokoonpanossa 
    usb-portin vaihtelulle saattaa tulla tarvetta (tällöinkin tulee 
    luoda kokonaan uusi moottorit-olio). Ohjaimen Arduinokokoonpano kolmen 
    moottorin kytkentöjen osalta toteutetaan 
    kerroMoottorienKytkennat()-metodin kuvaamalla tavalla. Luokka
    huolehtii rajakytkimien seurannasta ja moottorien liikuttelusta.
""" 
class Moottorit:
    
    
    """ Konstruktori. Parametreinä usb-kaapelin käyttämä pc:n portti 
    (jos automaattinen portintunnistus saadaan toimimaan, voi tämän jättää pois)
    ja x-, y- ja z-akseleilla kelkkaa liikuttelevat moottorit."""
    def __init__(self, portti, moottori_x, moottori_y, moottori_z):
            self.portti = portti
            self.kortti = pyfirmata.ArduinoMega(portti) #Arduino.AUTODETECT ei tässä toiminut
            self.moottori_x = moottori_x
            self.moottori_y = moottori_y
            self.moottori_z = moottori_z
            self.viive = 2.6 * 1e-6 # 2.6 * 1e-6 # ajurit edellyttävät että  impulssiväli on enemmän kuin 2.5 mikrosekunttia
            self.viive_y = 4 * 1e-6
            self.iteraattori = pyfirmata.util.Iterator(self.kortti)
            self.iteraattori.start()
            self.kortti.digital[self.moottori_x.rajakytkin_0].mode = pyfirmata.INPUT # kokeiltu INPUT_PULLUP # oletuksena OUTPUT?
            self.kortti.digital[self.moottori_x.rajakytkin_1].mode = pyfirmata.INPUT #Muutos muistiin: lisäsäin hakasulkeisiin [self.moott...
            self.kortti.digital[self.moottori_y.rajakytkin_0].mode = pyfirmata.INPUT
            self.kortti.digital[self.moottori_y.rajakytkin_1].mode = pyfirmata.INPUT
            self.kortti.digital[self.moottori_z.rajakytkin_0].mode = pyfirmata.INPUT
            self.kortti.digital[self.moottori_z.rajakytkin_1].mode = pyfirmata.INPUT

            
    """ Metodi joka tarkistaa parametrissä nimetyn moottorin osalta, onko tultu
        jommalle kummalle sen rajakytkimistä. Jos tullaan kytkimelle, asetetaan
        moottorin liikkumissuunta valmiiksi päinvastaiseksi."""
    def tarkista_kytkimet(self, moottorin_nimi):
        if moottorin_nimi == 'x':
            nonelaskuri = 0
            kytkimen_tila_0 = self.kortti.digital[self.moottori_x.rajakytkin_0].read()
      #      print("1: x:n 0-kytkimen lukemisen jälkeen tila: {0}".format(kytkimen_tila_0)) #TESTAUSTA
            kytkimen_tila_1 = self.kortti.digital[self.moottori_x.rajakytkin_1].read()
      #      print("1: x:n 1-kytkimen lukemisen jälkeen tila: {0}".format(kytkimen_tila_1)) #TESTAUSTA
            while kytkimen_tila_0 is None or kytkimen_tila_1 is None:
                try:    
                    print("odotetaan yhteyttä x:n kytkimiin")
                    time.sleep(0.1)
                    kytkimen_tila_0 = self.kortti.digital[self.moottori_x.rajakytkin_0].read()
                    print("2: Nonen jälkeen x:n 0-kytkimen tila: {0}".format(kytkimen_tila_0)) #TESTAUSTA, jos jäädään alussa silmukkaan kytkimien lukemisen kanssa, ollaan tässä (esiintyy vain x:n yhteydessä)!
                    kytkimen_tila_1 = self.kortti.digital[self.moottori_x.rajakytkin_1].read()
                    print("2: Nonen jälkeen x:n 1-kytkimen tila: {0}".format(kytkimen_tila_1)) #TESTAUSTA
                    nonelaskuri += 1
                    if nonelaskuri == 100:
                        print("Rajakytkimen pinnin lukeminen epäonnistui. Käynnistä ohjain uudelleen.")
                        self.moottori_x.esta_liike()
                        self.moottori_y.esta_liike()
                        self.moottori_z.esta_liike()
                        return
                except serial.SerialTimeoutException:
                    print("USB-yhteys katkesi")
            else:
                self.moottori_x.set_rajakytkin_0_tila(kytkimen_tila_0) 
                self.moottori_x.set_rajakytkin_1_tila(kytkimen_tila_1)
                if self.moottori_x.rajakytkin_0_tila == 1:
                    self.moottori_x.nollaa_sijainti() #tultiin sijaintiin 0
                    self.vaihda_suunta(moottorin_nimi) #rajakytkimellä käännyttävä
    #                print("3a: x:n 0-kytkimen tila IF-lauseessa: {0}".format(self.moottori_x.rajakytkin_0_tila)) #TESTAUSTA
     #               print("3b: x:n 1-kytkimen tila IF-lauseessa: {0}".format(self.moottori_x.rajakytkin_1_tila)) #TESTAUSTA
                    self.moottori_x.esta_liike()
                    print("x tuli 0-kytkimelle")
                    self.irrota_kytkimelta(self.moottori_x)
                elif self.moottori_x.rajakytkin_1_tila == 1:
                    self.vaihda_suunta(moottorin_nimi) # tieto moottorin palaamisesta asetetaan jo täällä, joten allaolevaa ei kuulu asettaa tässä
                    self.moottori_x.esta_liike()
                    print("x tuli 1-kytkimelle")
                    self.irrota_kytkimelta(self.moottori_x)
                elif self.moottori_x.rajakytkin_0_tila == 0 and self.moottori_x.rajakytkin_1_tila == 0: # mahdollinen toiseen jäänyt None jää kiinni tässä
     #               print("x voi liikkua")
                    return
                else:
                    print("x:n rajakytkimien lukemisessa ongelmia")
                    self.moottori_x.esta_liike()
        elif moottorin_nimi == 'y':
            try:
                kytkimen_tila_0 = self.kortti.digital[self.moottori_y.rajakytkin_0].read()
        #        print("1: y:n 0-kytkimen lukemisen jälkeen tila: {0}".format(kytkimen_tila_0)) #TESTAUSTA
                kytkimen_tila_1 = self.kortti.digital[self.moottori_y.rajakytkin_1].read()
        #        print("1: y:n 1-kytkimen lukemisen jälkeen tila: {0}".format(kytkimen_tila_1)) #TESTAUSTA
                while kytkimen_tila_0 is None or kytkimen_tila_1 is None:
                    print("odotetaan yhteyttä y:n kytkimiin")
                    time.sleep(0.1)
                    kytkimen_tila_0 = self.kortti.digital[self.moottori_y.rajakytkin_0].read()
      #              print("2: Nonen jälkeen Y:n 0-kytkimen tila: {0}".format(kytkimen_tila_0)) #TESTAUSTA
                    kytkimen_tila_1 = self.kortti.digital[self.moottori_y.rajakytkin_1].read()
                else:
                    self.moottori_y.set_rajakytkin_0_tila(kytkimen_tila_0)
                    self.moottori_y.set_rajakytkin_1_tila(kytkimen_tila_1)
                    if self.moottori_y.rajakytkin_0_tila == 1:
       #                 print("3a: Y:n 0-kytkimen tila IF-lauseessa: {0}".format(self.moottori_y.rajakytkin_0_tila)) #TESTAUSTA
                        self.moottori_y.esta_liike()
                        self.moottori_y.nollaa_sijainti()
                        self.vaihda_suunta(moottorin_nimi)
                        print("y tuli 0-kytkimelle")
                        self.irrota_kytkimelta(self.moottori_y)
                    elif self.moottori_y.rajakytkin_1_tila == 1:
                        self.moottori_y.esta_liike()
                        self.vaihda_suunta(moottorin_nimi)
                        print("y tuli 1-kytkimelle")
                        self.irrota_kytkimelta(self.moottori_y)
                    elif self.moottori_y.rajakytkin_0_tila == 0 and self.moottori_y.rajakytkin_1_tila == 0:
                        #print("y voi liikkua")
                        return
                    else: 
                        self.moottori_y.esta_liike()
                        print("y:n rajakytkimien lukemisessa ongelmia")
            except serial.SerialTimeoutException:
                print("USB-yhteys katkesi")
        elif moottorin_nimi == 'z':
            try:
                kytkimen_tila_0 = self.kortti.digital[self.moottori_z.rajakytkin_0].read()
     #           print("1: z:n 0-kytkimen lukemisen jälkeen tila: {0}".format(kytkimen_tila_0)) #TESTAUSTA
                kytkimen_tila_1 = self.kortti.digital[self.moottori_z.rajakytkin_1].read()
     #           print("1: z:n 1-kytkimen lukemisen jälkeen tila: {0}".format(kytkimen_tila_0)) #TESTAUSTA
                while kytkimen_tila_0 is None or kytkimen_tila_1 is None:
                    print("odotetaan yhteyttä z:n kytkimiin")
                    time.sleep(0.1)
                    kytkimen_tila_0 = self.kortti.digital[self.moottori_z.rajakytkin_0].read()
                    kytkimen_tila_1 = self.kortti.digital[self.moottori_z.rajakytkin_1].read()
                else:
                    self.moottori_z.set_rajakytkin_0_tila(kytkimen_tila_0)
                    self.moottori_z.set_rajakytkin_1_tila(kytkimen_tila_1)
              #      print("Z: kytkin0: {0}, kytkin1: {1}".format(kytkimen_tila_0, kytkimen_tila_1))
                    if self.moottori_z.rajakytkin_0_tila == 1:
                        self.moottori_z.esta_liike()
                        self.moottori_z.nollaa_sijainti()
                        self.vaihda_suunta(moottorin_nimi)
                        print("z tuli 0-kytkimelle")
                        self.irrota_kytkimelta(self.moottori_z)
                    elif self.moottori_z.rajakytkin_1_tila == 1:
                        self.moottori_z.esta_liike()
                        self.vaihda_suunta(moottorin_nimi)
                        print("z tuli 1-kytkimelle")
                        self.irrota_kytkimelta(self.moottori_z)
                    elif self.moottori_z.rajakytkin_0_tila == 0 and self.moottori_z.rajakytkin_1_tila == 0:
    #                    print("z voi liikkua")
                        return
                    else: 
                        self.moottori_z.esta_liike()
                        print("z:n rajakytkimien lukemisessa ongelmia")
            except serial.SerialTimeoutException:
                print("USB-yhteys katkesi")
        else: 
            print("Tarkista tarkista_kytkimet()-kutsun oikeellisuus.")


    """ Metodi jolla asetetaan suunta halutun moottorin liikuttamista varten. 
    Parametereinä moottorin nimi ja 1 tai 0, 
    missä 0= vastapäivään, 1= myötäpäivään."""
    def set_suunta(self, moottorin_nimi, myota_vai_vasta):
#        print("set_suunta sai suunta-arvoksi: ", myota_vai_vasta)
        if moottorin_nimi == 'x':
            moottori = self.moottori_x
            dir_pin = self.moottori_x.dir_pin
        elif moottorin_nimi == 'y':
            moottori = self.moottori_y
            dir_pin = self.moottori_y.dir_pin
        elif moottorin_nimi == 'z':
            moottori = self.moottori_z
            dir_pin = self.moottori_z.dir_pin
        else: print("Moottorin nimen tulee olla x, y tai z")
        if myota_vai_vasta == 0:
            self.kortti.digital[dir_pin].write(0) # LOW-arvolla vastapäivään
            moottori.set_suunta(0)
            if moottori.palaamassa == True: 
                moottori.lahtee() #tämä tarpeen, koska x ja z palaavat erisuuntaisella moottorinliikkeellä kuin y
            else: moottori.palaa() 
        elif myota_vai_vasta == 1:
            self.kortti.digital[dir_pin].write(1)
            moottori.set_suunta(1)
            if moottori.palaamassa == True: 
                moottori.lahtee() 
            else: moottori.palaa() 
        else: print("Suunnan suunta-arvoksi tulee antaa 0 (vastapäivään) tai 1 (myötäpäivään)")


    """ Metodi jolla vaihdetaan parametrina annetun moottorin nykyinen 
    liikkumasuunta päinvastaiseksi."""
    def vaihda_suunta(self, moottorin_nimi):
        if moottorin_nimi == 'x':
            moottori = self.moottori_x
            dir_pin = self.moottori_x.dir_pin
        elif moottorin_nimi == 'y':
            moottori = self.moottori_y
            dir_pin = self.moottori_y.dir_pin
        elif moottorin_nimi == 'z':
            moottori = self.moottori_z
            dir_pin = self.moottori_z.dir_pin
        else: print("Suuntaa vaihdettaessa moottorin nimen tulee olla x, y tai z")
        if moottori.dir_pin_tila == 0:
            self.kortti.digital[dir_pin].write(1)
            time.sleep(0.1)
            moottori.set_suunta(1)
            if moottori.palaamassa == True:
                moottori.lahtee()
            else: moottori.palaa()
        elif moottori.dir_pin_tila == 1:
            self.kortti.digital[dir_pin].write(0)
            time.sleep(0.1)
            moottori.set_suunta(0)
            if moottori.palaamassa == True:
                moottori.lahtee()
            else: moottori.palaa()
        else: 
            print("vaihda_suunta()-metodissa attribuutin dir_pin tilaksi asetettiin: ", dir_pin) # KOODIN TESTAILUUN
            


#TODO:tähän lisättävä myöhemmin kiihdytys ja pehmennys, mikäli askelia hukataan kameran painon kanssa.
    """ Metodi jolla liikutetaan valittua moottoria asetettu askelmäärää. Jos
    kesken matkan tullaan rajakytkimelle, moottori pystähtyy siihen, eikä käytä 
    jäljellä olevia askelia palaamiseen."""
    def liiku_askelta(self, moottorin_nimi, montako_askelta):        
        if moottorin_nimi == 'x':
            moottori = self.moottori_x
            step_pin = self.moottori_x.step_pin
            viive = self.viive
        elif moottorin_nimi == 'y':
            step_pin = self.moottori_y.step_pin
            moottori = self.moottori_y
            viive = self.viive_y
        elif moottorin_nimi == 'z':
            step_pin = self.moottori_z.step_pin
            moottori = self.moottori_z
            viive = self.viive
        else: print("Moottorin nimen tulee olla x, y tai z")
        try:
            for i in range(montako_askelta):
                self.tarkista_kytkimet(moottorin_nimi)
                if moottori.voi_liikkua == True:
                    self.kortti.digital[step_pin].write(1) 
                    time.sleep(viive)
                    self.kortti.digital[step_pin].write(0)
                    time.sleep(viive)
                    self.laskuri(moottori)
                else: 
                    time.sleep(0.1) 
                    break
        except serial.SerialTimeoutException:
            print("USB-yhteys katkesi")
 #       print('Moottori {0}:n sijainti on nyt {1}.'.format(moottorin_nimi, moottori.sijainti)) #TESTAUKSEEN
        moottori.salli_liike()


    """y-moottorin liikutteluun käyttäjän haluamalla nopeudella. Muuten käytännössä sama kuin yllä.
    Nopeus-parametri: mitä pienempi luku, sitä nopeampi vauhti. Kuitenkin vähintään 2.6"""
    def skannaa_askelta_nopeudella(self, askeleet, nopeus):
        if nopeus < 4: #TODO: Tai mikä arvo tähän lopulta määrittyykään
            print("Anna suurempi nopeuskerroin skannausfunktion attribuuttina! Arvon tulee olla vähintään 2.6")
            self.moottori_x.esta_liike()
            self.moottori_y.esta_liike()
            self.moottori_z.esta_liike()
            return
        step_pin = self.moottori_y.step_pin
        moottori = self.moottori_y
        kustomoitu_viive = nopeus * (1e-6) 
        try:
            for i in range(askeleet):
                self.tarkista_kytkimet(moottori.nimi)
                if moottori.voi_liikkua == True:
                    self.kortti.digital[step_pin].write(1) 
                    time.sleep(kustomoitu_viive) 
                    self.kortti.digital[step_pin].write(0)
                    time.sleep(kustomoitu_viive)
                    self.laskuri(moottori)
                else: 
                    time.sleep(0.1)
                    break
        except serial.SerialTimeoutException:
            print("USB-yhteys katkesi")
#        print('Moottori {0}:n sijainti on nyt {1}.'.format(moottori.nimi, moottori.sijainti)) #TESTAUKSEEN
        moottori.salli_liike()


    """ Käytetään AINOASTAAN funktiossa tarkista_kytkimet() rajakytkimelle tulon 
    yhteydessä, moottorin liikuttamiseen kytkimeltä lyhyen matkaa pois päin"""
    def irrota_kytkimelta(self, moottori):
        step_pin = moottori.step_pin
        if moottori == self.moottori_y:
            viive = self.viive_y
        else:
            viive = self.viive
        if moottori.voi_liikkua == False:
            for i in range(540):
                self.kortti.digital[step_pin].write(1) 
                time.sleep(viive) 
                self.kortti.digital[step_pin].write(0)
                time.sleep(viive)
                self.laskuri(moottori)
            

    """ Käytetään annetun moottorin laskuria tilanteseen sopivalla tavalla"""
    def laskuri(self, moottori):
        if moottori.palaamassa == False:
            moottori.kasvata_sijaintia()
        else:
            moottori.vahenna_sijaintia()
            

    """ Metodi kaikkien moottoreiden viimeisimmän sijaintitiedon palauttamista varten, 
        palauttaa Numpy arrayn."""
    def get_sijainti(self):
        sijainti = np.array([self.moottori_x.sijainti, self.moottori_y.sijainti, self.moottori_z.sijainti])        
        return sijainti


    """ Nollaa moottoreiden sijainniksi (0, 0, 0)"""
    def nollaa_sijainnit(self):
        self.moottori_x.nollaa_sijainti()
        self.moottori_y.nollaa_sijainti()
        self.moottori_z.nollaa_sijainti()
        

    """ Printtaa konsoliin käyttäjän otetun portin nimen. 
    Nimi löytyy esim. Arduinon kautta"""
    def print_portti(self):
        print("Käytössä oleva portti:", self.portti)
    
    
    """ Metodi joka printtaa konsoliin kolmen mottorin kytkentätiedot sekä
    moottoriominaisuuksista steps per revolution -tiedon"""
    def print_moottorien_kytkennat(self):
        print("Moottoreiden määritykset:")
        self.moottori_x.print_kytkennat()
        self.moottori_y.print_kytkennat()
        self.moottori_z.print_kytkennat()


    def lopeta(self):
        self.kortti.exit()
   
     
"""
    Luokka lineaarikuvauksen ohjaamista varten. Luokka käyttää yhtä moottorit-oliota
    ja huolehtii lineaarikuvauksen kameran liikuttelua varten asetettavista tiedoista. 
    Luokka sisältää kaikki ohjainohjelmiston käyttäjälle tarjoamat toiminnot.
"""        
class Ohjain:
    
    """ Konstruktori. Ohjain-olio voidaan luoda joko oletusaloituskohdalla (0,0,0) 
    tai osin tai kokonaan toisin määritellyllä aloituskohdalla."""
    def __init__(self, moottorit):
        self.moottorit = moottorit
        self.moottorit.set_suunta('x', 0) # 0
        self.moottorit.set_suunta('y', 1) # 1 
        self.moottorit.set_suunta('z',0) # 0 suunnat joilla kelkka siiretään koordinaatin sijaintiin (0,0,0)
        self.maaritykset = {
            "x" : 0, 
            "y_alku" : 0, 
            "z" : 0,
            "y_loppu" : 51500, #TODO: Määritä kehikkoon nähden sopiva oletusarvo y:lle lopetuskohtaa varten 
            "x_siirtyma" : 500 #TODO: Määritä sopiva oletusarvo siirtymälle
        }
    #    kokeilu = {'col1': [1, 2], 'col2': [3, 4]} #TESTI
    #    kuvaustiedot = pd.DataFrame(kokeilu)
    #    print(kuvaustiedot) #TESTI
        self.alkuun(moottorit)
        print("\nJärjestelmä on valmiina. Ohjeita liikutteluun:\nohjain.ohjeet()\nmitat()\n")


    """Käynnistettäessä varmistutaan, että kelkkaa lähdetään liikuttelemaan 0-sijainnista 
    (välttämätöntä sijaintitiedon määrittämiseksi). Moottorien suunta vaihdettu valmiiksi
    kytkimeltä pois päin."""
    def alkuun(self, moottorit):
        print("Alustus:")
        moottorit.liiku_askelta('x', 90000) 
        moottorit.skannaa_askelta_nopeudella(70000, 4) # tässä ei toimi self.moottorit.viive_y  #tässä eri funktiolla, koska y:n vauhdit ovat erilaiset kuin x ja z
        moottorit.liiku_askelta('z', 20000) #Ei tarvitse olla "tuplasti suurempi arvo", sillä z:n suuntainen akseli on kehikossa selvästi muita lyhyempi 
        moottorit.nollaa_sijainnit()
        sijainti = self.sijainti()
        print(sijainti)
        

    """ Käyttäjä määrittää varsinaiselle skannaukselle muun aloituspisteen
    kuin (0,0,0). Pisteen tiedot laitetaan muistiin ja kelkka siirretään aloituspisteeseen."""
    def aloituskohta(self, x, y, z):    
        self.maaritykset["x"] = x
        self.maaritykset["y_alku"] = y
        self.maaritykset["z"] = z
        print('Kuvauksen aloituskohdaksi määritettiin ({0}, {1}, {2})'.format(self.maaritykset["x"], self.maaritykset["y_alku"], self.maaritykset["z"]))
        self.siirry_askelta(x, y, z)


    """Liikutetaan nimettyä moottoria haluttu askelmäärä."""
    def siirry_askelta(self, x, y, z):
        self.moottorit.liiku_askelta('x', x)
        self.moottorit.liiku_askelta('y', y)
        self.moottorit.liiku_askelta('z', z)  
   #     print("\n")
        
        
    """ skannataan y-suuntaisesti annetulla nopeudella. Nopeus-parametri 
        tarkoittaa tässä moottorin liikuttelussa annettujen LOW-HIGH-impulssien välisen ajan
        määrittelyssä käytettyä kerrointa. 
        Parametrit: askeleet: y-moottorin liikuttelun askelmäärä, 
        nopeus: millä nopeudella liikutellaan"""
    def skannaa_askelta_nopeudella(self, askeleet, nopeus):
        self.moottorit.skannaa_askelta_nopeudella(askeleet, nopeus) 
        print("\n")

    
    """ Metodi jolla vaihdetaan halutun moottorin liikkumissuunnta päinvastaiseksi. 
    Parametereinä moottorin nimi."""
    def vaihda_suunta(self, moottorin_nimi):
        self.moottorit.vaihda_suunta(moottorin_nimi)
        

    """ Käyttäjä määrittää lopetuskohdan skannausta varten. Kohtaa tarkoittavalla luvulla tarkoitetaan
    sijaintipistettä (= askelmäärä nollasta lopetuskohtaan). Piste laitetaan muistiin skannaustoimintoa varten."""
    def lopetuskohta(self, y):    
        self.maaritykset["y_loppu"] = y
        print('Kuvauksen ensimmäisen siivun lopetuskohdaksi määritettiin ({0}, {1}, {2})'.format(self.maaritykset["x"], self.maaritykset["y_loppu"], self.maaritykset["z"]))
        
        
    def siirtyma(self, x):
        self.maaritykset["x_siirtyma"] = x
        print("Kuvattavan viipaleen paksuudeksi määriteltiin {0}".format(self.maaritykset["x_siirtyma"]))
        
        
    """ Ennen tämän käyttöä tulee olla määritettynä aloistus- ja lopetuspiste sekä 
    kuvattavan viipaleen paksuus (tai käytetään oletusarvoja). 
    Metodin alussa kelkka on aloituspisteessä. Siirrytään skannausmodessa lopetuspisteeseen, 
    palataan alkuun ja siirrytään määritetyn siirtymän verran oikealle, skannataan uudestaan 
    y:n suhteen lopetuspisteeseen... Pysähdytään kunnes on kuvattu parametrinä annettu
    määrä siirtymiä tai tultu rajakytkimelle"""
    def skannaa_viipaletta_nopeudella(self, frame_nimi, viipaleiden_maara, nopeus):
        y_liikuttava_matka = self.maaritykset['y_loppu'] - self.maaritykset['y_alku']
        siirtyma_laskuri = 0
        kuvaustiedot = { 'frame_nimi': [], 'alkusijainti': [], 'loppusijainti': [], 'aloitusaika': [], 'lopetusaika': [] }
        for viipaleet in range(viipaleiden_maara):
            alkusijainti = self.sijainti() #NA siivun alkusijainnista
            aloitus = time.time()
            self.moottorit.skannaa_askelta_nopeudella(y_liikuttava_matka, nopeus) #liikutaan tasaisesti y:n suhteen aloituspisteestä lopetuspisteeseen
            lopetus = time.time()
            loppusijainti = self.sijainti() #NA silmukan lopputilanteesta
            kuvaustiedot["frame_nimi"].append(frame_nimi)
            kuvaustiedot["alkusijainti"].append(alkusijainti)
            kuvaustiedot["loppusijainti"].append(loppusijainti)
            kuvaustiedot["aloitusaika"].append(aloitus)
            kuvaustiedot["lopetusaika"].append(lopetus)
            self.vaihda_suunta("y") #paluuta varten
            self.siirry_askelta(0, y_liikuttava_matka, 0)#self.siirry_askelta(0, self.maaritykset["y_alku"], 0) #palataan aloituspisteeseen
            self.vaihda_suunta("y") #y valmiina uutta skannausta varten
            siirtyma_laskuri += 1
            if siirtyma_laskuri < viipaleiden_maara: 
                self.siirry_askelta(self.maaritykset['x_siirtyma'], 0, 0)
        kuvaustietojen_taulukko = pd.DataFrame(data=kuvaustiedot)
        return kuvaustietojen_taulukko
         
    """ Metodi kaikkien moottoreiden viimeisimmän sijaintitiedon palauttamista varten, 
    palauttaa Numpy arrayn."""
    def sijainti(self):      
        sijainti = self.moottorit.get_sijainti()
        return sijainti
        
    
    """Sarjaportin sulkeminen lopuksi."""
    def lopeta(self):
        self.moottorit.lopeta() 
        
        
    def ohjeet(self):
        print("\nVoit ohjata kelkkaa vapaasti (esim. alkumääritysten tekemiseksi) funktioilla:\n .skannaa_askelta_nopeudella(askeleet=int, nopeus=int)\n .siirry(x_askeleet=int, y_askeleet=int, z_askeleet=int)\n .vaihda_suunta(moottorin_nimi=string)\nSkannaamista varten määritä alkupiste, loppupiste ja siirtymän leveys askelina:\n .set_aloituskohta(x=int, y=int, z=int) \n --> sijainti laitetaan muistiin JA kelkka siirretään aloituskohtaan\n .set_lopetuskohta(y=int)\n --> lopetuskohta laitetaan muistiin ja käytetään skannatessa\n .skannaa_viipaletta_nopeudella(montako=int, nopeuskerroin=int)\n --> kelkkaa siirretään aloituskohdasta lopetuskohtaan tasaista vauhtia, minkä jälkeen palataan aloituskohtaan, siirrytään siirtymän verran oikealle ja skannataan uudestaan.")
    
    def mitat(self):
        print("Esimerkkimittoja moottorien liikutteluun:\nX\nKoko väli: 66cm = 65 532 askelta\npuoliväli:33cm = 32 766 askelta\n10cm = 9 929 askelta\n1cm = 993 askelta\nY\nKoko väli: 52.3cm = 51705 askelta\nPuoliväli: 26.15 cm = 25853 askelta\n10cm = 9886 askelta\n1cm = 989 askelta\nZ\nKoko väli: 11cm = 14 514 askelta\nPuoliväli: 5,5cm = 7 257  askelta\n10cm = 13 195 askelta\n1cm = 1 319 askelta")
        
        
def main():
    #KÄYNNISTÄMISTOIMET:
    moottori_x = Moottori('x', 30, 32, 200, 2, 13) #oltava valmiina (kajotaan vain jos kytkentöihin tulee muutoksia)
    moottori_y = Moottori('y', 26, 28, 200, 8, 6) #oltava valmiina (kajotaan vain jos kytkentöihin tulee muutoksia)
    moottori_z = Moottori('z', 22, 24, 400, 7, 9) #oltava valmiina (kajotaan vain jos kytkentöihin tulee muutoksia)
    moottorit = Moottorit('COM7', moottori_x, moottori_y, moottori_z) # valmiina, selvitä 1.kerralla käytetty portti Arduino-IDEn avulla
    ohjain = Ohjain(moottorit)
    ohjain.mitat()

    #KÄYTTÄJÄN TOIMIEN KOKEILUA:
#    ohjain.ohjeet()

   # LIIKUTTELUN TAPA1:
 #   ohjain.skannaa_askelta_nopeudella(200, 100)
 #   ohjain.skannaa_askelta_nopeudella(2000, 3)
  #  ohjain.siirry_askelta(90000, 70000, 20000) #tällä voi ajaa alustuken jälkeen koko väliä
 #   ohjain.siirry_askelta(0, 70000, 0)
 #   ohjain.siirry_askelta(20000, 0, 0) 
 #   ohjain.siirry_askelta(0, 0, 400)
#    ohjain.vaihda_suunta("z")
#    ohjain.siirry_askelta(0, 0, 400)
 #   sijaintitiedot = ohjain.sijainti()
 #   print(sijaintitiedot)
#    ohjain.vaihda_suunta("x") 
#    ohjain.siirry_askelta(400, 0, 0)
 #   ohjain.vaihda_suunta("y") 
 #   ohjain.skannaa_askelta_nopeudella(400, 0.00001) #myötäp.
 #   sijaintitiedot = ohjain.sijainti()
 #   print(sijaintitiedot) #odotustuloste: (0,0,0)

   # print(type(sijaintitiedot)) #TESTAUSTA


    #TAPA2:
    ohjain.aloituskohta(0, 0, 400) 
    ohjain.lopetuskohta(24177)
    ohjain.siirtyma(3723)
    kuvaustiedot = ohjain.skannaa_viipaletta_nopeudella("framet_1", 8, 4) # 4=sama nopeus kuin muuallakin
    print(kuvaustiedot)
    #KULJETUN MATKAN PITUUDEN TESTIT:
    #ohjain.siirry_askelta(13901, 0, 0) #T
    #ohjain.siirry_askelta(32766, 0, 0) #T
    #ohjain.siirry_askelta(39717, 0, 0) #T
    #ohjain.siirry_askelta(0, 15813, 0) #T
    #ohjain.siirry_askelta(0, 25853, 0) #T
    #ohjain.siirry_askelta(0, 39544, 0) #T
    #ohjain.siirry_askelta(0, 0, 13195) #T
    #ohjain.siirry_askelta(0, 0, 7257) #T
    #ohjain.siirry_askelta(0, 0, 3957) #T
    #ohjain.siirry_askelta(0, 0, 660) #T
    #KOKO VÄLIN KULKEMINEN ILMAN ETTÄ TULLAAN KYTKIMELLE
    #ohjain.siirry_askelta(65532, 0, 0)#Ok
    #ohjain.siirry_askelta(0, 51705, 0) #ok, varalta ottaisin pari askelta pois tästä
    #ohjain.siirry_askelta(0, 0,14514)
    
   
    ohjain.lopeta() #Toimii - tämän jälkeen ei voi liikutella
if __name__ == "__main__":
    main()