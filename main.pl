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
use init qw(replace_qdisc);
use nba_monitoring qw(qdisc_monitoring);
use nba_allocation qw(nba_weight);
use nba_allocation qw(nba_bandwidth_allocation);


########################################## System patameters ##########################################


################ Timing
my $time_slot_ = 1; # Time slot
my $window_ = 10; # Slide window
my $BW = 1000; # NIC line bandwidht [Mbps]

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
my @Q_ema_rt_ = (0) x $R_;  #backlog_ema

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
my @Q_ema_pr_ = (0) x $P_;  #backlog_ema

############## BE containers
my $B_ = 1; # Numer of RT LXC
my @lxc_be_ = ("anritsu");
my @vf_dev_be_ = ("enp105s16f4");
my $nu_be_ = 1000;

my @W_be_ = (0) x $R_; # proportional weight to use in BW allocation
my @w_be_ = (0) x $R_; # individual weight
my @MU_be_ = (0) x $B_;
my @Dp_be_ = (1) x $B_; #Dropped packets 
my @Sp_be_ = (1) x $B_; #Sent packets (tx)
my @Q_be_ = (1) x $B_;  #backlog
my @Q_ema_be_ = (0) x $B_;  #backlog_ema

my @k_ = (1,2,3); # Priority policy

my $N_containers_ = $R_ + $P_ +  $B_;
my @vf_dev_ = (@vf_dev_rt_, @vf_dev_pr_,@vf_dev_be_); 
my @nu_ = ($nu_rt_,$nu_pr_,$nu_be_);


############## Initiating Qdisc
#set_qdisc_init($N_containers_,\@vf_dev_,\@nu_);
set_qdisc_init($R_,\@vf_dev_rt_,$nu_rt_,$k_[0]);
set_qdisc_init($P_,\@vf_dev_pr_,$nu_pr_,$k_[1]);
set_qdisc_init($B_,\@vf_dev_be_,$nu_be_,$k_[2]);


### RT-Qdisc
print "\************\ \n INIT RT-Qdisc\n";
qdisc_monitoring($R_,\@vf_dev_rt_,\@Dp_rt_,\@Sp_rt_,\@Q_rt_);
print("dropped: @Dp_rt_ ; sent: @Sp_rt_; backlog: @Q_rt_\n");


### PR-Qdisc
print "\************\ \n INIT PR-Qdisc\n";
qdisc_monitoring($P_,\@vf_dev_pr_,\@Dp_pr_,\@Sp_pr_,\@Q_pr_);
print("dropped: @Dp_pr_ ; sent: @Sp_pr_; backlog: @Q_pr_\n");

### BE-Qdisc
print "\************\ \n INIT BE-Qdisc\n";
qdisc_monitoring($B_,\@vf_dev_be_,\@Dp_be_,\@Sp_be_,\@Q_be_);
print("dropped: @Dp_be_ ; sent: @Sp_be_; backlog: @Q_be_\n");

my $vf_dev = "";
while (1){
	### RT-Qdisc
	print "\************\ \n INIT RT-Qdisc\n";
	qdisc_monitoring($R_,\@vf_dev_rt_,\@Dp_rt_,\@Sp_rt_,\@Q_rt_);
	print("dropped: @Dp_rt_ ; sent: @Sp_rt_; backlog: @Q_rt_\n");


	### PR-Qdisc
	print "\************\ \n INIT PR-Qdisc\n";
	qdisc_monitoring($P_,\@vf_dev_pr_,\@Dp_pr_,\@Sp_pr_,\@Q_pr_);
	print("dropped: @Dp_pr_ ; sent: @Sp_pr_; backlog: @Q_pr_\n");

	### BE-Qdisc
	print "\************\ \n INIT BE-Qdisc\n";
	qdisc_monitoring($B_,\@vf_dev_be_,\@Dp_be_,\@Sp_be_,\@Q_be_);
	print("dropped: @Dp_be_ ; sent: @Sp_be_; backlog: @Q_be_\n");

=begin	
	#### Weights Omega(t)
	print ("\n******\n Weights compuitng\n******\n");
	#nba_weight($R_,\@vf_dev_rt_,\@Dp_rt_,\@Sp_rt_,\@Q_rt_,\@w_rt_,$nu_rt_); # computing RT qdisc weight	
	nba_weight($R_,\@vf_dev_rt_,\@Dp_rt_,\@Sp_rt_,\@Q_rt_,\@Q_ema_rt_,\@w_rt_,$nu_rt_,$k_[0]); # computing RT qdisc weight	
	nba_weight($P_,\@vf_dev_pr_,\@Dp_pr_,\@Sp_pr_,\@Q_pr_,\@Q_ema_pr_,\@w_pr_,$nu_pr_,$k_[1]); # computing PR qdisc weight	
	nba_weight($B_,\@vf_dev_be_,\@Dp_be_,\@Sp_be_,\@Q_be_,\@Q_ema_be_,\@w_be_,$nu_be_,$k_[2]); # computing BE qdisc weight
	print ("RT weights: @w_rt_,PR weights: @w_pr_,BE weights: @w_be_\n");

	### Bandwidht allocation
	nba_bandwidth_allocation(\@w_rt_,\@W_rt_,\@MU_rt_,\@w_pr_,\@W_pr_,\@MU_pr_,\@w_be_,\@W_be_,\@MU_be_,$BW);	
	print ("\n******\n Bandwidht allocation\n******\n");
	print ("RT BW: @MU_rt_; PR BW: @MU_pr_; BE BW: @MU_be_\n");

	### Replacing Qdisc with new allocated BW
	
	replace_qdisc($R_,\@vf_dev_rt_,\@MU_rt_,$k_[0]);
	#$vf_dev = $vf_dev_rt_[0];
	#system("sudo tc -g -s qdisc ls dev $vf_dev");

	replace_qdisc($P_,\@vf_dev_pr_,\@MU_pr_,$k_[1]);
	#$vf_dev = $vf_dev_pr_[0];
	#system("sudo tc -g -s qdisc ls dev $vf_dev");
	
	replace_qdisc($B_,\@vf_dev_be_,\@MU_be_,$k_[2]);		
	#$vf_dev = $vf_dev_be_[0];
	#system("sudo tc -g -s qdisc ls dev $vf_dev");
	
	sleep($time_slot_);
=cut


}

