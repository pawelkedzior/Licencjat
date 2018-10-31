# coding=utf-8
from os import listdir

plik=open("nowy1.txt","w")

bla=listdir("/media/janek/Programy, Gry/Programy/UltraStar Deluxe/songs/Camp Rock")
l=len(bla)
for x in range(l):
	plik.write(bla[x])
	plik.write("\n")

