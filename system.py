#!/usr/bin/env python

import numpy as np
import math
from scipy.stats import poisson
from scipy.stats import bernoulli

#from container import Container
#from system import Driver_Queue
#from system import Virtual_Queue



class Controller : 
    #def __init__(self,containers_k1,R,container_k2,P,containers_k3,B,buffer_size) :
    def __init__(self,R,congestion_control_queues_k1,service_rates_k1,P,congestion_control_queues_k2,service_rates_k2,B,congestion_control_queues_k3,service_rates_k3,Theta,window_size) :
        
        # self.bandwidth_ = bandwidth
        # self.bandwidth_pps_ = bandwidth /  pkt_mtu
        # self.pkt_mtu = pkt_mtu
        self.Theta_ = Theta
        self.ema_alpha = 2/(window_size + 1)        
        
        ##-->Containers:        
        #TS:
        self.R_ = R; #number of TS containers        
        self.IDs_k1_ = IDs
        self.VFs_k1_ = VFs #List of NIC's VF for containers type k
        self.backlogs_buffer_k1_ = np.zeros((R,window_size),dtype=np.int32)        
        self.virtual_queues_k1_ = Virtual_Queues(R,service_rates_k1)
        
        #PR:
        self.P_ = P; #number of PR containers
        self.backlogs_buffer_k2_ = np.zeros((P,window_size),dtype=np.int32)
        self.congestion_control_queues_k2_ = congestion_control_queues_k2
        self.virtual_queues_k2_ = Virtual_Queues(P,service_rates_k2)
        
        #BE:
        self.B_ = B; #number of TS containers
        self.backlogs_buffer_k3_ = np.zeros((B,window_size),dtype=np.int32)
        self.congestion_control_queues_k3_ = congestion_control_queues_k3
        self.virtual_queues_k3_ = Virtual_Queues(B,service_rates_k3)
        
        
        ##-->NBA
        #TS
        self.thetas_k1_ = np.zeros(R, dtype=np.float32)
        self.thetas_avg_k1_ = np.zeros(R, dtype=np.float32)
        
        #PR
        self.thetas_k2_ = np.zeros(P, dtype=np.float32)
        self.thetas_avg_k2_ = np.zeros(P, dtype=np.float32)
        
        #BE
        self.thetas_k3_ = np.ones(B, dtype=np.float32)
        self.thetas_avg_k3_ = np.zeros(B, dtype=np.float32)
                
        
        
    def _queue_monitoring(self, delta_offset,backlog_k1,backlog_k2,backlog_k3) : 
        self.backlogs_buffer_k1_[:,delta_offset] = backlog_k1
        print("self.backlogs_buffer_k1_[:,delta_offset_",delta_offset,"]",self.backlogs_buffer_k1_[:,delta_offset]," = backlog_k1_",backlog_k1)
        print("self.backlogs_buffer_k1_",self.backlogs_buffer_k1_)
        self.backlogs_buffer_k2_[:,delta_offset] = backlog_k2
        print("self.backlogs_buffer_k2_[:,delta_offset]",self.backlogs_buffer_k2_[:,delta_offset]," = backlog_k2_",backlog_k2)
        print("self.backlogs_buffer_k2_",self.backlogs_buffer_k2_)
        self.backlogs_buffer_k3_[:,delta_offset] = backlog_k3
        print("self.backlogs_buffer_k3_[:,delta_offset]",self.backlogs_buffer_k3_[:,delta_offset]," = backlog_k3_",backlog_k3)
        print("self.backlogs_buffer_k3_",self.backlogs_buffer_k3_)
        
        
            
    def _ema_backlog(self, backlog_k1,backlog_k2,backlog_k3) :        
        
        sma_k1 =  np.mean(self.backlogs_buffer_k1_, axis=1)
        print("sma_k1_",sma_k1," =  np.mean(self.backlogs_buffer_k1_",self.backlogs_buffer_k1_,")")
        self.virtual_queues_k1_.arrival_rates_ = (self.ema_alpha*backlog_k1) + ((1-self.ema_alpha)*sma_k1)
        print("self.virtual_queues_k1.arrival_rates_",self.virtual_queues_k1_.arrival_rates_," = (self.ema_alpha_",self.ema_alpha,"*backlog_k1_",backlog_k1,") + ((1-self.ema_alpha_)",self.ema_alpha,"*sma_k1_",sma_k1,")")
        
        sma_k2 =  np.mean(self.backlogs_buffer_k2_, axis=1)
        print("sma_k2_",sma_k2," =  np.mean(self.backlogs_buffer_k2_",self.backlogs_buffer_k2_,")")
        self.virtual_queues_k2_.arrival_rates_ = (self.ema_alpha*backlog_k2) + ((1-self.ema_alpha)*sma_k2)
        print("self.virtual_queues_k2.arrival_rates_",self.virtual_queues_k2_.arrival_rates_," = (self.ema_alpha_",self.ema_alpha,"*backlog_k2_",backlog_k2,") + ((1-self.ema_alpha_)",self.ema_alpha,"*sma_k2_",sma_k2,")")
        
        sma_k3 =  np.mean(self.backlogs_buffer_k3_, axis=1)
        print("sma_k3_",sma_k3," =  np.mean(self.backlogs_buffer_k3_",self.backlogs_buffer_k3_,")")
        self.virtual_queues_k3_.arrival_rates_ = (self.ema_alpha*backlog_k3) + ((1-self.ema_alpha)*sma_k3)        
        print("self.virtual_queues_k3.arrival_rates_",self.virtual_queues_k3_.arrival_rates_," = (self.ema_alpha_",self.ema_alpha,"*backlog_k3_",backlog_k3,") + ((1-self.ema_alpha_)",self.ema_alpha,"*sma_k3_",sma_k3,")")
        
    def _virtual_queues(self) :
        self.virtual_queues_k1_._queueing_dynamics()
        self.virtual_queues_k2_._queueing_dynamics()
        self.virtual_queues_k3_._queueing_dynamics()
        
    def _set_service_rates(self,thetas_avg_k1,thetas_avg_k2,thetas_avg_k3,mean_backlogs,bandwidth,pkt_mtu,q_flag) :
        ##Setting Service for virtual queues
        print("Setting Service for virtual queues")
        v_service_rates_k1 = thetas_avg_k1 * mean_backlogs
        print("v_service_rates_k1_",v_service_rates_k1,"= thetas_avg_k1_",thetas_avg_k1," * mean_backlogs_",mean_backlogs)
        self.virtual_queues_k1_._set_queue_service_rates(v_service_rates_k1)
        
        v_service_rates_k2 = thetas_avg_k2 * mean_backlogs
        print("v_service_rates_k2_",v_service_rates_k2,"= thetas_avg_k2_",thetas_avg_k2," * mean_backlogs_",mean_backlogs)
        self.virtual_queues_k2_._set_queue_service_rates(v_service_rates_k2)
        
        v_service_rates_k3 = thetas_avg_k3 * mean_backlogs
        print("v_service_rates_k3_",v_service_rates_k3,"= thetas_avg_k3_",thetas_avg_k3," * mean_backlogs_",mean_backlogs)
        self.virtual_queues_k3_._set_queue_service_rates(v_service_rates_k3)
        
        
        ##Setting Service for congestion control queues
        print("Setting Service for congestion control queues")
        bandwidth_1_bps = bandwidth * thetas_avg_k1
        print("bandwidth_1_bps",bandwidth_1_bps," = bandwidth_",bandwidth," * thetas_avg_k1",thetas_avg_k1)
        bandwidth_2_bps = bandwidth * thetas_avg_k2
        print("bandwidth_2_bps",bandwidth_2_bps," = bandwidth_",bandwidth," * thetas_avg_k2",thetas_avg_k2)
        bandwidth_3_bps = bandwidth * thetas_avg_k3        
        print("bandwidth_3_bps",bandwidth_3_bps," = bandwidth_",bandwidth," * thetas_avg_k3",thetas_avg_k3)
        
        if q_flag == "pkt" :
            service_rates_k1 = bandwidth_1_bps / bandwidth
            self.congestion_control_queues_k2_._set_queue_service_rates(service_rates_k1,q_flag)
            
            service_rates_k2 = bandwidth_2_bps / bandwidth
            self.congestion_control_queues_k2_._set_queue_service_rates(service_rates_k2,q_flag)
            
            service_rates_k3 = bandwidth_3_bps / bandwidth
            self.congestion_control_queues_k3_._set_queue_service_rates(service_rates_k3,q_flag)
            
        elif q_flag == "gen" :
            service_rates_k1 = bandwidth_1_bps / pkt_mtu
            print("service_rates_k1_",service_rates_k1," = bandwidth_1_bps_",bandwidth_1_bps," / pkt_mtu_",pkt_mtu)
            self.congestion_control_queues_k1_._set_queue_service_rates(service_rates_k1,q_flag)
            
            service_rates_k2 = bandwidth_2_bps / pkt_mtu
            print("service_rates_k2_",service_rates_k2," = bandwidth_2_bps_",bandwidth_2_bps," / pkt_mtu_",pkt_mtu)
            self.congestion_control_queues_k2_._set_queue_service_rates(service_rates_k2,q_flag)
            
            service_rates_k3 = bandwidth_3_bps / pkt_mtu
            print("service_rates_k3_",service_rates_k3," = bandwidth_3_bps_",bandwidth_3_bps," / pkt_mtu_",pkt_mtu)
            self.congestion_control_queues_k3_._set_queue_service_rates(service_rates_k3,q_flag)        
        
        else:
            raise ValueError("Invalid arrival distribution. Choose 'B-bernoulli' or 'P-poisson'.")
        

    def _nba(self,bandwidth,pkt_mtu,q_flag) :
        
        min_k2 =  np.min(self.virtual_queues_k2_.backlogs_)
        min_k3 =  np.min(self.virtual_queues_k3_.backlogs_)
        print("min_k2_",min_k2,"min_k3",min_k3)
        weights_1 = np.vstack((self.virtual_queues_k1_.backlogs_, min_k2 * np.ones(self.R_), min_k3 * np.ones(self.R_)))
        print("weights_1",weights_1)
        self.thetas_k1_ = self.Theta_[np.argmax(weights_1, axis=0)]
        print("self.thetas_k1_",self.thetas_k1_)
        
        
        weights_2 = np.vstack((self.virtual_queues_k2_.backlogs_, min_k3 * np.ones(self.P_)))
        print("weights_2",weights_2)
        self.thetas_k2_ = self.Theta_[np.argmax(weights_2, axis=0)+1]
        print("self.thetas_k2_",self.thetas_k2_)
        
        self.thetas_k3_[:]  = self.Theta_[2]
        print("self.thetas_k3_",self.thetas_k3_)
        
    
        
        sum_thetas_k1 = np.sum(self.thetas_k1_)  
        sum_thetas_k2 = np.sum(self.thetas_k2_) 
        sum_thetas_k3 = np.sum(self.thetas_k3_)
        sum_thetas = sum_thetas_k1 + sum_thetas_k2 + sum_thetas_k3
        
        thetas_avg_k1 =  self.thetas_k1_ / sum_thetas
        print("thetas_avg_k1_",thetas_avg_k1,"= self.thetas_k1_",self.thetas_k1_," / sum_thetas",sum_thetas)
        thetas_avg_k2 =  self.thetas_k2_ / sum_thetas
        print("thetas_avg_k2_",thetas_avg_k2,"= self.thetas_k2_",self.thetas_k2_," / sum_thetas",sum_thetas)

        thetas_avg_k3 =  self.thetas_k3_ / sum_thetas
        print("thetas_avg_k3_",thetas_avg_k3,"= self.thetas_k3_",self.thetas_k3_," / sum_thetas",sum_thetas)
        
        mean_backlogs_k1 = np.mean(self.virtual_queues_k1_.backlogs_)
        mean_backlogs_k2 = np.mean(self.virtual_queues_k2_.backlogs_)
        mean_backlogs_k3 = np.mean(self.virtual_queues_k3_.backlogs_)        
        mean_backlogs = (mean_backlogs_k1 + mean_backlogs_k2 + mean_backlogs_k3) / 3
        
        self._set_service_rates(thetas_avg_k1,thetas_avg_k2,thetas_avg_k3,mean_backlogs,bandwidth,pkt_mtu,q_flag)
        
        
        

