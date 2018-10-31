# coding=utf-8
import ROOT
from ROOT import gROOT, TCanvas, TF1, TPad, TH1I, TH2I, gStyle, TFile, TLegend
from ROOT import TH2F
import numpy as np
#from matplotlib import pyplot as plt
import time 
import progressbar
from time import sleep 

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





def malujWykresyRoznic(wykresy, ileKanalow,f):
    
    #myTree = f.Get("Wykres 13-5 op.")
    zwrot=PojemnikOdchylen(ileKanalow)
    for j in range(ileKanalow):
        for k in range(j):
            nap="Wykres "+str(j)+"-"+str(k)
            wykO=f.Get(nap+" op.")
            wykN=f.Get(nap+" nar.")
            wykresy.ustawWykres(0,j,k,wykO)
            wykresy.ustawWykres(1,j,k,wykN)
    for j in range(ileKanalow):
        for k in range(j):
            malowanieWykresuZKanalu(wykresy, zwrot, j, k, 0)
            malowanieWykresuZKanalu(wykresy, zwrot, j, k, 1)
    return zwrot

def malowanieWykresuZKanalu(zmienneWykresowe, pojemnikOdchylen, kanal1, kanal2, ktoreZbocze):
    wykres=zmienneWykresowe.wezWykres(ktoreZbocze, kanal1, kanal2)
    nic=zmienneWykresowe.wezWykres(0,13,5)
    if (nic!=wykres):
        if (wykres.FindFirstBinAbove()!=-1):
            odchylenie=wykres.GetFunction("gaus").GetParameter(2)
            pojemnikOdchylen.ustawWartoscOdchylenia(ktoreZbocze,kanal1,kanal2,odchylenie)
        
        
        
        
        
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
        
        
        



plik=ROOT.TFile.Open("histogramy [18201172953].root")
czas="[18201172953]"
bly=PojemnikWykresowRoznic(104)
sigmy=malujWykresyRoznic(bly, 104,plik)

print (type(sigmy.wezWartosc(0, 13, 5))==type(Odchylenie())) 
malujWykresyOdchylen(sigmy, 104, czas, plik)

plik.Close()