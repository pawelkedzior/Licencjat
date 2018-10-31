# coding=utf-8
from ROOT import TFile, TH1I, TCanvas, TBrowser
import time, os
import pliki

def wypiszPomiar(kanal):
    lancuch="["
    for i in range(31):
        lancuch=lancuch+str(kanal[i])+", "
    lancuch=lancuch+str(kanal[31])+"]"
    return lancuch
    
def bityNaInt(tablica, liczbaBitow):
    tablica.reverse()
    iloczyn=1
    liczba=0
    for i in range(liczbaBitow):
        liczba=liczba+(iloczyn*(1 if tablica[i] else 0))
        iloczyn=iloczyn*2
    return liczba

def rozlozPomiarNaSkladowe(pomiar):
    zbocze=pomiar[0]
    numerKanalu=0
    for i in range(7):
        numerKanalu=numerKanalu*2+pomiar[i+1]
    rozluznienie=0
    for i in range(8):
        rozluznienie=rozluznienie*2+pomiar[i+8]
    zmierzonyCzas=0
    for i in range(16):
        zmierzonyCzas=zmierzonyCzas*2+pomiar[i+16]
    zwrot=[]
    zwrot.append(zbocze)
    zwrot.append(numerKanalu)
    zwrot.append(rozluznienie)
    zwrot.append(zmierzonyCzas)
    return zwrot

nazwaPliku=pliki.wybierzPlik(pliki.listaPlikow("root","./"))
plik=TFile(nazwaPliku)
drzewo=plik.Get("Zestawy")
liczbaDanych=drzewo.GetEntries()
czas=nazwaPliku[nazwaPliku.index("["):nazwaPliku.index("]")+1]

dane=[]
for i in xrange(liczbaDanych):
    drzewo.LoadTree(i)
    drzewo.GetEntry(i)
    galaz=drzewo.GetBranch("Zestaw")
    galaz.GetEntry(i)
    dodajDane=[]
    for j in xrange(52):
        kanal=[]
        for k in range(32):
            kanal.append(int(galaz.GetLeaf("kanal"+str(j)).GetValue(k)))
        dodajDane.append(rozlozPomiarNaSkladowe(kanal))
    dane=dane+[dodajDane]

plik.Close()

plik=TFile("histogramy "+czas+".root","recreate")

wykresy=[]
for i in range(51):
    wykresy=wykresy+[TH1I(("Wykres "+str(i+1)),("Roznica miedzy kanalem "+str(i)+" a "+str(i+1)),131071,-65535,65535)]
    wykresy[i].SetDirectory(plik)
    
poleWykr=TCanvas("Rozkład","Rozklad roznic pomiarowych miedzy kanalami",1280,720)

sigmy=[]
#czas=time.strftime("%d.%m.%Y %H:%M:%S")
os.mkdir("./Wykresy "+czas)
for j in range(51):
    for i in xrange(liczbaDanych):
        chwilowa=dane[i][j][3]-dane[i][j+1][3]
        wykresy[j].AddBinContent(chwilowa+65535)
    wykresy[j].Fit("gaus","Q","",-65535,65535)
    sigmy.append(wykresy[j].GetFunction("gaus").GetParameter(2))
    wykresy[j].SetAxisRange(wykresy[j].FindFirstBinAbove()-65536, wykresy[j].FindLastBinAbove()-65536)
    wykresy[j].Write()
    poleWykr.Update()
    poleWykr.Print("Wykresy "+czas+"/Wykres "+str(j+1)+".png")
    time.sleep(0.1)

poleWykresu=TCanvas("Odchylenia","Odchylenia standardowe",1280,720)

wykresKoncowy=TH1I("Odchylenia standardowe","Wykres odchylen standardowych",51,0,50)
for i in range(51):
    wykresKoncowy.AddBinContent(i+1, sigmy[i])
    wykresKoncowy.GetXaxis().SetBinLabel(i+1,str(i)+"-"+str(i+1))
wykresKoncowy.SetTitle("Odchylenia standardowe")
wykresKoncowy.Draw()
time.sleep(0.1)
wykresKoncowy.SetDirectory(plik)
wykresKoncowy.Write()
poleWykresu.Print("Wykresy "+czas+"/Odchylenia.png")

time.sleep(180)

plik.Close()
