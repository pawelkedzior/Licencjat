#!/usr/bin/perl -w
package ODCZYT;
use strict;
use Net::Pcap;
use Net::PcapUtils;
use POSIX qw(strftime);
use Term::ReadKey;
$,=' ';

use sigtrap 'handler', \&koniec, 'normal-signals';
 
my %info_interfejsowe;
my $blad;
my @interfejsy = Net::Pcap::findalldevs(\%info_interfejsowe, \$blad);
our $spr=3;
our $dlug;
my $data=strftime "%d.%m.%Y %H:%M:%S", localtime;
our $nr=3;
our $lurz=2;

system ("clear");
print "Dostępne urządzenia:\n\n";
for my $interfejs (@interfejsy) {
    print "[ ] $interfejs : $info_interfejsowe{$interfejs}\n";
    $lurz++;
}
$lurz++;
print "\c[[$nr;2Ho";
print "\c[[$lurz;1H";

ReadMode('cbreak');
{
	no warnings;
	my $wcisniete='';
	
	while($spr==3)
	{
		print "\c[[$lurz;1H";
		print "\r";
		
		$wcisniete=ReadKey(0);
		if((ord $wcisniete)==27)
		{
			do{
				$wcisniete=ReadKey(-1);
			}until(!(defined $wcisniete)||!(((ord $wcisniete)<65)||((ord $wcisniete)>67)));
			if(defined $wcisniete)
			{
				if((ord $wcisniete)==65)
				{		
					gora();
				}
				elsif((ord $wcisniete)==66)
				{
					dol();
				}
				elsif((ord $wcisniete)==67)
				{
					wybor();
				}
			}
		}
		elsif((ord $wcisniete)==10)
		{
			wybor();
		}
	}
ReadMode 1;
}

open(PLIK,">dane [$data].txt") or die "Nie mogę otworzyć pliku.";

do{
$blad=Net::PcapUtils::loop(\&analizuj_pakiet, NUMPACKETS => 1, DEV => $interfejsy[$nr], FILTER => 'udp');
die $blad if $blad;
} until ($spr==4);

sub analizuj_pakiet {
  my ($dane_uzytkownika, $naglowek, $pakiet) = @_;
  my $len = length $pakiet;
  my $i=14;
  my $lg = substr $pakiet, $i, 4;  
  
  if ($spr==1||$spr==5)
  {
  		$dlug=unpack ('N', $lg);
  		print "Odebrałem pakiet o długości $dlug\n";
  		$i+=4;
  }
  
  do {
    my $lg = substr $pakiet, $i, 4;
    print PLIK unpack('B32', $lg);
    print PLIK "\n";
    $i+=4;
  } until $i>=$len-4;
  
  if (($len-18)<=($dlug*4))
  {
		if ($spr!=2)
		{
			if($spr==5)
			{
				$spr=2;
			}
			else
			{
  				$spr=0;
			}
		}
  		$dlug-=($len-18)/4
  }
  else
  {
  		if($spr!=2&&$spr!=5)
  		{
  			$spr=1;
  		}
  		else
  		{
  			$spr=4;
  		}
  		print PLIK "\n";
  }
}

sub gora{ 
	if($nr!=3)
	{
		print "\e[$nr;2H ";
		$nr--;
		print "\e[$nr;2Ho";
		print "\c[[$lurz;1H";
	}
}
sub dol{
	if($nr!=$lurz-1)
	{
		print "\e[$nr;2H ";
		$nr++;
		print "\e[$nr;2Ho";
		print "\c[[$lurz;1H";
	}
}
sub wybor{
	$nr=$nr-3;
	print "Wybrałeś: $interfejsy[$nr]\n";
	$spr=1;	
}
sub koniec{	
	if($spr!=1&&$spr!=5&&$spr!=4)
	{
		$spr=2;
	}
	elsif($spr!=4)
	{
		$spr=5;
	}
	print "Kończę.\n";
}
close (PLIK) or die "Nie udało się zamknąć pliku.";
