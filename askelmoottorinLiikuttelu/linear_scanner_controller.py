# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#!/usr/bin/env python3

"""
Created on Wed Jul  8 09:59:45 2020
The prototype of control software of linear scanner for moving hyperspectral 
camera. The scanner is Arduino-based and provides moving in three dimensions.
In the development work it has sought to take into account both users,
who mainly want to perform scanning of certain size of objects, as well as,
users who want to take advantage of the program code along with their own 
python scripts.
Hyperspektrikameran lineaarisiirtimen ohjainohjelmiston ensimmäinen versio. 
Skanneri on toteutettu Arduinolla ja se tarjoaa kolmeulotteiset 
liikuttelumahdollisuudet. Kehitystyössä on pyritty huomioimaan sekä käyttäjiä,
jotka haluavat lähinnä toteuttaa tietynkokoisen kohteen skannausta, että 
käyttäjiä, jotka haluavat hyödyntää ohjelmakoodia yhdessä omien 
python-skriptien kanssa. 
@author: Sanna-Mari Äyrämö
"""

import numpy as np # Numpy array
import pyfirmata # Arduinon käyttö
import time # Arduinon käyttö
import serial #sarjaportti
import pandas as pd # taulukko


class Moottori:
    """ 
    Motor class for single stepper motor of the scanner.
    The class takes care of the individual motor specs and other information 
    that constitutes its role in the scanner.
    Moottori-luokka lineaarisiirtimen yhteen askelmoottoriin liittyvien 
    tietojen hallinnointia varten. Luokka huolehtii yksittäisen moottorin 
    teknisten tietojen, arduinokytkentöjen ja moottorin liikutteluun liittyvien 
    rajakytkimien arduinokytkentöjä koskevien tietojen kokoamisesta ja 
    ylläpidosta.
    """
    
    def __init__(self, nimi, dir_pin, step_pin, askelta_kierroksella, 
                 rajakytkin_0, rajakytkin_1):
        """ 
        The constructor. The parameters: 
        nimi: the motor name ('x', 'y' or 'z'), 
        dir_pin: the number of the arduino pin, which is applied for setting 
        direction information,
        step_pin: the number of the arduino pin, which is applied for setting 
        stepping commands,
        askelta_kierroksella: the steps per revolution value, can be found from 
        the specs of the motor, 
        rajakytkin_0: the number of the pin Arduino uses for detecting the 
        limit switch in the 0-end,
        rajakytkin_1: the number of the pin Arduino uses for detecting the 
        limit switch in the opposite end,    
        Konstruktori. Parametrit: 
        nimi: moottorin nimi ('x', 'y' tai 'z'), 
        dir_pin: sen pinnin numero, jonka kautta arduinolle kerrotaan, 
        kumpaanko suuntaan moottoria liikutetaan 
        step_pin: sen pinnin numero, jonka kautta arduinolle annetaan käsky 
        liikuttaa moottoria,
        askelta_kierroksella: askelmoottorin per revolution -tieto,
        rajakytkin_0: sen pinnin numero, jonka kautta Arduino seuraa tämän 
        moottorin kulkuväylän 0-päädyn rajakytkintä (vrt.x/y/z-koordinaatisto),
        rajakytkin_1: sen pinnin numero, jonka kautta Arduino seuraa tämän 
        moottorin kulkuväylän vastakkaisen päädyn rajakytkintä, 
        """
        self.nimi = nimi
        self.dir_pin = dir_pin
        self.dir_pin_tila = 0 #False, vastapäivään / counterclockwise
        self.step_pin = step_pin
        self.askelta_kierroksella = askelta_kierroksella
        self.sijainti = 0
        self.rajakytkin_0 = rajakytkin_0
        self.rajakytkin_0_tila = None
        self.rajakytkin_1 = rajakytkin_1
        self.rajakytkin_1_tila = None
        self.voi_liikkua = True
        self.palaamassa = False  

    def set_suunta(self, suunta):
        """ 
        A setter for setting the direction of motor movement: False (0, 
        counterclockwise) or True (1, clockwise).
        Moottorin liikutussuunnan asettaminen: False (0, vastapään) tai True 
        (1, myötäpäivään).
        """
        self.dir_pin_tila = suunta

    def set_rajakytkin_0_tila(self, tila):
        """ 
        Setter for changing the value of the 0-end limit switch.
        Setteri 0-rajakytkimen tilan muuttamiseksi.
        """
        self.rajakytkin_0_tila = tila
    
    def set_rajakytkin_1_tila(self, tila):
        """ 
        Setter for changing the value of the 1-end limit switch.
        Setteri 1-rajakytkimen tilan muuttamiseksi
        """
        self.rajakytkin_1_tila = tila

    def esta_liike(self):
        """ 
        A setter that denies the motor the permission to move. Used by the 
        Motors-object in movement methods in connection with limit switches.
        Setteri joka kieltää mottorilta luvan liikkua. Käytetään Moottorit-
        olion liikuttelumetodeissa rajakytkimien yhteydessä.
        """
        self.voi_liikkua = False

    def salli_liike(self):
        """ 
        A setter that allows the motor the permission to move. Used by the 
        motor-object in movement methods in connection with limit switches.
        Setteri joka sallii mottorin liikkua. Käytetään Moottorit-oliossa
        liikuttelumetodeissa rajakytkimien yhteydessä.
        """
        self.voi_liikkua = True

    def lahtee(self):
        """ 
        A setter related to the operations of the step counter. Applied to get 
        to know that the next calculation task is a plus calculation.
        Askellaskurin toimintaan liittyvä setteri, jonka avulla tiedetään, että 
        viimeisin askel tulee lisätä kokonaismäärään.
        """
        self.palaamassa = False
            
    def palaa(self):
        """ 
        A setter related to the operations of the step counter. Applied to get 
        to know that the next calculation task is a minus calculation.
        Askellaskurin toimintaan liittyvä setteri, jonka avulla tiedetään, että 
        viimeisin askel tulee vähentää kokonaismäärästä.
        """
        self.palaamassa = True
        
    def print_kytkennat(self):
        """
        Ohjelman jatkokehitystä varten:
        Prints in the console information about the connections of the motor.
        Printataan konsoliin tieto siitä, miten kyseisen moottorin
        kytkennät on asetettu.
        """
        print("{0}: dir_pin: {1}, step_pin: {2}, askelta kierroksella: {3},"+ \
              " rajakytkin_0 pinnissä: {4}, rajakytkin_1 pinnissä: {5}".format(
                      self.nimi, 
                      self.dir_pin, 
                      self.step_pin, 
                      self.askelta_kierroksella, 
                      self.rajakytkin_0, 
                      self.rajakytkin_1
                      ))

    def nollaa_sijainti(self):
        """ 
        Sets the value of the step counter in zero.
        Metodi joka nollaa moottorin ohjaaman kelkan sijaintia laskevan 
        askelmittarin
        """
        self.sijainti = 0

    def kasvata_sijaintia(self):
        """ 
        Increases the value of the step counter by one.
        Metodi jolla kasvatetaan askelmittarin lukemaa yhdellä.
        """
        self.sijainti += 1

    def vahenna_sijaintia(self):
        """ 
        Decreases the value of the step counter by one.
        Metodi jolla vähennetään askelmittarin lukemaa yhdellä. Käytetään 
        akselin 1-päädystä palatessa.
        """
        self.sijainti -= 1
    
    def get_sijainti(self):
        """ 
        Method that returns the value of the step counter, that is, the 
        location relative to the axis for which the motor is responsible. Note: 
        real location is unknown. The value indicates the number of the steps 
        commanded to be taken. Metodi joka palauttaa askellaskurin 
        sijaintilukeman kyseisen moottorin vastaaman akselin suhteen. Huom! 
        Todellista sijaintia ei tiedetä. Laskelma kertoo 0-rajakytkimeltä 
        käskytettyjen askelten määrän miinustaen lukemasta 1-päädyn 
        rajakytkimellä käynnin jälkeen otetut askeleet.
        """
        return self.sijainti       
 
       
