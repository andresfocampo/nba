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

#use lib '/home/andres/Documents/PhD/Papers/NBA/algorithm_implementation/modules';
use lib '/home/cloudran/Documents/nba/algorithm/modules';
use nba_monitoring qw(qdisc_monitoring);


sub ema_backlog{ 
    my($N,$backlog_ref,$backlog_ema_ref) = @_;
    my $n = 0; 
    my $window = 4; my $k = 2/($window+1); my $q_i = 0; my $q_f = 0; my $ema = 0;    

    while ($n < $N){        
        $q_i = 0; $q_f; $ema = 0;
        $q_i = @$backlog_ema_ref[$n]; 
        $q_f = @$backlog_ref[$n];
        $ema = ($k*$q_f) + ((1-$k)*$q_i);
        #if ($ema < 0 ){$ema = $ema*(-1);}
        $backlog_ema_ref->[$n] =  $ema;   
        $n++;        
    }    
}   


sub nba_weight{ 
    my($N,$vf_dev_ref,$dropped_ref,$sent_ref,$backlog_ref,$backlog_ema_ref,$w_ref,$nu,$k) = @_;
    my $n = 0; my $theta = 0;
    
    my @sent_i = @$sent_ref; my @sent = (0) x $N;
    qdisc_monitoring($N,$vf_dev_ref,$dropped_ref,$sent_ref,$backlog_ref);          
    @sent = pairwise { $a - $b } @$sent_ref,@sent_i;    
    
    
    ema_backlog($N,$backlog_ref,$backlog_ema_ref);
    print("\n\nbacklog_ema_ref_@$backlog_ema_ref; backlog_@$backlog_ref\n");
    
    while ($n < $N){
        $theta = 0;
        if ($sent[$n] > 0){                        
            if(@$dropped_ref[$n] > 0){
                $theta  = $nu;
                print(" !!!! Queue is full and Packets dropped -> theta_$theta  = nu_$nu\n");            
            }elsif(@$backlog_ref[$n] > 0){
                $theta = @$backlog_ref[$n];
                print("theta_$theta = backlog_@$backlog_ref[$n] \n");                
            }else{             
                $theta = @$backlog_ema_ref[$n];
                print("theta_$theta = backlog_ema_ref_@$backlog_ema_ref[$n]\n");
                #$theta = $backlog_i[$n];                 
                #print("theta_$theta = backlog_i_$backlog_i[$n] \n");                
            }            
        }else{
            $theta = 1;
            print("NO PACKETS!!! theta_$theta = 1\n");
        }        
        $w_ref->[$n] = $theta/($k*$k);            
        print("w_@$w_ref[$n]  = theta_$theta/(k_$k*k_$k);\n");        
        #$w_ref->[$n] = $theta/($nu*$nu);            
        #print("w_@$w_ref[$n]  = theta_$theta/(nu_$nu*nu_$nu); \n");                
        #$w_ref->[$n] = $theta;            
        #print("w_@$w_ref[$n]  = w_@$w_ref[$n] \n");        
        $n++;        
    }
    #@$dropped_ref = @dropped; @$sent_ref = @sent; @$backlog_ref = @backlog; 
}   



sub nba_proportional_weight{ 
    my($w_rt_ref,$W_rt_ref,$w_pr_ref,$W_pr_ref,$w_be_ref,$W_be_ref) = @_;
    my $n = 0; my $sum_weight = 0; my @w = (@$w_rt_ref, @$w_pr_ref,@$w_be_ref);    
    
    $sum_weight = sum(@w);
    if ($sum_weight < 1){$sum_weight = 1;}

    print("w_@w,sum_weight=$sum_weight\n");
    
    @$W_rt_ref = map { $_ * 1/$sum_weight } @$w_rt_ref;
    @$W_pr_ref = map { $_ * 1/$sum_weight } @$w_pr_ref;
    @$W_be_ref = map { $_ * 1/$sum_weight } @$w_be_ref;   
    
}   


sub nba_bandwidth_allocation{ 
    my($w_rt_ref,$W_rt_ref,$MU_rt_ref,$w_pr_ref,$W_pr_ref,$MU_pr_ref,$w_be_ref,$W_be_ref,$MU_be_ref,$BW) = @_;    
    #print ("RT weights: @$w_rt_ref,PR weights: @$w_pr_ref,BE weights: @$w_be_ref\n");
    nba_proportional_weight($w_rt_ref,$W_rt_ref,$w_pr_ref,$W_pr_ref,$w_be_ref,$W_be_ref);

    @$MU_rt_ref = map { $_ * $BW } @$W_rt_ref;
    @$MU_pr_ref = map { $_ * $BW } @$W_pr_ref;
    @$MU_be_ref = map { $_ * $BW } @$W_be_ref;       

}   


1;