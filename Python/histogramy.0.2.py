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

#odczyt danych z pliku przekonwertowanego na .root
nazwaPliku=pliki.wybierzPlik(pliki.listaPlikow("root","./"))
plik=TFile(nazwaPliku)
drzewo=plik.Get("Zestawy")
liczbaDanych=drzewo.GetEntries()
czas=nazwaPliku[nazwaPliku.index("["):nazwaPliku.index("]")+1]

#dane(pomiar(kanałOp/Nar(zbocze,nrKanału,zgrubnyCzas,zmierzonyCzas)))
#dane - tablica składająca się z tablic reprezentujących dany pomiar
#pomiar - tablica zawierająca wyniki pomiaru przedstawiona za pomocą 104 tablic zawierających wyniki z danego kanału podzielonego na zb nar i opad
#kanałOp/Nar - tablica składająca się z czterech elementów reprezentujących wynik pomiaru z danego kanału dla danego zbocza  
dane=[]
for i in xrange(liczbaDanych):
    drzewo.LoadTree(i)
    drzewo.GetEntry(i)
    galaz=drzewo.GetBranch("Zestaw")
    galaz.GetEntry(i)
    dodajDane=[]
    for j in xrange(52):
        #odczyt danych kanałowych (zbocza opadające)
        kanal=[]
        for k in range(32):
            kanal.append(int(galaz.GetLeaf("kanal"+str(j)+"op").GetValue(k)))
        dodajDane.append(rozlozPomiarNaSkladowe(kanal))
        #odczyt danych kanałowych (zbocza narastające)
        kanal=[]
        for k in range(32):
            kanal.append(int(galaz.GetLeaf("kanal"+str(j)+"nar").GetValue(k)))
        dodajDane.append(rozlozPomiarNaSkladowe(kanal))
    dane=dane+[dodajDane]
#koniec odczytu danych
plik.Close()

#tworzenie wykresów
plik=TFile("histogramy "+czas+".root","recreate")

#wykresy różnic między kanałami
wykresy=[]
for i in range(51):
    wykresy=wykresy+[TH1I(("Wykres "+str(i+1)+" op."),("Roznica miedzy kanalem "+str(i)+" a "+str(i+1)+" (zbocze opadajace)"),1023,-511,511)]
    wykresy[2*i].SetDirectory(plik)
    wykresy=wykresy+[TH1I(("Wykres "+str(i+1)+" nar."),("Roznica miedzy kanalem "+str(i)+" a "+str(i+1)+" (zbocze narastajace)"),1023,-511,511)]
    wykresy[2*i+1].SetDirectory(plik)
    
poleWykr=TCanvas("Rozkład","Rozklad roznic pomiarowych miedzy kanalami",1280,720)

#tworzenie poszczególnych wykresów i pobieranie wartości odchylenia standardowego z dopasowanej funkcji
sigmy=[]
#czas=time.strftime("%d.%m.%Y %H:%M:%S")
os.mkdir("./Wykresy "+czas)
for j in range(51):
    for i in xrange(liczbaDanych):
        #wypełnianie wykresu opadających zbocz
        chwilowa=dane[i][2*j][3]-dane[i][2*j+2][3]
        wykresy[2*j].AddBinContent(chwilowa+512)
        #wypełnianie wykresu narastających zbocz
        chwilowa2=dane[i][2*j+1][3]-dane[i][2*j+3][3]
        wykresy[2*j+1].AddBinContent(chwilowa2+512)
    #malowanie wykresu opadających zbocz
    wykresy[2*j].Fit("gaus","Q","",-511,511)
    sigmy.append(wykresy[2*j].GetFunction("gaus").GetParameter(2))
    wykresy[2*j].SetAxisRange(wykresy[2*j].FindFirstBinAbove()-512, wykresy[2*j].FindLastBinAbove()-512)
    wykresy[2*j].Write()
    poleWykr.Update()
    poleWykr.Print("Wykresy "+czas+"/Wykres "+str(j+1)+" op.png")
    time.sleep(0.1)
    #malowanie wykresu narastających zbocz
    wykresy[2*j+1].Fit("gaus","Q","",-511,511)
    sigmy.append(wykresy[2*j+1].GetFunction("gaus").GetParameter(2))
    wykresy[2*j+1].SetAxisRange(wykresy[2*j+1].FindFirstBinAbove()-512, wykresy[2*j+1].FindLastBinAbove()-512)
    wykresy[2*j+1].Write()
    poleWykr.Update()
    poleWykr.Print("Wykresy "+czas+"/Wykres "+str(j+1)+" nar.png")
    time.sleep(0.1)

#tworzenie wykresów zbiorczych odchyleń
poleWykresu=TCanvas("Odchylenia","Odchylenia standardowe",1280,720)

wykresKoncowyNar=TH1I("Odchylenia standardowe (zb. narastajace)","Wykres odchylen standardowych",51,0,50)
wykresKoncowyOp=TH1I("Odchylenia standardowe (zb. opadajace)","Wykres odchylen standardowych",51,0,50)
for i in range(51):
    #wypełnianie wykresu zbiorczego odchyleń dla zbocz opadających
    wykresKoncowyOp.AddBinContent(i+1, sigmy[2*i])
    wykresKoncowyOp.GetXaxis().SetBinLabel(i+1,str(i)+"-"+str(i+1))
    #wypełnianie wykresu zbiorczego odchyleń dla zbocz narastających
    wykresKoncowyNar.AddBinContent(i+1, sigmy[2*i+1])
    wykresKoncowyNar.GetXaxis().SetBinLabel(i+1,str(i)+"-"+str(i+1))
#malowanie wykresu zbiorczego odchyleń dla zbocz narastających
wykresKoncowyNar.SetTitle("Odchylenia standardowe (zb. narastajace)")
wykresKoncowyNar.Draw()
time.sleep(0.1)
wykresKoncowyNar.SetDirectory(plik)
wykresKoncowyNar.Write()
poleWykresu.Print("Wykresy "+czas+"/Odchylenia narastajace.png")

#malowanie wykresu zbiorczego odchyleń dla zbocz opadających
wykresKoncowyOp.SetTitle("Odchylenia standardowe (zb. opadajace)")
wykresKoncowyOp.Draw()
time.sleep(0.1)
wykresKoncowyOp.SetDirectory(plik)
wykresKoncowyOp.Write()
poleWykresu.Print("Wykresy "+czas+"/Odchylenia opadajace.png")

#czas potrzebny do obejrzenia wykresów
time.sleep(180)

plik.Close()
