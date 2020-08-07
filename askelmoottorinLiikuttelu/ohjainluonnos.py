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
        self.rajakytkin_0_tila = 0
        self.rajakytkin_1 = rajakytkin_1
        self.rajakytkin_1_tila = 0
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
    
    
    """ Konstruktori. Parametreinä usb-kaapelin käyttämä pc:n portti ja x-, y-
        ja z-akseleilla kelkkaa liikuttelevat moottorit."""
    def __init__(self, portti, moottori_x, moottori_y, moottori_z):
            self.portti = portti
            self.kortti = pyfirmata.Arduino(portti) #Arduino.AUTODETECT ei tässä toiminut
            self.moottori_x = moottori_x
            self.moottori_y = moottori_y
            self.moottori_z = moottori_z 
            self.iteraattori = pyfirmata.util.Iterator(self.kortti)
            self.iteraattori.start()
            self.kortti.digital[moottori_x.rajakytkin_0].mode = pyfirmata.INPUT # oletuksena OUTPUT?
            self.kortti.digital[moottori_x.rajakytkin_1].mode = pyfirmata.INPUT
            self.kortti.digital[moottori_y.rajakytkin_0].mode = pyfirmata.INPUT
            self.kortti.digital[moottori_y.rajakytkin_1].mode = pyfirmata.INPUT
            self.kortti.digital[moottori_z.rajakytkin_0].mode = pyfirmata.INPUT
            self.kortti.digital[moottori_z.rajakytkin_1].mode = pyfirmata.INPUT

            
    """ Metodi joka tarkistaa parametrissä nimetyn moottorin osalta, onko tultu
        jommalle kummalle sen rajakytkimistä. Jos tullaan kytkimelle, asetetaan
        moottorin liikkumissuunta valmiiksi päinvastaiseksi."""
    def tarkista_kytkimet(self, moottorin_nimi):
        if moottorin_nimi == 'x':
            kytkimen_tila_0 = self.kortti.digital[self.moottori_x.rajakytkin_0].read()
            kytkimen_tila_1 = self.kortti.digital[self.moottori_x.rajakytkin_1].read()
            while kytkimen_tila_0 is None or kytkimen_tila_1 is None:
                print("odotetaan yhteyttä x:n kytkimiin")
                time.sleep(0.1)
                kytkimen_tila_0 = self.kortti.digital[self.moottori_x.rajakytkin_0].read()
                kytkimen_tila_1 = self.kortti.digital[self.moottori_x.rajakytkin_1].read()
            else:
                self.moottori_x.set_rajakytkin_0_tila(kytkimen_tila_0)
                self.moottori_x.set_rajakytkin_1_tila(kytkimen_tila_1)
          #      print("X: kytkin0: {0}, kytkin1: {1}".format(kytkimen_tila_0, kytkimen_tila_1))
                if self.moottori_x.rajakytkin_0_tila == 1:
                    self.moottori_x.nollaa_sijainti() #tultiin sijaintiin 0
                    self.vaihda_suunta(moottorin_nimi) #rajakytkimellä käännyttävä
                    self.moottori_x.lahtee() #laskuri tietää kasvattaa sijaintilukemaa
                    print("x tuli 0-kytkimelle")
                    self.moottori_x.esta_liike()
                elif self.moottori_x.rajakytkin_1_tila == 1:
                    self.vaihda_suunta(moottorin_nimi)
                    self.moottori_x.palaa() # laskuri tietää vähentää sijaintilukemaa
                    print("x tuli 1-kytkimelle")
                    self.moottori_x.esta_liike()
                elif self.moottori_x.rajakytkin_0_tila == 0 and self.moottori_x.rajakytkin_1_tila == 0:
     #             print("x voi liikkua")
                    return
                else:
                    print("x:n rajakytkimien lukemisessa ongelmia")
                    self.moottori_x.esta_liike()
        elif moottorin_nimi == 'y':
            kytkimen_tila_0 = self.kortti.digital[self.moottori_y.rajakytkin_0].read()
            kytkimen_tila_1 = self.kortti.digital[self.moottori_y.rajakytkin_1].read()
            while kytkimen_tila_0 is None or kytkimen_tila_1 is None:
                print("odotetaan yhteyttä y:n kytkimiin")
                time.sleep(0.1)
                kytkimen_tila_0 = self.kortti.digital[self.moottori_y.rajakytkin_0].read()
                kytkimen_tila_1 = self.kortti.digital[self.moottori_y.rajakytkin_1].read()
            else:
                self.moottori_y.set_rajakytkin_0_tila(kytkimen_tila_0)
                self.moottori_y.set_rajakytkin_1_tila(kytkimen_tila_1)
            #    print("Y: kytkin0: {0}, kytkin1: {1}".format(kytkimen_tila_0, kytkimen_tila_1))
                if self.moottori_y.rajakytkin_0_tila == 1:
                    self.moottori_y.esta_liike()
                    self.moottori_y.nollaa_sijainti()
                    self.vaihda_suunta(moottorin_nimi)
                    self.moottori_y.lahtee()
                    print("y tuli 0-kytkimelle")
                elif self.moottori_y.rajakytkin_1_tila == 1:
                    self.moottori_y.esta_liike()
                    self.vaihda_suunta(moottorin_nimi)
                    self.moottori_y.palaa()
                    print("y tuli 1-kytkimelle")
                elif self.moottori_y.rajakytkin_0_tila == 0 and self.moottori_y.rajakytkin_1_tila == 0:
                    #print("y voi liikkua")
                    return
                else: 
                    self.moottori_y.esta_liike()
                    print("y:n rajakytkimien lukemisessa ongelmia")
        elif moottorin_nimi == 'z':
            kytkimen_tila_0 = self.kortti.digital[self.moottori_z.rajakytkin_0].read()
            kytkimen_tila_1 = self.kortti.digital[self.moottori_z.rajakytkin_1].read()
            while kytkimen_tila_0 is None or kytkimen_tila_1 is None:
                print("odotetaan yhteyttä z:n kytkimiin")
                time.sleep(0.1)
                kytkimen_tila_0 = self.kortti.digital[self.moottori_z.rajakytkin_0].read()
                kytkimen_tila_1 = self.kortti.digital[self.moottori_z.rajakytkin_1].read()
            else:
                self.moottori_z.set_rajakytkin_0_tila(kytkimen_tila_0)
                self.moottori_z.set_rajakytkin_1_tila(kytkimen_tila_1)
              #  print("Z: kytkin0: {0}, kytkin1: {1}".format(kytkimen_tila_0, kytkimen_tila_1))
                if self.moottori_z.rajakytkin_0_tila == 1:
                    self.moottori_z.esta_liike()
                    self.moottori_z.nollaa_sijainti()
                    self.vaihda_suunta(moottorin_nimi)
                    self.moottori_z.lahtee()
                    print("z tuli 0-kytkimelle")
                elif self.moottori_z.rajakytkin_1_tila == 1:
                    self.moottori_z.esta_liike()
                    self.vaihda_suunta(moottorin_nimi)
                    self.moottori_z.palaa()
                    print("z tuli 1-kytkimelle")
                elif self.moottori_z.rajakytkin_0_tila == 0 and self.moottori_z.rajakytkin_1_tila == 0:
    #               print("z voi liikkua")
                    return
                else: 
                    self.moottori_z.esta_liike()
                    print("z:n rajakytkimien lukemisessa ongelmia")
        else: 
            print("Tarkista tarkista_kytkimet()-kutsun oikeellisuus.")
            # moottorin_nimen oikeellisuus tarkistetaan kutsuketjussa ylempänä


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
                moottori.lahtee() #TÄMÄ IFFITTELY ON TURHA, KUNHAN TIEDETÄÄN, KUMPI SUUNTA MERKITSEE PALAAMISTA
            else: moottori.palaa() #...turha kun tiedetään...
        elif myota_vai_vasta == 1:
            self.kortti.digital[dir_pin].write(1)
            moottori.set_suunta(1)
            if moottori.palaamassa == True: 
                moottori.lahtee() #TÄMÄ IFFITTELY ON TURHA, KUNHAN TIEDETÄÄN, KUMPI SUUNTA MERKITSEE PALAAMISTA
            else: moottori.palaa() #...turha kun tiedetään...
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
            time.sleep(1)
            moottori.set_suunta(1)
            if moottori.palaamassa == True:
                moottori.lahtee()
            else: moottori.palaa()
        elif moottori.dir_pin_tila == 1:
            self.kortti.digital[dir_pin].write(0)
            time.sleep(1)
            moottori.set_suunta(0)
            if moottori.palaamassa == True:
                moottori.lahtee()
            else: moottori.palaa()
        else: 
            print("vaihda_suunta() dir_pin: ", dir_pin) # KOODIN TESTAILUUN
            print("Suunta-arvoksi tulee antaa 0 (vastapäivään) tai 1 (myötäpäivään)")


