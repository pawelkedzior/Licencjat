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
    zgrubnyCzas=0
    for i in range(15):
        zgrubnyCzas=zgrubnyCzas*2+pomiar[i+8]
    zmierzonyCzas=0
    for i in range(9):
        zmierzonyCzas=zmierzonyCzas*2+pomiar[i+23]
    zwrot=[]
    zwrot.append(zbocze)
    zwrot.append(numerKanalu)
    zwrot.append(zgrubnyCzas)
    zwrot.append(zmierzonyCzas)
    return zwrot



def odczytDanychZPliku(drzewo, liczbaDanych, ileKanalow):
    zwrot=[]
    for i in xrange(liczbaDanych):
        drzewo.LoadTree(i)
        drzewo.GetEntry(i)
        galaz=drzewo.GetBranch("Zestaw")
        galaz.GetEntry(i)
        dodajDane=[]
        for j in xrange(ileKanalow):
            #odczyt danych kanałowych (zbocza opadające)
            dodajDane.append(odczytDanychZKanalu(galaz, j , "op"))
            #odczyt danych kanałowych (zbocza narastające)
            dodajDane.append(odczytDanychZKanalu(galaz, j , "nar"))
        zwrot=zwrot+[dodajDane]
    return zwrot
    #format zwracanych danych:
    #dane(pomiar(kanałOp/Nar(zbocze,nrKanału,zgrubnyCzas,zmierzonyCzas)))
    #dane - tablica składająca się z tablic reprezentujących dany pomiar
    #pomiar - tablica zawierająca wyniki pomiaru przedstawiona za pomocą 104 tablic zawierających wyniki z danego kanału podzielonego na zb nar i opad
    #kanałOp/Nar - tablica składająca się z czterech elementów reprezentujących wynik pomiaru z danego kanału dla danego zbocza

def odczytDanychZKanalu(galaz, nrKanalu, zbocze):
    kanal=[]
    for k in range(32):
        kanal.append(int(galaz.GetLeaf("kanal"+str(nrKanalu)+zbocze).GetValue(k)))
    return rozlozPomiarNaSkladowe(kanal)



def stworzZmienneWykresowe(katalog, ileKanalow):
    zwrot=[]
    for i in range(ileKanalow-1):
        zwrot=stworzZmiennaWykresowa(katalog, i , 0, zwrot)
        zwrot=stworzZmiennaWykresowa(katalog, i , 1, zwrot)
    return zwrot

def stworzZmiennaWykresowa(katalog, ktora, jaka, pojemnik):
    nazwaKr=" op." if jaka==0 else " nar."
    nazwaDl="opadajace" if jaka==0 else "narastajace"
    pojemnik=pojemnik+[TH1I(("Wykres "+str(ktora+1)+nazwaKr),("Roznica miedzy kanalem "+str(ktora)+" a "+str(ktora+1)+" (zbocze "+nazwaDl+")"),1023,-511,511)]
    pojemnik[2*ktora+jaka].SetDirectory(katalog)
    return pojemnik



def malujWykresyRoznic(ileKanalow):
    poleWykr=TCanvas("Rozkład","Rozklad roznic pomiarowych miedzy kanalami",1280,720)
    zwrot=[]
    for j in range(ileKanalow-1):
        #wypełnianie wykresu opadających zbocz
        wypelnijWykres(wykresy, dane, liczbaDanych, 2*j, 0)
        #wypełnianie wykresu narastających zbocz
        wypelnijWykres(wykresy, dane, liczbaDanych, 2*j, 1)
        #malowanie wykresu opadających zbocz
        zwrot=malowanieWykresuZKanalu(wykresy, zwrot, poleWykr, czas, j, 0)
        #malowanie wykresu narastających zbocz
        zwrot=malowanieWykresuZKanalu(wykresy, zwrot, poleWykr, czas, j, 1)
    return zwrot

def wypelnijWykres(wykresy, dane, liczbaDanych, ktoreKanaly, ktoreZbocze):
    for i in xrange(liczbaDanych):
        chwilowa=dane[i][ktoreKanaly+ktoreZbocze][3]-dane[i][ktoreKanaly+2+ktoreZbocze][3]
        wykresy[ktoreKanaly+ktoreZbocze].AddBinContent(chwilowa+512)

