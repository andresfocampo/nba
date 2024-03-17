#!/usr/bin/perl

########################################## Includes ##########################################
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
use init qw(set_qdisc_init);
use nba_monitoring qw(qdisc_monitoring);


########################################## System patameters ##########################################
my $time_slot_ = 1; # Time slot
my $window_ = 10; # Slide window



################ Timing
my $time_slot_ = 1; # Time slot
my $window_ = 10; # Slide window

############## RT containers
my $R_ = 1; # Numer of RT LXC
my @lxc_rt_ = ("vbbu1","eNB");
my @vf_dev_rt_ = ("enp105s16");
my $nu_rt_ = 170;


my @W_rt_ = (0) x $R_; # proportional weight to use in BW allocation
my @w_rt_ = (0) x $R_; # individual weight
my @MU_rt_ = (0) x $R_;
my @Dp_rt_ = (1) x $R_; #Dropped packets 
my @Sp_rt_ = (1) x $R_; #Sequeued packets (tx)
my @Q_rt_ = (1) x $R_; #backlog

############## PR containers
my $P_ = 1; # Numer of PR LXC
my @lxc_pr_ = ("vbbu3");
my @vf_dev_pr_ = ("enp105s16f2");
my $nu_pr_ = 340;

my @W_pr_ = (0) x $R_; # proportional weight to use in BW allocation
my @w_pr_ = (0) x $R_; # individual weight
my @MU_pr_ = (0) x $P_;
my @Dp_pr_ = (1) x $P_; #Dropped packets d
my @Sp_pr_ = (1) x $P_; #Sent packets (tx)
my @Q_pr_ = (1) x $P_; #backlog


############## BE containers
my $B_ = 1; # Numer of RT LXC
my @lxc_be_ = ("anritsu");
my @vf_dev_be_ = ("enp105s0f1");
my $nu_be_ = 1000;

my @W_be_ = (0) x $R_; # proportional weight to use in BW allocation
my @w_be_ = (0) x $R_; # individual weight
my @MU_be_ = (0) x $B_;
my @Dp_be_ = (1) x $B_; #Dropped packets 
my @Sp_be_ = (1) x $B_; #Sent packets (tx)
my @Q_be_ = (1) x $B_;  #backlog


my $N_containers_ = $R_ + $P_ +  $B_;
my @vf_dev_ = (@vf_dev_rt_, @vf_dev_pr_,@vf_dev_be_); 
my @nu_ = ($nu_rt_,$nu_pr_,$nu_be_);
my @w_ = (@w_rt_, @w_pr_,@w_be_); 
my @W_ = (@W_rt_, @W_pr_,@W_be_);
print("****////*** w_: @w_; @W_\n");

############## Initiating Qdisc
my $dp = 0; my $sp = 0; my $bl = 0;
set_qdisc_init($N_containers_,\@vf_dev_,\@nu_);

### RT-Qdisc
print "\************\ \n INIT RT-Qdisc\n";
qdisc_monitoring($R_,\@vf_dev_rt_,\@Dp_rt_,\@Sp_rt_,\@Q_rt_);
print("dropped: @Dp_rt_ ; sent: @Sp_rt_; backlog: @Q_rt_\n");


### PR-Qdisc
print "\************\ \n INIT PR-Qdisc\n";
#qdisc_monitoring($P_,\@vf_dev_pr_,\@Dp_pr_,\@Sp_pr_,\@Q_pr_);
#print("dropped: @Dp_pr_ ; sent: @Sp_pr_; backlog: @Q_pr_\n");

### BE-Qdisc
print "\************\ \n INIT BE-Qdisc\n";
qdisc_monitoring($B_,\@vf_dev_be_,\@Dp_be_,\@Sp_be_,\@Q_be_);
print("dropped: @Dp_be_ ; sent: @Sp_be_; backlog: @Q_be_\n");

my $j = 1;

my @vector = (1,2,3); my $a = 0;
$a=sum(@vector); 

print("######## a: $a \n")\n;

while ($j < 10){
	#qdisc_monitoring($B_,\@vf_dev_be_,\@Dp_be_,\@Sp_be_,\@Q_be_);	
	print("dropped: @Dp_be_ ; sent: @Sp_be_; backlog: @Q_be_\n");

	#### Weights Omega(t)
	#nba_weight($R_,\@vf_dev_rt_,\@Dp_rt_,\@Sp_rt_,\@Q_rt_,\@w_rt_,$nu_rt_); # computing RT qdisc weight
	#nba_weight($P_,\@vf_dev_pr_,\@Dp_pr_,\@Sp_pr_,\@Q_pr_,\@w_pr_,$nu_pr_); # computing PR qdisc weight    
	nba_weight($B_,\@vf_dev_be_,\@Dp_be_,\@Sp_be_,\@Q_be_,\@w_be_,$nu_be_); # computing BE qdisc weight

	### Bandwidht allocation
	nba_bandwidth_allocation($R,\@w_rt_,\@W_rt_,\@MU_rt_,$P,\@w_pr_,\@W_pr_,\@MU_pr_,$B,\@w_be_,\@W_be_,\@MU_be_)



	my $oe = $w_be_[0]/$nu_be_;
    
	print("weight: @w_be_, $oe\n");
	 
	$j++;
	sleep(1)



}