#TODO:tähän lisättävä myöhemmin kiihdytys ja pehmennys, mikäli askelia hukataan kameran painon kanssa.
    """ Metodi jolla liikutetaan valittua moottoria asetettu askelmäärää. Jos
    kesken matkan tullaan rajakytkimelle, moottori pystähtyy siihen, eikä käytä 
    jäljellä olevia askelia palaamiseen."""
    def liiku_askelta(self, moottorin_nimi, montako_askelta):
        if moottorin_nimi == 'x':
            moottori = self.moottori_x
            step_pin = self.moottori_x.step_pin           
        elif moottorin_nimi == 'y':
            step_pin = self.moottori_y.step_pin
            moottori = self.moottori_y
        elif moottorin_nimi == 'z':
            step_pin = self.moottori_z.step_pin
            moottori = self.moottori_z
        else: print("Moottorin nimen tulee olla x, y tai z")
        try:
            for i in range(montako_askelta):
                self.tarkista_kytkimet(moottorin_nimi)
                if moottori.voi_liikkua == True:
                    self.kortti.digital[step_pin].write(1) 
                    time.sleep(500 * 10**(-6)) # nopea liike
                    self.kortti.digital[step_pin].write(0)
                    time.sleep(500 * 10**(-6))
                    self.laskuri(moottori)
                else: 
                  #  print("Moottori {0} ei voi liikkua enempää tähän suuntaan.".format(moottorin_nimi))
                    time.sleep(1) #??
                    break
        except serial.SerialTimeoutException:
            print("USB-yhteys katkesi")
        print('Moottori {0}:n sijainti on nyt {1}.'.format(moottorin_nimi, moottori.sijainti))
        moottori.salli_liike()


    """ Metodi jolla liikutetaan y-moottoria asetettu askelmäärää hitaammin
    kuin liiku_askelta()-metodilla. Tähän olisi tarkoitus määrittää testaamalla 
    "turvalliseksi" todettu nopeus"""
    def skannaa_askelta(self, montako_askelta):
        step_pin = self.moottori_y.step_pin
        moottori = self.moottori_y
        try:
            for i in range(montako_askelta):
                self.tarkista_kytkimet(moottori.nimi) #tarvitaanko getteri?
                if moottori.voi_liikkua == True:
                    self.kortti.digital[step_pin].write(1) 
                    time.sleep(4000 * 10**(-6)) #TODO: Määritä riittävän hidas vauhti 
                    self.kortti.digital[step_pin].write(0)
                    time.sleep(4000 * 10**(-6))
                    self.laskuri(moottori)
                else: 
                    time.sleep(1) #??
                    print("y-moottori ei voi liikkua enempää tähän suuntaan.")
                    break
        except serial.SerialTimeoutException:
            print("USB-yhteys katkesi")
        print('Moottori {0}:n sijainti on nyt {1}.'.format(moottori.nimi, moottori.sijainti))
        moottori.salli_liike()


    """y-moottorin liikutteluun käyttäjän haluamalla nopeudella. Muuten käytännössä sama kuin yllä.
    Nopeuds-parametri: esim 500 nopeampi kuin 4000"""
    def skannaa_askelta_nopeudella(self, askeleet, nopeus):
        step_pin = self.moottori_y.step_pin
        moottori = self.moottori_y
        try:
            for i in range(askeleet):
                self.tarkista_kytkimet(moottori.nimi) #tarvitaanko getteri?
                if moottori.voi_liikkua == True:
                    self.kortti.digital[step_pin].write(1) 
                    time.sleep(nopeus * 10**(-6)) #TODO: Määritä riittävän hidas vauhti 
                    self.kortti.digital[step_pin].write(0)
                    time.sleep(nopeus * 10**(-6))
                    self.laskuri(moottori)
                else: 
                    time.sleep(1) #??
                    print("Y-moottori ei voi liikkua enempää tähän suuntaan.")
                    break
        except serial.SerialTimeoutException:
            print("USB-yhteys katkesi")
        print('Moottori {0}:n sijainti on nyt {1}.'.format(moottori.nimi, moottori.sijainti))
        moottori.salli_liike()


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
    Luokka kuvaustapahtuman hallintaa varten. Luokka käyttää yhtä moottorit-oliota
    ja huolehtii yksittäisistä kuvaustapahtumaa varten asetettavista tiedoista. 
    Luokka sisältää kaikki ohjainohjelmiston käyttäjälle tarjoamat toiminnot.
