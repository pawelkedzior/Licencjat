# coding=utf-8
from ROOT import TFile, gROOT, TTree
import pliki
import time

def tekstNaTabLog(tekst):
    liczba=[]
    for i in range(len(tekst)):
        liczba.append(tekst[i]=="1")
    return liczba

def wezNumerKanalu(zestawTab):
    numerKanalu=0
    for i in range(7):
        numerKanalu=numerKanalu*2+zestawTab[i+1]
    return numerKanalu

struktura="struct DaneZKanalow {"
for i in range(52):
    struktura=struktura+"Bool_t kanal"+str(i)+"op[32]; "
    struktura=struktura+"Bool_t kanal"+str(i)+"nar[32]; "
struktura=struktura+"};"

gROOT.ProcessLine(struktura)
from ROOT import DaneZKanalow

plikZrodlowyDanych=pliki.wybierzPlik(pliki.listaPlikow("txt","./"))
plikDanych=open(plikZrodlowyDanych)
odczyt=plikDanych.read()
zestawyTekst=odczyt.split("\n\n")
liczbaZestawow=len(zestawyTekst)-1
if plikZrodlowyDanych.find("[")>=0:
    data=plikZrodlowyDanych[plikZrodlowyDanych.index("["):plikZrodlowyDanych.index("]")+1]
else:
    data="["+time.strftime("%d.%m.%Y %H:%M:%S")+"]"
    
plik=TFile('dane '+data+'.root', 'RECREATE')

drzewo=TTree("Zestawy","Drzewo z zestawami.")

kanalyD=DaneZKanalow()
struktura="kanal0op[32]/B:kanal0nar[32]"
for i in range(51):
    struktura=struktura+":kanal"+str(i+1)+"op[32]"
    struktura=struktura+":kanal"+str(i+1)+"nar[32]"
galaz=drzewo.Branch("Zestaw",kanalyD,struktura)
galaz.SetBasketSize(240)

for i in range(liczbaZestawow):
    zestaw=zestawyTekst[i]
    kanaly=zestaw.split("\n")
    for j in range(len(kanaly)):
        zesTablica=tekstNaTabLog(kanaly[j])
        kanal=getattr(kanalyD,"kanal"+str(wezNumerKanalu(zesTablica))+("nar" if zesTablica else "op"))
        for k in range(32):
            kanal[k]=zesTablica[k]
    drzewo.Fill()

plik.Write()
plik.Close()

plikDanych.close()