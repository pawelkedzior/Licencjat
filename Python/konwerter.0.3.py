# coding=utf-8
from ROOT import TFile, TTree
import pliki
import funkcjeGenKonw
    
liczbaKanalow=52    

#tworzenie i import struktury, która będzie wykorzystywana w drzewie
funkcjeGenKonw.stworzStrukturePomiaru(liczbaKanalow)
from ROOT import DaneZKanalow

#odczyt danych z pliku txt
sciezkaPlikuZrodlowego=pliki.wybierzPlik(pliki.listaPlikow("txt","./"))
plikDanych=open(sciezkaPlikuZrodlowego)
odczyt=plikDanych.read()
zestawyTekst=odczyt.split("\n\n")
liczbaZestawow=len(zestawyTekst)-1
data=funkcjeGenKonw.odczytajLubStworzDate(sciezkaPlikuZrodlowego)    

plik=TFile('dane '+data+'.root', 'RECREATE')
drzewo=TTree("Zestawy","Drzewo z zestawami.")
kanalyD=DaneZKanalow()
struktura=funkcjeGenKonw.lancuchFormatuDanych(liczbaKanalow)
galaz=drzewo.Branch("Zestaw",kanalyD,struktura)
galaz.SetBasketSize(240)

#konwersja odczytu pomiaru z konkretnych kanałów
funkcjeGenKonw.konwertujIZapiszDane(drzewo, kanalyD, liczbaZestawow, zestawyTekst)
    
#zapis przekonwertowanych danych w pliku root
plik.Write()
plik.Close()
plikDanych.close()