#!/usr/bin/perl

use List::MoreUtils 'pairwise';
use warnings;
use strict;
#use Parse::CommandLine;
#use List::Util qw(sum);
#use Fcntl;
use Scalar::Util qw(reftype);
use List::Util qw(min);
use List::Util qw(sum);
use Data::Dump;

sub qdisc_monitoring{
    my($N,$vf_dev_ref, $dropped_ref,$sent_ref,$backlog_ref) = @_;
    my $n = 0;  my $vf_dev = " ";
    #my @dropped = (0) x $N; my @sent = (0) x $N; my  @backlog = (0) x $N;
    my @sent = (0) x $N;
    while ($n < $N){
        $vf_dev = @$vf_dev_ref[$n];
        #print("**********\n vf_dev:$vf_dev\n");
        #$dropped[$n] = 0; $sent[$n] = 0; $backlog[$n] = 0;
        $sent[$n] = $sent_ref[$n];
        my $stats =`/home/cloudran/Documents/nba/algorithm/modules/qdisc_stats.sh "$vf_dev"`;
        my ($dp, $sp, $bl) = split / /, $stats;        
        $dropped_ref->[$n] = $dp;      
        $sent_ref->[$n] = $sp;
        $backlog_ref->[$n] = $bl;
        $n++;
    }        
}

#=begin

1;