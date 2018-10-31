# coding=utf-8
from ROOT import TFile, TH1I, TH2I, TCanvas, TBrowser, gStyle
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
    for i in range(17):
        zgrubnyCzas=zgrubnyCzas*2+pomiar[i+8]
    zmierzonyCzas=0
    for i in range(7):
        zmierzonyCzas=zmierzonyCzas*2+pomiar[i+25]
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
    #pomiar - tablica zawierająca wyniki pomiaru przedstawiona za pomocą 2*ileKanalow tablic zawierających wyniki z danego kanału podzielonego na zb nar i opad
    #kanałOp/Nar - tablica składająca się z czterech elementów reprezentujących wynik pomiaru z danego kanału dla danego zbocza

def odczytDanychZKanalu(galaz, nrKanalu, zbocze):
    kanal=[]
    for k in range(32):
        kanal.append(int(galaz.GetLeaf("kanal"+str(nrKanalu)+zbocze).GetValue(k)))
    return rozlozPomiarNaSkladowe(kanal)



class PojemnikWykresowRoznic():
    wykresyOp=[]
    wykresyNar=[]
    def __init__(self,ileKanalow):
        for i in range(ileKanalow*(ileKanalow-1)/2):
            zmienna=0
            self.wykresyOp.append(zmienna)
            self.wykresyNar.append(zmienna)
    def ustawWykres(self,zbocze,kanal1,kanal2,wykres):
        if zbocze==1:
            self.wykresyNar[(kanal1-1)*kanal1/2+kanal2]=wykres
        else:
            self.wykresyOp[(kanal1-1)*kanal1/2+kanal2]=wykres
    def wezWykres(self,zbocze,kanal1,kanal2):
        return self.wykresyNar[(kanal1-1)*kanal1/2+kanal2] if zbocze==1 else self.wykresyOp[(kanal1-1)*kanal1/2+kanal2]

def stworzZmienneWykresowe(katalog, ileKanalow):
    zwrot=PojemnikWykresowRoznic(ileKanalow)
    for i in range(ileKanalow):
        for j in range(i):
            stworzZmiennaWykresowa(katalog, i, j, 0, zwrot)
            stworzZmiennaWykresowa(katalog, i, j, 1, zwrot)
    return zwrot

def stworzZmiennaWykresowa(katalog, kanal1, kanal2, jaka, pojemnik):
    nazwaKr=" op." if jaka==0 else " nar."
    nazwaDl="opadajace" if jaka==0 else "narastajace"
    wykr=TH1I(("Wykres "+str(kanal1)+"-"+str(kanal2)+nazwaKr),("Roznica miedzy kanalami "+str(kanal1)+" a "+str(kanal2)+" (zbocze "+nazwaDl+")"),1055,-527,527)
    wykr.SetDirectory(katalog)
    pojemnik.ustawWykres(jaka,kanal1,kanal2,wykr)



class Odchylenie():
    kanal1=-1
    kanal2=-1
    wartosc=-1.0
    def wezKanaly(self):
        return [self.kanal1, self.kanal2]
    def wezWartoscOdchylenia(self):
        return self.wartosc
    def ustawKanal1(self, nrKanalu):
        self.kanal1=nrKanalu
    def ustawKanal2(self, nrKanalu):
        self.kanal2=nrKanalu
    def ustawWartosc(self, wartosc):
        self.wartosc=wartosc
    
class PojemnikOdchylen():
    kanalyOp=[]
    kanalyNar=[]
    def __init__(self,liczbaKanalow):
        for i in range(liczbaKanalow*(liczbaKanalow-1)/2):
            zmienna=Odchylenie()
            self.kanalyOp.append(zmienna)
            zmienna=Odchylenie()
            self.kanalyNar.append(zmienna)
    def ustawWartoscOdchylenia(self,zbocze,kanal1,kanal2,wartosc):
        if(zbocze==0):
            self.kanalyOp[(kanal1-1)*kanal1/2+kanal2]=wartosc
        else:
            self.kanalyNar[(kanal1-1)*kanal1/2+kanal2]=wartosc
    def wezWartosc(self, zbocze, kanal1, kanal2):
        return (self.kanalyNar[(kanal1-1)*kanal1/2+kanal2]) if (zbocze==1) else (self.kanalyOp[(kanal1-1)*kanal1/2+kanal2])

def malujWykresyRoznic(wykresy, dane, ileKanalow, liczbaDanych, czas):
    poleWykr=TCanvas("Rozkład","Rozklad roznic pomiarowych miedzy kanalami",1280,720)
    zwrot=PojemnikOdchylen(ileKanalow)
    for j in range(ileKanalow):
        for k in range(j):
            #wypełnianie wykresu opadających zbocz
            wypelnijWykres(wykresy, dane, liczbaDanych, j, k, 0)
            #wypełnianie wykresu narastających zbocz
            wypelnijWykres(wykresy, dane, liczbaDanych, j, k, 1)
            #malowanie wykresu opadających zbocz
            malowanieWykresuZKanalu(wykresy, zwrot, poleWykr, czas, j, k, 0)
            #malowanie wykresu narastających zbocz
            malowanieWykresuZKanalu(wykresy, zwrot, poleWykr, czas, j, k, 1)
    return zwrot

