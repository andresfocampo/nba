#!/usr/bin/perl

use warnings;
use strict;



use warnings;
use strict;


my @vf_dev_ = ("enp105s16","enp105s16f2","enp105s16f4");

for my $vf (@vf_dev_) {
    print("vf_dev_ $vf\n");
    system("sudo tc qdisc del dev $vf root 2> /dev/null > /dev/null");	
    system("sudo ip link set $vf txqueuelen 1000");
    system("sudo tc -g -s qdisc ls dev $vf");

}

1;