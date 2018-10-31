# coding=utf-8
from ROOT import TFile, TTree
import funkcjeGenKonw

liczbaKanalow=52

funkcjeGenKonw.stworzStrukturePomiaru(liczbaKanalow)
from ROOT import DaneZKanalow

czas=funkcjeGenKonw.stworzDate()
plik=TFile('daneGener ['+czas+'].root', 'RECREATE')

drzewo=TTree("Zestawy","Drzewo z wygenerowanymi zestawami.")
kanaly=DaneZKanalow()
struktura=funkcjeGenKonw.lancuchFormatuDanych(liczbaKanalow)
galaz=drzewo.Branch("Zestaw",kanaly,struktura)
galaz.SetBasketSize(240)
funkcjeGenKonw.stworzZestaw(drzewo, kanaly, 1000, liczbaKanalow)

plik.Write()
plik.Close()
