#!/usr/bin/perl -w
package ODCZYT;

use strict;
use Net::Pcap;
use Net::PcapUtils;
use POSIX qw(strftime);
use Term::ReadKey;
$,=' ';

our $nr=3;
our $lurz=2;

system ("clear");
print "Avalaible devices:\n\n";
for my $interfejs (@interfejsy) {
    print "[ ] $interfejs : $info_interfejsowe{$interfejs}\n";
    $lurz++;
}
$lurz++;
print "\c[[$nr;2Ho";
print "\c[[$lurz;1H";

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
	print "You've chosen: $interfejsy[$nr]\n";
	$spr=1;	
}

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
		elsif((ord $wcisniete)==10)
		{
			wybor();
		}
	}
ReadMode 1;
}