class Containers : 
    def __init__(self,N,VFs,IDs) :
        self.N_ = N  #Number of container type k
        self.IDs_ = IDs
        self.VFs_ = VFs #List of NIC's VF for containers type k


    
            
            
class Virtual_Queues : 
    def __init__(self,N,service_rates) :
    #def __init__(self) :        
        #self.N_ = N  #Number of container type k        
        self.backlogs_ = np.zeros(N,dtype=np.float64)
        self.service_rates_ = service_rates
        self.arrival_rates_ = np.zeros(N,dtype=np.float64)
        
        
        
    def _queueing_dynamics(self) :
        print("###--> Virtual Queue: Dequeueing")
        v_service = np.minimum(self.backlogs_,self.service_rates_)
        print("v_service_",v_service," = np.minimum(self.backlogs_,self.service_rates_)",np.minimum(self.backlogs_,self.service_rates_))        
        self.backlogs_ -= v_service
        print("self.backlogs_",self.backlogs_," -= v_service_",v_service)
        
        ###--> Enqueueing
        print("###--> Virtual Queue: Enqueueing")
        self.backlogs_ += self.arrival_rates_
        print("self.backlogs_",self.backlogs_," += self.arrival_rates_",self.arrival_rates_)
        
    
       
    def _set_queue_service_rates(self,service_rates) :
        self.service_rates_ = service_rates
    
        
        