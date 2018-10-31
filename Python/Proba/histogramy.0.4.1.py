# coding=utf-8
from ROOT import TFile, TH1I, TH2I, TCanvas, TBrowser, gStyle
import time, os
import pliki
import progressbar

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
        dodajDane=[]
        for j in xrange(len(drzewo.FTAB_Rising)):
            #odczyt danych kanałowych (zbocza opadające)
            dodajDane.append(odczytDanychZKanalu(drzewo, j, "op"))
            #odczyt danych kanałowych (zbocza narastające)
            #dodajDane.append(odczytDanychZKanalu(drzewo, j , "nar"))
        zwrot=zwrot+[dodajDane]
    return zwrot
    #format zwracanych danych:
    #dane(pomiar(kanałOp/Nar(zbocze,nrKanału,zgrubnyCzas,zmierzonyCzas)))
    #dane - tablica składająca się z tablic reprezentujących dany pomiar
    #pomiar - tablica zawierająca wyniki pomiaru przedstawiona za pomocą 2*ileKanalow tablic zawierających wyniki z danego kanału podzielonego na zb nar i opad
    #kanałOp/Nar - tablica składająca się z czterech elementów reprezentujących wynik pomiaru z danego kanału dla danego zbocza

def odczytDanychZKanalu(galaz, nrKanalu, zbocze):
    kanal=[]
    kanal.append(galaz.FTAB_Rising[nrKanalu])
    kanal.append(galaz.FTAB_Channel[nrKanalu])
    kanal.append(galaz.FTAB_Coarse[nrKanalu])
    kanal.append(galaz.FTAB_Fine[nrKanalu])
    return kanal



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
    wypelnijWykres(wykresy, dane, liczbaDanych)
    for j in range(ileKanalow):
        for k in range(j):
            #wypełnianie wykresu opadających zbocz
            #wypełnianie wykresu narastających zbocz
            #wypelnijWykres(wykresy, dane, liczbaDanych, j, k, 1)
            #malowanie wykresu opadających zbocz
            malowanieWykresuZKanalu(wykresy, zwrot, poleWykr, czas, j, k, 0)
            #malowanie wykresu narastających zbocz
            malowanieWykresuZKanalu(wykresy, zwrot, poleWykr, czas, j, k, 1)
    return zwrot

class Tymcz():
    wykresyOp=[]
    wykresyNar=[]
    def __init__(self,ileKanalow):
        for i in range(ileKanalow):
            zmienna=[]
            zmienna2=[]
            self.wykresyOp.append(zmienna)
            self.wykresyNar.append(zmienna2)
    def dodaj(self,zbocze,kanal,wartosc):
        if int(zbocze)==1:
            self.wykresyNar[kanal].append(wartosc)
        else:
            self.wykresyOp[kanal].append(wartosc)
    def wez(self,zbocze,kanal):
        return self.wykresyNar[kanal] if zbocze==1 else self.wykresyOp[kanal]