def malowanieWykresuZKanalu(zmienneWykresowe, pojemnikOdchylen, poleWykr, czas, ktoraPara, ktoreZbocze):
    zmienneWykresowe[2*ktoraPara+ktoreZbocze].Fit("gaus","Q","",-511,511)
    pojemnikOdchylen.append(zmienneWykresowe[2*ktoraPara+ktoreZbocze].GetFunction("gaus").GetParameter(2))
    zmienneWykresowe[2*ktoraPara+ktoreZbocze].SetAxisRange(zmienneWykresowe[2*ktoraPara+ktoreZbocze].FindFirstBinAbove()-512, zmienneWykresowe[2*ktoraPara+ktoreZbocze].FindLastBinAbove()-512)
    zmienneWykresowe[2*ktoraPara+ktoreZbocze].Write()
    poleWykr.Update()
    poleWykr.Print("Wykresy "+czas+"/Wykres "+str(ktoraPara+1)+(" nar" if ktoreZbocze==1 else " op")+".png")
    time.sleep(0.1)
    return pojemnikOdchylen



def malujWykresyOdchylen(ileKanalow):
    wykresKoncowyNar=TH1I("Odchylenia standardowe (zb. narastajace)","Wykres odchylen standardowych",ileKanalow-1,0,ileKanalow-2)
    wykresKoncowyOp=TH1I("Odchylenia standardowe (zb. opadajace)","Wykres odchylen standardowych",ileKanalow-1,0,ileKanalow-2)
    #wypełnianie wykresu zbiorczego odchyleń dla zbocz opadających
    wypelnijWykresZbiorczy(wykresKoncowyOp, ileKanalow, sigmy, 0)
    #wypełnianie wykresu zbiorczego odchyleń dla zbocz narastających
    wypelnijWykresZbiorczy(wykresKoncowyNar, ileKanalow, sigmy, 1)
    #malowanie wykresu zbiorczego odchyleń dla zbocz narastających
    malowanieWykresuZbiorczego(wykresKoncowyNar, "narastajace", czas)
    #malowanie wykresu zbiorczego odchyleń dla zbocz opadających
    malowanieWykresuZbiorczego(wykresKoncowyOp, "opadajace", czas)

def wypelnijWykresZbiorczy(wykres, ileKanalow, pojemnikOdchylen, ktoreZbocze):
    for i in range(ileKanalow-1):
        wykres.AddBinContent(i+1, pojemnikOdchylen[2*i]+ktoreZbocze)
        wykres.GetXaxis().SetBinLabel(i+1,str(i)+"-"+str(i+1))
    
def malowanieWykresuZbiorczego(wykres, ktoreZbocze, czas):
    poleWykresu=TCanvas("Odchylenia","Odchylenia standardowe",1280,720)
    
    wykres.SetTitle("Odchylenia standardowe (zb. "+ktoreZbocze+")")
    wykres.Draw()
    time.sleep(0.1)
    wykres.SetDirectory(plik)
    wykres.Write()
    poleWykresu.Print("Wykresy "+czas+"/Odchylenia "+ktoreZbocze+".png")
    
#odczyt danych z pliku przekonwertowanego na .root
nazwaPliku=pliki.wybierzPlik(pliki.listaPlikow("root","./"))
plik=TFile(nazwaPliku)
drzewo=plik.Get("Zestawy")
liczbaDanych=drzewo.GetEntries()
liczbaKanalow=drzewo.GetBranch("Zestaw").GetNleaves()/2
czas=nazwaPliku[nazwaPliku.index("["):nazwaPliku.index("]")+1]
  
dane=odczytDanychZPliku(drzewo, liczbaDanych, liczbaKanalow)
plik.Close()

#tworzenie wykresów
plik=TFile("histogramy "+czas+".root","recreate")

#wykresy różnic między kanałami
wykresy=stworzZmienneWykresowe(plik, liczbaKanalow)

#tworzenie poszczególnych wykresów i pobieranie wartości odchylenia standardowego z dopasowanej funkcji
os.mkdir("./Wykresy "+czas)
sigmy=malujWykresyRoznic(liczbaKanalow)

#tworzenie wykresów zbiorczych odchyleń
malujWykresyOdchylen(liczbaKanalow)

plik.Close()