class Moottorit:
    """ 
    A class that brings together the three stepper motors of a scanner hardware, 
    Arduino card and the selected usb port. The class takes care of the 
    movement of the motors, monitoring of the limit switches and the step 
    counters.
    Luokka, joka kokoaa skannerilaitteiston kolmesta moottorista, Arduino-
    kortista ja usb-portista koostuvan laitteiston. Luokka huolehtii moottorien 
    liikuttelusta, rajakytkimien seurannasta ja askellaskureiden toiminnasta.
    """ 
        
    def __init__(self, portti, moottori_x, moottori_y, moottori_z):
        """ 
        The constructor. The parameters: 
        portti: the name of the USB-port. The name can be determined, for 
        example, via the Device Manager or the Arduino IDE.
        The rest: the motor-objects that 
        take care of moving the carriage on the x-, y-, and z-axes.
        Konstruktori. Parametreinä PC:ssä käytetty usb-portti ja x-, y- 
        ja z-akseleilla kelkan liikuttelusta vastaavat moottorit. Portin nimi 
        selviää esim. Device Managerin tai Arduino IDE:n kautta.
        """
        self.portti = portti
        self.kortti = pyfirmata.ArduinoMega(portti)
        self.moottori_x = moottori_x
        self.moottori_y = moottori_y
        self.moottori_z = moottori_z
        self.viive = 2.6 * 1e-6 # pulse interval min. 2.5 µs
        self.viive_y = 4 * 1e-6 # y-moottori hyötyy hieman pitemmästä viiveestä
                            # the y-motor benefits from a slightly longer delay
        self.iteraattori = pyfirmata.util.Iterator(self.kortti)
        self.iteraattori.start()
        self.kortti.digital[
                self.moottori_x.rajakytkin_0
                ].mode = pyfirmata.INPUT
        self.kortti.digital[
                self.moottori_x.rajakytkin_1
                ].mode = pyfirmata.INPUT
        self.kortti.digital[
                self.moottori_y.rajakytkin_0
                ].mode = pyfirmata.INPUT
        self.kortti.digital[
                self.moottori_y.rajakytkin_1
                ].mode = pyfirmata.INPUT
        self.kortti.digital[
                self.moottori_z.rajakytkin_0
                ].mode = pyfirmata.INPUT
        self.kortti.digital[
                self.moottori_z.rajakytkin_1
                ].mode = pyfirmata.INPUT

    def tarkista_kytkimet(self, moottorin_nimi):
        """ 
        Checks whether the motor named in the parameter has arrived
        at either of its limit switches. When arriving at the switch,
        the direction of movement of the motor will be set reversed. Besides, 
        the motor is not allowed to take any remaining steps in the opposite 
        direction.
        Tarkistaa parametrissä nimetyn moottorin osalta, onko tultu
        jommalle kummalle sen rajakytkimistä. Jos tullaan kytkimelle, asetetaan
        moottorin liikkumissuunta valmiiksi päinvastaiseksi, eikä anneta
        moottorin liikkua mahdollisesti jäljelle jäänyttä askelmäärää
        vastakkaiseen suuntaan.
        """
        nonelaskuri = 0
        if moottorin_nimi == 'x':
            moottori = self.moottori_x
            raja_0 = moottori.rajakytkin_0
            raja_1 = moottori.rajakytkin_1
            nimi = moottori.nimi
        elif moottorin_nimi == 'y':
            moottori = self.moottori_y
            raja_0 = moottori.rajakytkin_0
            raja_1 = moottori.rajakytkin_1
            nimi = moottori.nimi
        elif moottorin_nimi == 'z':
            moottori = self.moottori_z
            raja_0 = moottori.rajakytkin_0
            raja_1 = moottori.rajakytkin_1
            nimi = moottori.nimi
        else:
            print("Tarkista tarkista_kytkimet()-kutsu!")
        kytkimen_tila_0 = self.kortti.digital[raja_0].read()
        kytkimen_tila_1 = self.kortti.digital[raja_1].read()
        while kytkimen_tila_0 is None or kytkimen_tila_1 is None:
            try:    
                print("odotetaan yhteyttä {0}:n kytkimiin".format(nimi))
                time.sleep(0.1)
                kytkimen_tila_0 = self.kortti.digital[raja_0].read()
                nonelaskuri += 1
                if nonelaskuri == 100:
                    print("Rajakytkimen pinnin lukeminen epäonnistui." + \
                          "Käynnistä ohjain uudelleen.")
                    self.moottori.esta_liike()
                    return
            except serial.SerialTimeoutException:
                print("USB-yhteys katkesi")
        else:
            moottori.set_rajakytkin_0_tila(kytkimen_tila_0) 
            moottori.set_rajakytkin_1_tila(kytkimen_tila_1)
            if moottori.rajakytkin_0_tila == 1:
                moottori.nollaa_sijainti()
                self.vaihda_suunta(moottorin_nimi)
                moottori.esta_liike()
                print("{0}-moottori tuli 0-kytkimelle".format(nimi))
                self.irrota_kytkimelta(moottori)
            elif moottori.rajakytkin_1_tila == 1:
                self.vaihda_suunta(moottorin_nimi)
                moottori.esta_liike()
                print("{0}-moottori tuli 1-kytkimelle".format(nimi))
                self.irrota_kytkimelta(moottori)
            elif moottori.rajakytkin_0_tila == 0 and moottori.rajakytkin_1_tila == 0:
                return
            else:
                print("Kytkinten lukemisessa ongelmia")

    def set_suunta(self, moottorin_nimi, myota_vai_vasta):
        """ 
        Sets the direction for moving selected motor.
        The parameters: 
        moottorin_nimi: the name of the motor,
        myota_vai_vasta = 1 or 0,
        where 0 = counterclockwise and 1 = clockwise.
        Metodi jolla asetetaan suunta halutun moottorin liikuttamista varten. 
        Parametereinä moottorin nimi ja 1 tai 0, 
        missä 0= vastapäivään, 1= myötäpäivään.
        """
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
                                                # LOW/0 = counterclockwise
            moottori.set_suunta(0)
            if moottori.palaamassa == True: 
                moottori.lahtee()
            else: moottori.palaa() 
        elif myota_vai_vasta == 1:
            self.kortti.digital[dir_pin].write(1)
            moottori.set_suunta(1)
            if moottori.palaamassa == True: 
                moottori.lahtee() 
            else: moottori.palaa() 
        else: print("Suunnan suunta-arvoksi tulee antaa 0 (vastapäivään)" + \
                    " tai 1 (myötäpäivään)")

    def vaihda_suunta(self, moottorin_nimi):
        """
        Reversing the current direction of movement of the motor named in the 
        parameter. Parameter: name of the motor
        Metodi jolla vaihdetaan parametrina annetun moottorin nykyinen 
        liikkumasuunta päinvastaiseksi.
        """
        if moottorin_nimi == 'x':
            moottori = self.moottori_x
            dir_pin = self.moottori_x.dir_pin
        elif moottorin_nimi == 'y':
            moottori = self.moottori_y
            dir_pin = self.moottori_y.dir_pin
        elif moottorin_nimi == 'z':
            moottori = self.moottori_z
            dir_pin = self.moottori_z.dir_pin
        else: print("Suuntaa vaihdettaessa moottorin nimi joko x, y tai z")
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
            print("vaihda_suunta()-metodissa dir_pinnin tilaksi" +\
                  "asetettiin: ", dir_pin) # testing
            
    def liiku_askelta(self, moottorin_nimi, montako_askelta):        
        """ 
        Moves the named motor a set number of steps.
        Metodi jolla liikutetaan valittua moottoria asetettu askelmäärää. 
        Before each step, the limit switches are checked.
        Tarkistaa ennen jokaista askelta, ollaanko tultu jommalle kummalle
        rajakytkimelle.
        """
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
        moottori.salli_liike()

    def skannaa_askelta_nopeudella(self, askeleet, nopeus):
        """
        Moves the y-motor at a speed set by the user.
        Parameters: 
        askeleet: number of the steps, 
        nopeus: delay value. The lower the number, the faster the speed.
        However, atleast 4 (driver's minimum is 2.5, but there may occur
        loss of steps with the y-motor at speeds below 4.)
        y-moottorin liikutteluun käyttäjän haluamalla nopeudella.
        Nopeus-parametri: mitä pienempi luku, sitä nopeampi vauhti. 
        Kuitenkin vähintään 4 (vaikka ajureiden minimi 2.5, y-moottorin 
        esiintyy sijaintitiedoissa vaihtelua alle 4:n nopeudella.)
        """
        if nopeus < 4: 
            print("Skannausfunktiolle annettavan nopeuskertoimen oltava min.4")
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
        moottori.salli_liike()

    def irrota_kytkimelta(self, moottori):
        """
        Should be called _only_ after a motor has arrived at a limit switch. 
        Moves the parameter motor 540 steps without checking the switches. 
        Käyttö ainoastaan funktiossa tarkista_kytkimet() rajakytkimelle 
        tulon yhteydessä, parametrinä annetun moottorin liikuttamiseen
        kytkimeltä 540 askelta poispäin (huom. suunta asetettu jo ennen tämän
        kutsua).
        """
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
            
    def laskuri(self, moottori):
        """
        Commands the step counter of given motor as appropriate to the 
        situation. Parameter: the motor.
        Käskytetään annetun moottorin laskuria tilanteseen sopivalla tavalla
        """
        if moottori.palaamassa == False:
            moottori.kasvata_sijaintia()
        else:
            moottori.vahenna_sijaintia()
            
        """
        A method for retrieving the latest location information for all the
        motors, returns a Numpy Array.
        Metodi kaikkien moottoreiden viimeisimmän sijaintitiedon palauttamista 
        varten, palauttaa Numpy arrayn.
        """
    def get_sijainti(self):
        sijainti = np.array([
                self.moottori_x.sijainti, 
                self.moottori_y.sijainti, 
                self.moottori_z.sijainti
                ])        
        return sijainti

    #POIS jos ei käyttöä!
    def nollaa_sijainnit(self):
        """
        Sets the location information of the three motors (0, 0, 0). Used only 
        in connection with start-up operations.
        Nollaa moottoreiden sijainniksi (0, 0, 0). Käytetään vain 
        osana ohjain-olion suorittamia aloitustoimia, kun jokainen on moottori 
        on käynyt 0-kytkimellä ja irrottautunut siitä.
        """
        self.moottori_x.nollaa_sijainti()
        self.moottori_y.nollaa_sijainti()
        self.moottori_z.nollaa_sijainti()
        
    def print_portti(self):
        """
        For further development of the program:
        Prints the name of the port on the console.
        Ohjelman jatkokehitystä varten:
        Printtaa konsoliin käytetyn portin nimen. 
        """
        print("Käytössä oleva portti:", self.portti)    
    
    def print_moottorien_kytkennat(self):
        """
        A method that prints the wiring information and the step by revolution 
        specs of the three motors.
        Metodi joka printtaa konsoliin kolmen mottorin kytkentätiedot sekä
        moottoriominaisuuksista steps per revolution -tiedon
        """
        print("Moottoreiden määritykset:")
        self.moottori_x.print_kytkennat()
        self.moottori_y.print_kytkennat()
        self.moottori_z.print_kytkennat()

    def lopeta(self):
        """
        Closes the connection to Arduino. 
        Suljetaan yhteys Arduinoon hallitusti.
        """
        self.kortti.exit()
   
     