def wypelnijWykres(wykresy, dane, liczbaDanych):
    pasek=progressbar.ProgressBar(maxval=liczbaDanych, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    pasek.start()
    
    
    
    ileKan=104
    
    
    
    
    for i in xrange(liczbaDanych):
        #if not ((dane[i][2*kanal1+ktoreZbocze][2]==0 and dane[i][2*kanal1+ktoreZbocze][3]==0) or (dane[i][2*kanal2+ktoreZbocze][2]==0 and dane[i][2*kanal2+ktoreZbocze][3]==0)):
        t=Tymcz(ileKan)
        for j in xrange(len(dane[i])):
            chwilowa=(dane[i][j][2]*128)+(dane[i][j][3])
            kanal=dane[i][j][1]
            zbocze=dane[i][j][0]
            t.dodaj(zbocze, kanal, chwilowa)
        for j in xrange(ileKan):
            for k in xrange(j):
                chwilowe1o=t.wez(0, j)
                chwilowe2o=t.wez(0, k)
                chwilowe1n=t.wez(1, j)
                chwilowe2n=t.wez(1, k)
                if (len(chwilowe1o)!=0 and len(chwilowe2o)!=0):
                    chwilowao=chwilowe1o[len(chwilowe1o)-1]-chwilowe2o[len(chwilowe2o)-1]
                    if(chwilowao>-528 and chwilowao<528):
                        wykresy.wezWykres(0, j, k).AddBinContent(chwilowao+528)
                if (len(chwilowe1n)!=0 and len(chwilowe2n)!=0):
                    chwilowan=chwilowe1n[len(chwilowe1n)-1]-chwilowe2n[len(chwilowe2n)-1]
                    if(chwilowan>-528 and chwilowan<528):
                        wykresy.wezWykres(1, j, k).AddBinContent(chwilowan+528)
        pasek.update(i+1)
#            if (dane[i][j][1]==kanal1):
#                if (dane[i][j][0]==0):
#                    chwil0Kan1=(dane[i][j][2]*128)+(dane[i][j][3])
#                else:
#                    chwil1Kan1=(dane[i][j][2]*128)+(dane[i][j][3])
#            elif (dane[i][j][1]==kanal2):
#                if (dane[i][j][0]==0):
#                    chwil0Kan2=(dane[i][j][2]*128)+(dane[i][j][3])
#                else:
#                    chwil1Kan2=(dane[i][j][2]*128)+(dane[i][j][3])
#        if (chwil0Kan1!=-1 and chwil0Kan2!=-1):
#            chwilowa0=chwil0Kan1-chwil0Kan2
#            if (chwilowa0>-528 and chwilowa0<528):
#                wykresy.wezWykres(0, kanal1, kanal2).AddBinContent(chwilowa0+528)
#        if (chwil1Kan1!=-1 and chwil1Kan2!=-1):
#            chwilowa1=chwil1Kan1-chwil1Kan2
#            if (chwilowa1>-528 and chwilowa1<528):
#                wykresy.wezWykres(1, kanal1, kanal2).AddBinContent(chwilowa1+528)

def malowanieWykresuZKanalu(zmienneWykresowe, pojemnikOdchylen, poleWykr, czas, kanal1, kanal2, ktoreZbocze):
    wykres=zmienneWykresowe.wezWykres(ktoreZbocze, kanal1, kanal2)
    wykres.Fit("gaus","Q","",-527,527)
    wykres.SetAxisRange(-527,527)#wykres.FindFirstBinAbove()-527, wykres.FindLastBinAbove()-527)
    if (wykres.FindFirstBinAbove()!=-1):
        poleWykr.Update()
        wykres.Write()
        time.sleep(0.1)
        poleWykr.Print("Wykresy "+czas+"/Wykres "+str(kanal1)+"-"+str(kanal2)+(" nar" if ktoreZbocze==1 else " op")+".png")
        odchylenie=wykres.GetFunction("gaus").GetParameter(2)
        pojemnikOdchylen.ustawWartoscOdchylenia(ktoreZbocze,kanal1,kanal2,odchylenie)



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
            if (type(pojemnikOdchylen.wezWartosc(ktoreZbocze, i, j))!=type(Odchylenie())):
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
drzewo=plik.Get("FTAB_Timeslots")
liczbaDanych=drzewo.GetEntries()
liczbaKanalow=104#drzewo.GetBranch("Zestaw").GetNleaves()/2
czas=nazwaPliku[nazwaPliku.index("["):nazwaPliku.index("]")+1]

dane=odczytDanychZPliku(drzewo, liczbaDanych, liczbaKanalow)
plik.Close()

#print len(dane)
print ("Skończyłem odczyt.")

#tworzenie wykresów
plik=TFile("histogramy "+czas+".root","recreate")

#wykresy różnic między kanałami
wykresy=stworzZmienneWykresowe(plik, liczbaKanalow)

#tworzenie poszczególnych wykresów i pobieranie wartości odchylenia standardowego z dopasowanej funkcji
if (not os.path.exists("./Wykresy "+czas)):
    os.mkdir("./Wykresy "+czas)
sigmy=malujWykresyRoznic(wykresy, dane, liczbaKanalow, liczbaDanych, czas)

#tworzenie wykresów zbiorczych odchyleń
malujWykresyOdchylen(sigmy, liczbaKanalow, czas, plik)

plik.Close()
