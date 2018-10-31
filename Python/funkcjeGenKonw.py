# coding=utf-8
from ROOT import TFile, gROOT, TTree, TRandom3
from ROOT.Math import *
import time

def stworzDate():
    return time.strftime("%d.%m.%Y %H:%M:%S")
    
def odczytajLubStworzDate(nazwaPliku):
    if nazwaPliku.find("[")>=0:
        data=nazwaPliku[nazwaPliku.index("["):nazwaPliku.index("]")+1]
    else:
        data="["+stworzDate()+"]"
    return data

def stworzStrukturePomiaru(ileKanalow):
    struktura="struct DaneZKanalow {"
    for i in range(ileKanalow):
        struktura=struktura+"Bool_t kanal"+str(i)+"op[32]; "
        struktura=struktura+"Bool_t kanal"+str(i)+"nar[32]; "
    struktura=struktura+"};"
    gROOT.ProcessLine(struktura)

#tworzenie łańcucha tekstowego zawierającego format danych
def lancuchFormatuDanych(ileKanalow):
    lancuch="kanal0op[32]/B:kanal0nar[32]"
    for i in range(ileKanalow-1):
        lancuch=lancuch+":kanal"+str(i+1)+"op[32]"
        lancuch=lancuch+":kanal"+str(i+1)+"nar[32]"
    return lancuch

def wezNumerKanalu(zestawTab):
    numerKanalu=0
    for i in range(7):
        numerKanalu=numerKanalu*2+zestawTab[i+1]
    return numerKanalu

def tekstNaTabLog(tekst):
    liczba=[]
    for i in range(len(tekst)):
        liczba.append(tekst[i]=="1")
    return liczba

def konwertujNaBity(wartosc,ileBitow):
    wynik=[bool(0) for i in range(ileBitow)]
    i=0
    while(wartosc!=0):
        wynik[ileBitow-1-i]=bool(wartosc%2)
        wartosc=wartosc/2
        i=i+1
    return wynik



#wykorzystywane przez konwerter
def konwertujIZapiszDane(pojemnikDoZapisu, zmiennaZapisu, liczbaPomiarow, zestawDanych):
    for i in range(liczbaPomiarow):
        pomiar=zestawDanych[i]
        kanaly=pomiar.split("\n")
        for j in range(len(kanaly)):
            kanalTab=tekstNaTabLog(kanaly[j])
            kanal=getattr(zmiennaZapisu,"kanal"+str(wezNumerKanalu(kanalTab))+("nar" if kanalTab[0] else "op"))
            for k in range(32):
                kanal[k]=kanalTab[k]
        pojemnikDoZapisu.Fill()



#wykorzystywane przez generator
def zapiszDoKanalu(numer,zbocze,wygenerZestaw,pojemnikKanalow):
    daneKanalowe=wygenerZestaw.daneZKanalu(numer,[zbocze])
    kanal=getattr(pojemnikKanalow,"kanal"+str(numer)+("nar" if zbocze==1 else "op"))
    for k in range(32):
        kanal[k]=daneKanalowe[k]
            
def stworzZestaw(pojemnikZapisu,pojemnikDanych,liczbaDanych, liczbaKanalow):
    gener=TRandom3(0)
    for i in range(liczbaDanych):
        zestaw=ZestawDanych(liczbaKanalow)
        zestaw.wypelnijKanaly(gener)
        zapiszDoKanalu
        for j in range(liczbaKanalow):
            zapiszDoKanalu(j, 1, zestaw, pojemnikDanych)
            zapiszDoKanalu(j, 0, zestaw, pojemnikDanych)
        pojemnikZapisu.Fill()

class ZestawDanych():
    kanalyNar=[[1]]
    kanalyOp=[[0]]
    def __init__(self,liczbaKanalow):
        self.kanalyNar=[[1] for i in range(liczbaKanalow)]
        self.kanalyOp=[[0] for i in range(liczbaKanalow)]
    def daneZKanalu(self, numer, zbocze):
        return (self.kanalyNar[numer] if zbocze[0]==bool(1) else self.kanalyOp[numer])
    def wprowadzDoKanalu(self, numer, dane):
        if dane[0]==1:
            self.kanalyNar[numer]=dane
        else:
            self.kanalyOp[numer]=dane
    def generujLiczbe(self, generator, mnoznik):
        generator.SetSeed(generator.GetSeed()+48*mnoznik)
        liczba=generator.Gaus(60,10)/1;
        liczba=int(liczba)
        return liczba
    def porownajWygenerowane(self,liczba1,liczba2):
        if liczba2>liczba1:
            return [liczba1]+[liczba2]
        else:
            return [liczba2]+[liczba1]
    def stworzDane(self, zbocze, numerKanalu, czas):
        czasBity=konwertujNaBity(czas,7)
        rozluznienie=konwertujNaBity(0,17)
        numerBity=konwertujNaBity(numerKanalu,7)
        zbocze=zbocze+numerBity
        zbocze=zbocze+rozluznienie
        zbocze=zbocze+czasBity
        self.wprowadzDoKanalu(numerKanalu, zbocze)
        return zbocze
    def wypelnijKanaly(self, generator):
        for i in range(len(self.kanalyNar)):
            liczba=self.generujLiczbe(generator, i)
            liczba2=self.generujLiczbe(generator, i)
            liczby=self.porownajWygenerowane(liczba,liczba2)
            self.stworzDane([bool(0)],i,liczby[1])
            self.stworzDane([bool(1)],i,liczby[0])