class Ohjain:
    """
    A class for configuring and running a linear scan. The class uses
    one motors object and provides the user the opportunity to determine the 
    motion sequences of linear scanning. Includes functions needed by the user.
    Luokka lineaariskannauksen määrittämistä ja ajamista varten. Luokka käyttää 
    yhtä moottorit-oliota ja huolehtii lineaarikuvauksen liikesarjoja varten 
    määritettävistä tiedoista. Sisältää kaikki ohjainohjelmiston 
    (ei-tietoteknisesti orientoituneelle) käyttäjälle tarjoamat toiminnot.
    """
    
    def __init__(self, moottorit):
        """
        The constructor.
        Konstruktori.
        """
        self.moottorit = moottorit
        self.moottorit.set_suunta('x', 0) # 0
        self.moottorit.set_suunta('y', 1) # 1 
        self.moottorit.set_suunta('z',0) # 0 - suunnat joilla skannerin kelkka  
                                         # siiretään sijaintiin (0,0,0)
        self.maaritykset = {
            "x" : 0, 
            "y_alku" : 0, 
            "z" : 0,
            "y_loppu" : 51500,  
            "x_siirtyma" : 500 
        }
        self.alkuun()
        print("\nJärjestelmä on valmiina." + \
              "Ohjeita liikutteluun:\nohjain.ohjeet()\nmitat()\n")

    def alkuun(self):
        """
        A method used only in the constructor of Ohjain. Makes sure 
        that the carriage is first moved to the position, which is determined 
        to be (0, 0, 0). Sets the value of the stepper counter of each motor at
        0 and prints the location information on console.
        Metodi jota käytetään vain ohjaimen konstruktorissa. Varmistaa, että 
        kelkkaa lähdetään liikuttelemaan 0-sijainnista (välttämätöntä 
        sijaintitiedon määrittämiseksi). Tulostaa moottorien sijaintitiedon 
        näyttöön.
        """
        print("Alustus:")
        self.moottorit.liiku_askelta('x', 90000)
        self.moottorit.skannaa_askelta_nopeudella(70000, 4)
        self.moottorit.liiku_askelta('z', 20000) 
        self.moottorit.nollaa_sijainnit() # Määrätään käytön suhteen että 
                                        # todellinen sijainti (540, 540, 540) 
                                        # on skannerin käyttäjälle (0, 0, 0)
        sijainti = self.sijainti()
        print(sijainti)

    def aloituskohta(self, x, y, z):    
        """
        Sets a customed starting point value for scanning operation.
        The carriage is moved to the starting point.
        Parameters: the location value in steps regarding x, y, z axes.
        Prints the location information stored in the console.
        Käyttäjä määrittää skannausoperaatiolle muun aloituspisteen
        kuin (0,0,0). Pisteen tiedot laitetaan muistiin ja kelkka siirretään 
        aloituspisteeseen. Tulostaa konsoliin muistiin merkityt sijaintitiedot.
        """
        self.maaritykset["x"] = x
        self.maaritykset["y_alku"] = y
        self.maaritykset["z"] = z
        print('Kuvauksen aloituskohdaksi määritettiin ({0}, {1}, {2})'.format(
                self.maaritykset["x"], 
                self.maaritykset["y_alku"], 
                self.maaritykset["z"]
                ))
        self.siirry_askelta(x, y, z)

    def siirry_askelta(self, x, y, z):
        """
        Runs the motors the number of steps given in the parameters. 
        Parameters: 
        x: the number of steps that the x-motor is moved,
        y: the number of steps that the y-motor is moved,
        z: the number of steps that the z-motor is moved.
        Liikutetaan nimettyä moottoria haluttu askelmäärä. Parametreinä x-, 
        y- ja z-moottorin ottama askelmäärä.
        """
        self.moottorit.liiku_askelta('x', x)
        self.moottorit.liiku_askelta('y', y)
        self.moottorit.liiku_askelta('z', z)        

    def skannaa_askelta_nopeudella(self, askeleet, nopeus):
        """ 
        Scans in the y-line at a given speed. The parameters:
        askeleet: how many steps will be taken
        nopeus: the speed parameter in µs, i.e. the duration of the delay 
        between the LOW-HIGH pulses given to the motor.
        Skannataan y-suuntaisesti annetulla nopeudella. 
        Parametrit: askeleet: y-moottorin liikuttelun askelmäärä, 
        nopeus: millä nopeudella liikutellaan, tarkoittaa moottorin 
        liikuttelussa annettujen impulssien välissä käytetyn viiveen kestoa 
        mikrosekunteissa ilmaistuna.
        """
        self.moottorit.skannaa_askelta_nopeudella(askeleet, nopeus) 
        print("\n")
    
    def vaihda_suunta(self, moottorin_nimi):
        """
        Changes the direction of movement of named motor
        to the contrary. The parameter: 
        moottorin_nimi: the name of the motor.
        Vaihdetaan halutun moottorin liikkumissuunnta 
        päinvastaiseksi. Parametrinä moottorin nimi.
        """
        self.moottorit.vaihda_suunta(moottorin_nimi)        

    def lopetuskohta(self, y):    
        """
        Sets the end point for scanning. The parameter:
        y: the location point (also the number of steps
        from y-zero to the end point).
        Käyttäjä määrittää lopetuskohdan skannausta varten. Kohtaa 
        tarkoittava luku tarkoittaa sijaintipistettä (= askelmäärä 
        nollasta lopetuskohtaan).
        """
        self.maaritykset["y_loppu"] = y
        print('Kuvauksen ensimmäisen siivun lopetuskohdaksi määritettiin' + \
              ' ({0}, {1}, {2})'.format(
                  self.maaritykset["x"], 
                  self.maaritykset["y_loppu"], 
                  self.maaritykset["z"]
                  )) 
        
    def siirtyma(self, x):
        """
        Sets the number of steps taken during the transition between scanning
        sequences. The parameter:
        x: steps to be taken by x-motor
        Käyttäjä määrittää kuvattavan frame-sarjan välissä käytetyn siirtymän
        leveyden.
        """
        self.maaritykset["x_siirtyma"] = x
        print("Kuvattavan viipaleen paksuudeksi" + \
              "määriteltiin {0}".format(self.maaritykset["x_siirtyma"]))
        
    def skannaa_viipaletta_nopeudella(self, frame_nimi, viipaleiden_maara, nopeus):
        """
        Runs the desired number of scanning sequences at the speed determined 
        by the user. At the beginning of the method, the sled is at the 
        starting point. Next, runs y-motor in scan mode to the end point, 
        returns, and moves x-motor according to the transition (x_siirtyma), 
        rescans by y-motor to the end point... Returns scanning data in a 
        data frame (pandas).
        The parameters: 
        frame_nimi: a name that is saved in connection of the scanning data, 
        viipaleiden_maara:the number of scanning sequences that will be taken, 
        nopeus: the speed parameter in µs,
        Skannaa halutun määrän frame-sarjoja annetulla nopeudella. Metodin 
        alussa kelkka on aloituspisteessä. Siirrytään skannausmodessa 
        lopetuspisteeseen, palataan takaisin y:n suhteen ja siirrytään 
        määritetyn siirtymän verran oikealle, skannataan uudestaan 
        y:n suhteen lopetuspisteeseen... Palauttaa skannaustietoja data frame
        muodossa.
        """
        y_liikuttava_matka = self.maaritykset['y_loppu'] 
        - self.maaritykset['y_alku']
        siirtyma_laskuri = 0
        kuvaustiedot = { 
                'frame_nimi': [], 
                'alkusijainti': [], 
                'loppusijainti': [], 
                'aloitusaika': [], 
                'lopetusaika': [] 
                }
        for viipaleet in range(viipaleiden_maara):
            alkusijainti = self.sijainti() #NA siivun alkusijainnista
            aloitus = time.time()
            self.moottorit.skannaa_askelta_nopeudella(
                    y_liikuttava_matka, 
                    nopeus
                    )
            lopetus = time.time()
            loppusijainti = self.sijainti() #NA siivun loppusijainnista
            kuvaustiedot["frame_nimi"].append(frame_nimi)
            kuvaustiedot["alkusijainti"].append(alkusijainti)
            kuvaustiedot["loppusijainti"].append(loppusijainti)
            kuvaustiedot["aloitusaika"].append(aloitus)
            kuvaustiedot["lopetusaika"].append(lopetus)
            print("Tultiin {0}.:n framesarjan loppuun".format(
                    siirtyma_laskuri + 1
                    ))
            self.vaihda_suunta("y")
            self.siirry_askelta(0, y_liikuttava_matka, 0) 
            self.vaihda_suunta("y") #y valmiina uutta skannausta varten
            siirtyma_laskuri += 1
            if siirtyma_laskuri < viipaleiden_maara: 
                self.siirry_askelta(self.maaritykset['x_siirtyma'], 0, 0)
        kuvaustietojen_taulukko = pd.DataFrame(data=kuvaustiedot)
        return kuvaustietojen_taulukko
         
    def sijainti(self):      
        """
        Returns motors' location information in a Numpy array.
        Metodi kaikkien moottoreiden viimeisimmän sijaintitiedon palauttamista 
        varten. Palauttaa Numpy arrayn.
        """
        sijainti = self.moottorit.get_sijainti()
        return sijainti
    
    def lopeta(self):
        """
        Closes the connection to Arduino.
        Suljetaan yhteys Arduinoon lopuksi.
        """
        self.moottorit.lopeta() 
        
    def ohjeet(self):
        """
        Prints instructions on console (in Finnish).
        Ohjeita ohjaimen käyttöön.
        """
        print("\nVoit ohjata kelkkaa vapaasti (esim. alkumääritysten" + \
              " tekemiseksi) funktioilla:\n .skannaa_askelta_nopeudella" + \
              "(askeleet=int, nopeus=int)\n .siirry(x_askeleet=int, " + \
              "y_askeleet=int, z_askeleet=int)\n .vaihda_suunta(" + \
              "moottorin_nimi=string)\nSkannaamista varten määritä " + \
              "alkupiste, loppupiste ja siirtymän leveys askelina:\n ." + \
              "set_aloituskohta(x=int, y=int, z=int) \n --> sijainti" + \
              " laitetaan muistiin JA kelkka siirretään aloituskohtaan\n" + \
              " .set_lopetuskohta(y=int)\n --> lopetuskohta laitetaan " + \
              "muistiin ja käytetään skannatessa\n .skannaa_viipaletta_" + \
              "nopeudella(montako=int, nopeuskerroin=int)\n --> kelkkaa " + \
              "siirretään aloituskohdasta lopetuskohtaan tasaista " + \
              "vauhtia, minkä jälkeen palataan aloituskohtaan, siirrytään" + \
              " siirtymän verran oikealle ja skannataan uudestaan.")
    
    def mitat(self):
        """
        Examples of the step count needed by the motors to run some 
        predetermined distance. The step counts are determined according to 
        the weight of the hyperspectral camera at hand.
        Valmiiksi laskettuja esimerkkejä eri moottorien tarvitsemista askel-
        määristä eri matkoilla. Määritetty käytössä olevan hyperspektrikameran 
        paino huomioiden.
        """
        print("Esimerkkimittoja moottorien liikutteluun:\nX\nKoko väli: " + \
              "66cm = 65 532 askelta\npuoliväli:33cm = 32 766 askelta\n" + \
              "10cm = 9 929 askelta\n1cm = 993 askelta\nY\nKoko väli: " + \
              "52.3cm = 51705 askelta\nPuoliväli: 26.15 cm = 25853 " + \
              "askelta\n10cm = 9886 askelta\n1cm = 989 askelta\nZ\nKoko" + \
              " väli: 11cm = 14 514 askelta\nPuoliväli: 5,5cm = 7 257  " + \
              "askelta\n10cm = 13 195 askelta\n1cm = 1 319 askelta\n" + \
              "Kun määrität aloituskohtaa, lopetuskohtaa ja siivun " + \
              "paksuutta kohteen mittojen perusteella, muista vähentää " + \
              "kokonaismittojen edellyttämistä askelmääristä ensin 540 " + \
              "askelta! Sijainti 0,0,0 on todellisuudessa irrottauduttu " + \
              "540 askelta rajakytkimiltä.")
        
        
