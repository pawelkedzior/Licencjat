# coding=utf-8
from ROOT import gROOT, TFile, TTree, TRandom3
from ROOT.Math import *
import time

def konwertujNaBity(wartosc,ileBitow):
	wynik=[0 for i in range(ileBitow)]
	i=0
	while(wartosc!=0):
		wynik[ileBitow-1-i]=bool(wartosc%2)
		wartosc=wartosc/2
		i=i+1
	return wynik

class ZestawDanych():
	kanaly=[[0] for i in range(52)]
	def daneZKanalu(self, numer):
		return self.kanaly[numer]
	def wprowadzDoKanalu(self, numer, dane):
		self.kanaly[numer]=dane
	def stworzDane(self, zbocze, numerKanalu, czas):
		czasBity=konwertujNaBity(czas,16)
		rozluznienie=konwertujNaBity(0,8)
		numerBity=konwertujNaBity(numerKanalu,7)
		zbocze=zbocze+numerBity
		zbocze=zbocze+rozluznienie
		zbocze=zbocze+czasBity
		self.wprowadzDoKanalu(numerKanalu, zbocze)
		return zbocze
	def wypelnijKanaly(self, generator, zbocze):
		for i in range(52):
			generator.SetSeed(generator.GetSeed()+48*i)
			liczba=generator.Gaus(600,30)/1;
			liczba=int(liczba)
			self.stworzDane(zbocze,i,liczba)

struktura="struct DaneZKanalow {"
for i in range(52):
	struktura=struktura+"Bool_t kanal"+str(i)+"[32]; "
struktura=struktura+"};"

gROOT.ProcessLine(struktura)
from ROOT import DaneZKanalow

czas=time.strftime("%d.%m.%Y %H:%M:%S")
plik=TFile('daneGener ['+czas+'].root', 'RECREATE')

gener=TRandom3(0)

drzewo=TTree("Zestawy","Drzewo z wygenerowanymi zestawami.")
kanaly=DaneZKanalow()
struktura="kanal0[32]/B"
for i in range(51):
	struktura=struktura+":kanal"+str(i+1)+"[32]"
galaz=drzewo.Branch("Zestaw",kanaly,struktura)
galaz.SetBasketSize(120)
for i in range(1000):
	zestaw=ZestawDanych()
	zestaw.wypelnijKanaly(gener, [0])
	for j in range(52):
		daneKanalowe=zestaw.daneZKanalu(j)
		kanal=getattr(kanaly,"kanal"+str(j))
		for k in range(32):
			kanal[k]=daneKanalowe[k]
	drzewo.Fill()

plik.Write()
plik.Close()