"""        
class Kuvaus:
    
    """ Konstruktorit. Kuvaus-olio voidaan luoda joko oletusaloituskohdalla (0,0,0) 
    tai osin tai kokonaan toisin määritellyllä aloituskohdalla."""
    def __init__(self, moottorit):
        self.moottorit = moottorit
        self.moottorit.set_suunta('x', 1) #TODO: Varmista että alustetut suunnat ovat oikeat:
        self.moottorit.set_suunta('y', 1)
        self.moottorit.set_suunta('z', 1) # eli ne joilla kelkka siiretään 0-sijaintiin
        self.maaritykset = {
            "x" : 0, 
            "y_alku" : 0, 
            "z" : 0,
            "y_loppu" : 1000, #TODO: Määritä kehikkoon nähden sopiva oletusarvo y:lle lopetuskohtaa varten 
            "x_siirtyma" : 5 #TODO: Määritä sopiva oletusarvo siirtymälle
        }
        self.alkuun(moottorit)
        print("\nJärjestelmä on valmiina. Ohjeita liikutteluun: kuvaus.ohjeet()\n")


    """Käynnistettäessä varmistutaan, että kelkkaa lähdetään liikuttelemaan 0-sijainnista 
    (välttämätöntä sijaintitiedon määrittämiseksi). Moottorien suunta vaihdettu valmiiksi
    kytkimeltä pois päin."""
    def alkuun(self, moottorit):
        moottorit.liiku_askelta('x', 20000) #TODO:Tarpeeksi iso luku jotta tullaan varmasti 0:aan?
        moottorit.liiku_askelta('y', 20000) #TODO:Tarpeeksi iso luku?
        moottorit.liiku_askelta('z', 40000) #TODO:Tarpeeksi iso luku - muista tuplata!


    """ Käyttäjä määrittää varsinaiselle skannaukselle muun aloituspisteen
    kuin (0,0,0). Pisteen tiedot laitetaan muistiin ja kelkka siirretään aloituspisteeseen."""
    def aloituskohta(self, x, y, z):    
        self.maaritykset["x"] = x
        self.maaritykset["y_alku"] = y
        self.maaritykset["z"] = z
        print('Kuvauksen aloituskohdaksi on määritetty (x{0}, y{1}, z{2})'.format(self.maaritykset["x"], self.maaritykset["y_alku"], self.maaritykset["z"]))
        self.siirry_askelta(x, y, z)#TODO:Tarpeeksi isot luvut jotta tullaan varmasti 0:aan? z tuplana!


    """Liikutetaan nimettyä moottoria haluttu askelmäärä."""
    def siirry_askelta(self, x, y, z):
        self.moottorit.liiku_askelta('x', x)
        self.moottorit.liiku_askelta('y', y)
        self.moottorit.liiku_askelta('z', z)  
        print("\n")
 
    
    def skannaa_askelta(self, askeleet):
        self.moottorit.skannaa_askelta(askeleet) 
        print("\n")
        
        
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
        print('Kuvauksen lopetuskohdaksi on määritetty (x{0}, y{1}, z{2})'.format(self.maaritykset["x"], self.maaritykset["y_loppu"], self.maaritykset["z"]))
        
        
    def siirtyma(self, x):
        self.maaritykset["x_siirtyma"] = x
        print("Kuvattavan viipaleen paksuus on {}".format(self.maaritykset["x_siirtyma"]))
        
    
#lisätäänkö tähän numpy array -sijaintitietojen palautukset pitkin matkaa?    
    """ Ennen tämän käyttöä tulee olla määritettynä aloistus- ja lopetuspiste sekä 
    kuvattavan viipaleen paksuus (tai käytetään oletusarvoja). 
    Metodin alussa kelkka on aloituspisteessä. Siirrytään kuvausmodessa lopetuspisteeseen, 
    palataan alkuun ja siirrytään määritetyn siirtymän verran oikealle, skannataan uudestaan 
    y:n suhteen lopetuspisteeseen... Pysähdytään kunnes on kuvattu parametrinä annettu
    määrä siirtymiä tai tultu rajakytkimelle"""
    def skannaa_viipaletta(self, viipaleiden_maara):
        y_liikuttava_matka = self.maaritykset['y_loppu'] - self.maaritykset['y_alku']
        for viipaleet in range(viipaleiden_maara):
            print("Skannataan...")
            self.moottorit.skannaa_askelta(y_liikuttava_matka) #liikutaan hitaasti y:n suhteen aloituspisteestä lopetuspisteeseen
            self.vaihda_suunta("y") #paluuta varten
            print("Takaisin aloistuskohtaan...")
            self.siirry_askelta(0, self.maaritykset["y_alku"], 0) #palataan aloituspisteeseen
            self.vaihda_suunta("y") #y valmiina uutta skannausta varten
            print("Siirrytään uuden viipaleen alkuun...")
            self.siirry_askelta(self.maaritykset['x_siirtyma'], 0, 0)
            sijaintitiedot = self.sijainti() #otetaan sijaintitaulukko nyt esimerkkinä silmukan lopputilanteesta
            print("{0}: {1}".format(viipaleet, sijaintitiedot)) #tämä muuallekin tähän metodirunkoon?
        
         
    """ Metodi kaikkien moottoreiden viimeisimmän sijaintitiedon palauttamista varten, 
    palauttaa Numpy arrayn."""
    def sijainti(self):      
        sijainti = self.moottorit.get_sijainti()
        return sijainti
        
    
    """Sarjaportin sulkeminen lopuksi."""
    def lopeta(self):
        self.moottorit.lopeta() 
        
        
    def ohjeet(self):
        print("\nVoit ohjata kelkkaa joko:\n siirry(x=int, y=int, z=int)\n vaihda_suunta(moottorin_nimi)\ntai määrittämällä alkupisteen, loppupisteen ja siirtymän leveyden:\n set_aloituskohta(x=int, y=int, z=int) --> sijainti laitetaan muistiin ja kelkka siirretään aloituskohtaan \nset_lopetuskohta(y=int) --> lopetuskohta laitetaan muistiin skannaamista varten\n skannaa() --> kelkkaa siirretään aloituskohdasta lopetuskohtaan tasaista vauhtia, minkä jälkeen palataan aloituskohtaan, siirrytään siirtymän verran oikealle ja skannataan uudestaan")
    
def main():
    #KÄYNNISTÄMISTOIMET:
    moottori_x = Moottori('x', 4, 3, 200, 2, 13)
    moottori_y = Moottori('y', 10, 8, 200, 5, 6)
    moottori_z = Moottori('z', 12, 11, 400, 7, 9)
    moottorit = Moottorit('COM6', moottori_x, moottori_y, moottori_z) # katso portti Arduinon kautta
    kuvaus1 = Kuvaus(moottorit)
    


    #KÄYTTÄJÄN TOIMIEN KOKEILUA:
    #kuvaus1.ohjeet()

   # LIIKUTTELUN TAPA1:
 #   kuvaus1.skannaa_askelta_nopeudella(200, 100) # nopeasti, vastap.
 #   kuvaus1.skannaa_askelta_nopeudella(200, 10000) # hitaasti, vastap.
#    kuvaus1.siirry_askelta(0, 400, 0) # yhden moottorin liikuttelu
#    kuvaus1.siirry_askelta(200, 300, 100) # kaikkien moottoreiden liikuttelu
#    kuvaus1.siirry_askelta(0, 0, 400)
#    kuvaus1.vaihda_suunta("z")
#    kuvaus1.siirry_askelta(0, 0, 400)
   # sijaintitiedot = kuvaus1.sijainti()
   #  print(sijaintitiedot)
#    kuvaus1.vaihda_suunta("x") 
#    kuvaus1.siirry_askelta(400, 0, 0)
 #   kuvaus1.vaihda_suunta("y") 
 #   kuvaus1.skannaa_askelta(400) #vastap, myötäp.
 #   sijaintitiedot = kuvaus1.sijainti()
 #   print(sijaintitiedot) #odotus: (0,0,0)

   # print(type(sijaintitiedot))


    #TAPA2:
    kuvaus1.aloituskohta(200, 400, 200) 
    kuvaus1.lopetuskohta(800)
    kuvaus1.siirtyma(10)
    kuvaus1.skannaa_viipaletta(5)

   
    kuvaus1.lopeta() #Toimii - tämän jälkeen ei voi liikutella
if __name__ == "__main__":
    main()
        
        