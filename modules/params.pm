#!/usr/bin/perl


################ Timing
my $time_slot_ = 1; # Time slot
my $window_ = 10; # Slide window


############## RT containers
my $R_ = 1; # Numer of RT LXC
my @lxc_rt_ = ("vbbu1","eNB");
my @vf_dev_rt_ = ("enp105s16");
my @nu_rt_ = (170);


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
my @nu_pr_ = (340);

my @W_pr_ = (0) x $P_;
my @MU_pr_ = (0) x $P_;
my @Dp_pr_ = (1) x $P_; #Dropped packets d
my @Sp_pr_ = (1) x $P_; #Sent packets (tx)
my @Q_pr_ = (1) x $P_; #backlog


############## BE containers
my $B_ = 1; # Numer of RT LXC
my @lxc_be_ = ("anritsu");
my @vf_dev_be_ = ("enp105s16f4");
my @nu_be_ = (1000);
my @W_be_ = (0) x $B_;
my @MU_be_ = (0) x $B_;
my @Dp_be_ = (1) x $B_; #Dropped packets 
my @Sp_be_ = (1) x $B_; #Sent packets (tx)
my @Q_be_ = (1) x $B_;  #backlog


my $N_containers_ = $R_ + $P_ +  $B_;
my @vf_dev_ = (@vf_dev_rt_, @vf_dev_pr_,@vf_dev_be_); 
my @nu_ = (@nu_rt_,@nu_pr_,@nu_be_);