def main():
    #KÄYNNISTÄMISTOIMET:
    moottori_x = Moottori('x', 30, 32, 200, 5, 13) 
    moottori_y = Moottori('y', 26, 28, 200, 8, 6) 
    moottori_z = Moottori('z', 22, 24, 400, 7, 9) 
    moottorit = Moottorit('COM7', moottori_x, moottori_y, moottori_z) 
    ohjain = Ohjain(moottorit) # nämä oltava valmiina, kajotaan vain jos 
                                # kytkentöihin tulee muutoksia)

    #KÄYTTÄJÄN TOIMIEN KOKEILUA - - - - - - - - - - - - - - - - - - - - - -
#    ohjain.ohjeet()
#    ohjain.mitat()
    
        #LIIKUTTELUN TAPA1, ERIT. ALKUVALMISTELUIHIN:
 #   ohjain.skannaa_askelta_nopeudella(200, 100) # hidas
 #   ohjain.skannaa_askelta_nopeudella(2000, 4) # nopea
  #  ohjain.siirry_askelta(90000, 70000, 20000) # kelkka alustuksen jälkeen 
                                              # toiseen ääreen
 #   ohjain.siirry_askelta(0, 70000, 0) # yhden moottorin liikuttelut...
 #   ohjain.siirry_askelta(20000, 0, 0) 
 #   ohjain.siirry_askelta(0, 0, 400)
#    ohjain.vaihda_suunta("z")
#    ohjain.siirry_askelta(0, 0, 400)
 #   sijaintitiedot = ohjain.sijainti()
 #   print(sijaintitiedot)
#    ohjain.vaihda_suunta("x") 
#    ohjain.siirry_askelta(400, 0, 0)
 #   ohjain.vaihda_suunta("y") 
 #   ohjain.skannaa_askelta_nopeudella(400, 200) # hitaasti
 #   sijaintitiedot = ohjain.sijainti()
 #   print(sijaintitiedot)
   # print(type(sijaintitiedot)) # tulosteen tyypin tarkistus


        #TAPA2, SKANNAUS KUN TARVITTAVAT SIJAINNIT ASKELMÄÄRINÄ ON SELVITETTY:
    ohjain.aloituskohta(0, 0, 400) 
    ohjain.lopetuskohta(24177)
    ohjain.siirtyma(3656)
    kuvaustiedot = ohjain.skannaa_viipaletta_nopeudella("framet_1", 8, 4)
    print(kuvaustiedot)
   
    ohjain.lopeta()
if __name__ == "__main__":
    main()