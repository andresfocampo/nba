#!/usr/bin/perl

use warnings;
use strict;



########################################## Init ##########################################
sub set_qdisc_init {        
    my($N,$vf_dev_ref,$nu,$k) = @_;
    my $n = 0; 
    while ($n < $N){
        my $vf_dev = @$vf_dev_ref[$n];                
        my $major = $k.$n;
        my $q_handle = $major.0; # this solve the concatenation problem between $j and strings as we need "$j"0
        print "q_handle: $q_handle\n******************\n\n\n";
        system("sudo ip link set $vf_dev txqueuelen $nu");
	    system("sudo ethtool -K $vf_dev tso off");
        system("sudo tc qdisc del dev $vf_dev root 2> /dev/null > /dev/null");	
        system("sudo tc qdisc add dev $vf_dev root handle $major: htb default $q_handle");
        system("sudo tc class add dev $vf_dev parent $major:0 classid $major:$q_handle htb rate 1000mbit ceil 1000mbit");
        system("sudo tc qdisc add dev $vf_dev parent $major:$q_handle handle $major$major: pfifo limit $nu");	 
        system("sudo tc -g -s qdisc ls dev $vf_dev");
	    $n++;
    }	
}


sub replace_qdisc {    
	my($N,$vf_dev_ref,$MU_ref_,$k) = @_;    
    my $n = 0; 
    print "replacing QDISC for $k\n";
    print "Received Params:\n N:$N; vf_dev:@$vf_dev_ref;MU:@$MU_ref_\n";
    while ($n < $N){
        my $vf_dev = @$vf_dev_ref[$n];                
        my $major = $k.$n;
        my $q_handle = $major.0; # this solve the concatenation problem between $j and strings as we need "$j"0
        my $MU = @$MU_ref_[$n];        
        my $mu = "${MU}mbit";
        print "sudo tc class replace dev $vf_dev parent $major:0 classid $major:$q_handle htb rate $mu ceil $mu\n";
        system("sudo tc class replace dev $vf_dev parent $major:0 classid $major:$q_handle htb rate $mu ceil $mu");                
	    $n++;
    }
}

1;
