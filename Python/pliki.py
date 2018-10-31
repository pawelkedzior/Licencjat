# coding=utf-8
from os import listdir

def listaPlikow(rozszerzenie, sciezka):
    if rozszerzenie[0]!=".":
        rozszerzenie="."+rozszerzenie
    
    pliki=listdir(sciezka)

    naszepliki=[]
    for plik in pliki:
        if plik[-(len(rozszerzenie)):]==rozszerzenie:
            naszepliki=naszepliki+[plik]
        
    return naszepliki

def wybierzPlik(plikowLista):
    if (plikowLista==[]):
        print "Lista jest pusta"
        return
    print "\033[2J\033[0;1HOto pliki w katalogu:"
    for plik in plikowLista:
        print "[ ] "+plik
    print "\033[2;2Ho]"
    print "\033["+str(len(plikowLista)+1)+";0H"
    i=2
    while (1):
        z=getch()
        if(z=="\033"):
            z=getch()
            if(z=="["):
                z=getch()
                if(z=="A" and i>2):
                    print "\033["+str(i)+";2H "
                    i=i-1
                    print "\033["+str(i)+";2Ho"
                    print "\033["+str(len(plikowLista)+1)+";0H"
                elif(z=="B" and i<len(plikowLista)+1):
                    print "\033["+str(i)+";2H "
                    i=i+1
                    print "\033["+str(i)+";2Ho"
                    print "\033["+str(len(plikowLista)+1)+";0H"
                elif(z=="C"):
                    break
        elif(ord(z)==13):
            break
    return plikowLista[i-2]

def getch():
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch







