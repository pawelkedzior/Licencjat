# coding=utf-8
from ROOT import gROOT, TFile, TTree, TRandom3
from ROOT.Math import *
import time

def konwertujNaBity(wartosc,ileBitow):
	wynik=[bool(0) for i in range(ileBitow)]
	i=0
	while(wartosc!=0):
		wynik[ileBitow-1-i]=bool(wartosc%2)
		wartosc=wartosc/2
		i=i+1
	return wynik

class ZestawDanych():
	kanalyNar=[[1] for i in range(52)]
	kanalyOp=[[0] for i in range(52)]
	def daneZKanalu(self, numer, zbocze):
		return (self.kanalyNar[numer] if zbocze[0]==bool(1) else self.kanalyOp[numer])
	def wprowadzDoKanalu(self, numer, dane):
		if dane[0]==1:
			self.kanalyNar[numer]=dane
		else:
			self.kanalyOp[numer]=dane
	def stworzDane(self, zbocze, numerKanalu, czas):
		czasBity=konwertujNaBity(czas,9)
		rozluznienie=konwertujNaBity(0,15)
		numerBity=konwertujNaBity(numerKanalu,7)
		zbocze=zbocze+numerBity
		zbocze=zbocze+rozluznienie
		zbocze=zbocze+czasBity
		self.wprowadzDoKanalu(numerKanalu, zbocze)
		return zbocze
	def wypelnijKanaly(self, generator):
		for i in range(52):
			generator.SetSeed(generator.GetSeed()+48*i)
			liczba=generator.Gaus(300,60)/1;
			liczba=int(liczba)
			generator.SetSeed(generator.GetSeed()+48*i)
			liczba2=generator.Gaus(300,60)/1;
			liczba2=int(liczba2)
			if liczba2>liczba:
				self.stworzDane([bool(0)],i,liczba2)
				self.stworzDane([bool(1)],i,liczba)
			else:
				self.stworzDane([bool(0)],i,liczba)
				self.stworzDane([bool(1)],i,liczba2)

struktura="struct DaneZKanalow {"
for i in range(52):
	struktura=struktura+"Bool_t kanal"+str(i)+"op[32]; "
	struktura=struktura+"Bool_t kanal"+str(i)+"nar[32]; "
struktura=struktura+"};"

gROOT.ProcessLine(struktura)
from ROOT import DaneZKanalow

czas=time.strftime("%d.%m.%Y %H:%M:%S")
plik=TFile('daneGener ['+czas+'].root', 'RECREATE')

gener=TRandom3(0)

drzewo=TTree("Zestawy","Drzewo z wygenerowanymi zestawami.")
kanaly=DaneZKanalow()
struktura="kanal0op[32]/B:kanal0nar[32]"
for i in range(51):
	struktura=struktura+":kanal"+str(i+1)+"op[32]"
	struktura=struktura+":kanal"+str(i+1)+"nar[32]"
galaz=drzewo.Branch("Zestaw",kanaly,struktura)
galaz.SetBasketSize(240)
for i in range(1000):
	zestaw=ZestawDanych()
	zestaw.wypelnijKanaly(gener)
	for j in range(52):
		daneKanalowe=zestaw.daneZKanalu(j,[1])
		kanal=getattr(kanaly,"kanal"+str(j)+"nar")
		for k in range(32):
			kanal[k]=daneKanalowe[k]
		daneKanalowe=zestaw.daneZKanalu(j,[0])
		kanal=getattr(kanaly,"kanal"+str(j)+"op")
		for k in range(32):
			kanal[k]=daneKanalowe[k]
	drzewo.Fill()

plik.Write()
plik.Close()