def wypelnijWykres(wykresy, dane, liczbaDanych, kanal1, kanal2, ktoreZbocze):
    for i in xrange(liczbaDanych):
        if not ((dane[i][2*kanal1+ktoreZbocze][2]==0 and dane[i][2*kanal1+ktoreZbocze][3]==0) or (dane[i][2*kanal2+ktoreZbocze][2]==0 and dane[i][2*kanal2+ktoreZbocze][3]==0)):
            chwilKan1=(dane[i][2*kanal1+ktoreZbocze][2]*40)+(dane[i][2*kanal1+ktoreZbocze][3])
            chwilKan2=(dane[i][2*kanal2+ktoreZbocze][2]*40)+(dane[i][2*kanal2+ktoreZbocze][3])
            chwilowa=chwilKan1-chwilKan2
            wykresy.wezWykres(ktoreZbocze, kanal1, kanal2).AddBinContent(chwilowa+528)

def malowanieWykresuZKanalu(zmienneWykresowe, pojemnikOdchylen, poleWykr, czas, kanal1, kanal2, ktoreZbocze):
    wykres=zmienneWykresowe.wezWykres(ktoreZbocze, kanal1, kanal2)
    wykres.Fit("gaus","Q","",-527,527)
    odchylenie=wykres.GetFunction("gaus").GetParameter(2)
    pojemnikOdchylen.ustawWartoscOdchylenia(ktoreZbocze,kanal1,kanal2,odchylenie)
    wykres.SetAxisRange(wykres.FindFirstBinAbove()-527, wykres.FindLastBinAbove()-527)
    wykres.Write()
    poleWykr.Update()
    time.sleep(0.1)
    poleWykr.Print("Wykresy "+czas+"/Wykres "+str(kanal1)+"-"+str(kanal2)+(" nar" if ktoreZbocze==1 else " op")+".png")



def malujWykresyOdchylen(sigmy, ileKanalow, czas, katalog):
	gStyle.SetOptStat(0)
	wykresKoncowyNar=TH2I("Odchylenia standardowe (zb. narastajace)","Wykres odchylen standardowych", ileKanalow-1,1,ileKanalow,ileKanalow-1,0,ileKanalow-1)
	wykresKoncowyOp=TH2I("Odchylenia standardowe (zb. opadajace)","Wykres odchylen standardowych",ileKanalow-1,1,ileKanalow,ileKanalow-1,0,ileKanalow-1)
    #wypełnianie wykresu zbiorczego odchyleń dla zbocz opadających
	wypelnijWykresZbiorczy(wykresKoncowyOp, ileKanalow, sigmy, 0)
    #wypełnianie wykresu zbiorczego odchyleń dla zbocz narastających
	wypelnijWykresZbiorczy(wykresKoncowyNar, ileKanalow, sigmy, 1)
    #malowanie wykresu zbiorczego odchyleń dla zbocz narastających
	malowanieWykresuZbiorczego(wykresKoncowyNar, "narastajace", czas, katalog)
    #malowanie wykresu zbiorczego odchyleń dla zbocz opadających
	malowanieWykresuZbiorczego(wykresKoncowyOp, "opadajace", czas, katalog)

def wypelnijWykresZbiorczy(wykres, ileKanalow, pojemnikOdchylen, ktoreZbocze):
    for i in range(ileKanalow):
        for j in range(i):
            wykres.Fill(i,j, pojemnikOdchylen.wezWartosc(ktoreZbocze, i, j))
    for i in range(ileKanalow-1):
        wykres.GetXaxis().SetBinLabel(i+1,str(i+1))
        wykres.GetYaxis().SetBinLabel(i+1,str(i))
    
def malowanieWykresuZbiorczego(wykres, ktoreZbocze, czas, katalog):
    poleWykresu=TCanvas("Odchylenia","Odchylenia standardowe",1280,720)
    wykres.SetTitle("Odchylenia standardowe (zb. "+ktoreZbocze+")")
    wykres.SetDirectory(katalog)
    wykres.Write()
    wykres.Draw("COLZ")
    time.sleep(1)
    poleWykresu.Print("Wykresy "+czas+"/Odchylenia "+ktoreZbocze+".png")

#odczyt danych z pliku przekonwertowanego na .root
nazwaPliku=pliki.wybierzPlik(pliki.listaPlikow("root","./"))#"./daneGener [19.07.2018 02:24:53].root"
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
sigmy=malujWykresyRoznic(wykresy, dane, liczbaKanalow, liczbaDanych, czas)

#tworzenie wykresów zbiorczych odchyleń
malujWykresyOdchylen(sigmy, liczbaKanalow, czas, plik)

plik.Close()
