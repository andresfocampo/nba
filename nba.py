#!/usr/bin/env python


"""
# Imports
"""
import numpy as np
import os


#from scipy.stats import bernoulli


from system import Controller,Containers,Congestion_Control_Queues





def init(R,queue_size_k1,P,queue_size_k2,B,queue_size_k3,window_size,bandwidth,pkt_mtu,Theta,q_flag) :
    N = R + P + B
    #N = 3    
    bandwidth_k_bps = bandwidth / N
    # service_rates_k1 = np.ones(R, dtype=np.float32)
    # service_rates_k2 = np.ones(P, dtype=np.float32)
    # service_rates_k3 = np.ones(B, dtype=np.float32)
    if q_flag == "pkt" :
        service_rates_k1 = np.ones(R, dtype=np.float32)
        service_rates_k2 = np.ones(P, dtype=np.float32)
        service_rates_k3 = np.ones(B, dtype=np.float32)
        s_param = bandwidth_k_bps / bandwidth
        service_rates_k1 *= s_param
        service_rates_k2 *= s_param
        service_rates_k3 *= s_param
        print("s_param_",s_param,"= bandwidth_k_bps_",bandwidth_k_bps,"/ bandwidth_",bandwidth)
    elif q_flag == "gen" :
        service_rates_k1 = np.ones(R, dtype=np.int32)
        service_rates_k2 = np.ones(P, dtype=np.int32)
        service_rates_k3 = np.ones(B, dtype=np.int32)
        #s_param = math.ceil(bandwidth_k_bps / pkt_mtu)
        s_param = bandwidth_k_bps / pkt_mtu
        print("s_param",s_param," = int(bandwidth_k_bps_",bandwidth_k_bps," / pkt_mtu_",pkt_mtu,")")
        service_rates_k1 *= int(s_param)
        service_rates_k2 *= int(s_param)
        service_rates_k3 *= int(s_param)
    else:
        raise ValueError("Invalid congestion control queue type. Choose 'pkt' or 'gen'.")
    # N = R + P + B
    # bandwidth_k_bps = bandwidth / N    
    # #print("bandwidth_bps",bandwidth_bps)
    # bandwidth_pps = bandwidth_k_bps / pkt_mtu
    # #print("bandwidth_pps",bandwidth_pps)
    # #Dequeue_init = int(bandwidth_pps / cycles_1_seg)  #Normalized to match x_Mega_cycles_per_second -> should by divided by 1000 for the exact granularity
    # Dequeue_init = int(bandwidth_pps)   #Normalized to match x_Mega_cycles_per_second -> should by divided by 1000 for the exact granularity
    # #print("Dequeue_init_",Dequeue_init )
    
    
    # containers_k1 = [Containers(R) for i in range(R)] #collection of TS containers
    # containers_k2 = [Containers(P) for i in range(P)] #collection of PR containers
    # containers_k3 = [Containers(B) for i in range(B)] #collection of BE containers
    
    containers_k1 = Containers(R,q_flag) #TS containers
    containers_k2 = Containers(P,q_flag) #PR containers
    containers_k3 = Containers(B,q_flag) #BE containers
    
    # congestion_control_queues_k1 = [Congestion_Control_Queues(R,queue_size_k1,Dequeue_init) for i in range(R)] #collection of TS containers
    # congestion_control_queues_k2 = [Congestion_Control_Queues(P,queue_size_k1,Dequeue_init) for i in range(P)] #collection of PR containers
    # congestion_control_queues_k3 = [Congestion_Control_Queues(B,queue_size_k1,Dequeue_init) for i in range(B)] #collection of BE containers
    
    
    congestion_control_queues_k1 = Congestion_Control_Queues(R,queue_size_k1,service_rates_k1,q_flag) #Queues for TS containers
    congestion_control_queues_k2 = Congestion_Control_Queues(P,queue_size_k2,service_rates_k2,q_flag) #Queues for PR containers
    congestion_control_queues_k3 = Congestion_Control_Queues(B,queue_size_k3,service_rates_k3,q_flag) #Queues for BE containers
    
    
    #controller = Controller(R,P,B,service_rates_k1,service_rates_k2,service_rates_k3,Theta,window_size)
    controller = Controller(R,congestion_control_queues_k1,service_rates_k1,P,congestion_control_queues_k2,service_rates_k2,B,congestion_control_queues_k3,service_rates_k3,Theta,window_size)
    return controller,\
           containers_k1,containers_k2,containers_k3,\
           congestion_control_queues_k1,congestion_control_queues_k2,congestion_control_queues_k3
           

def arrivals(containers_k1,a_param_k1,containers_k2,a_param_k2,containers_k3,a_param_k3,q_flag) :
    
    if q_flag == "pkt" :
        #if containers_k1.N_ > 0 :
        containers_k1._arrivals_bernoulli(a_param_k1)
        print("containers_k1.arrivals_",containers_k1.arrivals_)
        #if containers_k2.N_ > 0 :
        containers_k2._arrivals_bernoulli(a_param_k2)
        print("containers_k2.arrivals_",containers_k2.arrivals_)
        #if containers_k3.N_ > 0 :
        containers_k3._arrivals_bernoulli(a_param_k3)
        print("containers_k3.arrivals_",containers_k3.arrivals_)
        
    elif q_flag == "gen" :
        #if containers_k1.N_ > 0 :
        containers_k1._arrivals_poisson(a_param_k1)
        print("containers_k1.arrivals_",containers_k1.arrivals_)
        #if containers_k2.N_ > 0 :
        containers_k2._arrivals_poisson(a_param_k2)
        print("containers_k2.arrivals_",containers_k2.arrivals_)
        #if containers_k3.N_ > 0 :
        containers_k3._arrivals_poisson(a_param_k3)
        print("containers_k3.arrivals_",containers_k3.arrivals_)
        
    else:
        raise ValueError("Invalid arrival distribution. Choose 'B-bernoulli' or 'P-poisson'.")

def queueing(containers_k1,congestion_control_queues_k1,containers_k2,congestion_control_queues_k2,containers_k3,congestion_control_queues_k3,q_flag) :
    if q_flag == "pkt" : 
        congestion_control_queues_k1._queueing_dynamics_1pkt(containers_k1.arrivals_)        
        congestion_control_queues_k2._queueing_dynamics_1pkt(containers_k2.arrivals_)
        congestion_control_queues_k3._queueing_dynamics_1pkt(containers_k3.arrivals_)
        
    elif q_flag == "gen" :        
        congestion_control_queues_k1._queueing_dynamics_gen(containers_k1.arrivals_)        
        congestion_control_queues_k2._queueing_dynamics_gen(containers_k2.arrivals_)        
        congestion_control_queues_k3._queueing_dynamics_gen(containers_k3.arrivals_)
        
    else:
        raise ValueError("Invalid congestion control queue type. Choose 'pkt' or 'gen'.")

def mec_server() :        
    
    ###-->Sysem
    ## Time 
    T_max = 100000    
    #cycles_1_seg = 4700 #M_cycles_per_sec - normalized by 1*10⁶ (4700000000/1000000)
    cycles_1_seg = 1000
    
    #T = 1000; #--100;250;1000--# 
    T = cycles_1_seg; #--100;250;1000--# 
    T_s = T; T_offset = 1;     
    
    W = 10; #--10;25--#  
    w = 0;    
    d_T = T / W;  d_T_s = 0; d_T_offset = 0; # sub-time-slot        
    
    ##NIC
    bandwidth = 1000 #Mbps - normalized by 1*10⁶ (1000000000/1000000)
    pkt_mtu = (1.5*8) #kbits - normalized by 1*10³ (1500/1000)*8    
    
    ##Containers
    R = 1; queue_size_k1 = 1000 
    P = 4; queue_size_k2 = 1000 
    B = 4; queue_size_k3 = 1000 
    ###-->
    
    ###--> NBA
    ## Priorities
    Theta = np.array([1,0.7,0.5])
    ###-->
    
    ###--> Simulation
    a_rates_k1 = [200,400,600,800,1000]    
    a_rates_k2 = [200,400,600,800,1000]    
    a_rates_k3 = [200,400,600,800,1000]
    
    a_param_k1 = 0
    a_param_k2 = 0
    a_param_k3 = 0
    #a_param_k2 = a_rates_k2[0] / pkt_mtu
    #a_param_k3 = a_rates_k3[0] / pkt_mtu
    


    q_flag = "gen" ## options: 1) "pkt"  2) "gen"
    ###-->
    
    ###--> Initialization
    controller,\
    containers_k1,containers_k2,containers_k3,\
    congestion_control_queues_k1,congestion_control_queues_k2,congestion_control_queues_k3 =\
        init(R,queue_size_k1,\
             P,queue_size_k2,\
             B,queue_size_k3,\
             W,bandwidth,pkt_mtu,Theta,q_flag
             )
            
    # Dump results to file
    # Specify the path where the files will be saved
    output_directory = "/home/andres/Documents/PhD/Papers/NBA/experiments/simulator/nba/data/users/4/"

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    
    for a_rate in a_rates_k1 :
        
        if q_flag == "pkt" :
            ##--- Arraival based on Bernoulli:
            a_param_k1 = min(a_rate / bandwidth, 1)                        
        elif q_flag == "gen" :
            ##--- Arraival based on Poisson:
            a_param_k1 = a_rate / pkt_mtu
            a_param_k2 = a_rate / pkt_mtu
            a_param_k3 = a_rate / pkt_mtu
        else:
            raise ValueError("Invalid arrival distribution. Choose 'B-bernoulli' or 'P-poisson'.")
                
        output_file = os.path.join(output_directory, f"{a_rate}.csv")
        with open(output_file, "a") as file:
            t = 0;
            while(t <= T_max) :
                print("t:",t)
                
                if (t == T_s) :        
                    print("*******->\n t_",t,"==d_T",d_T)             
                    print("EMA here")
                    controller._ema_backlog(congestion_control_queues_k1.backlogs_,congestion_control_queues_k2.backlogs_,congestion_control_queues_k3.backlogs_)
                    print("Virtual Queues Arrivals")
                    print("controller.virtual_queues_k1_.arrival_rates_",controller.virtual_queues_k1_.arrival_rates_)
                    print("controller.virtual_queues_k2_.arrival_rates_",controller.virtual_queues_k2_.arrival_rates_)
                    print("controller.virtual_queues_k3_.arrival_rates_",controller.virtual_queues_k3_.arrival_rates_)
                    controller._virtual_queues()
                    print("\n *** NBA *** here\n")
                    controller._nba(bandwidth,pkt_mtu,q_flag)
                    
                    T_offset += 1
                    T_s = T * T_offset
      
                if(t == d_T_s) :
                    print("***\n t_",t,"==d_t_s_",d_T_s)
                    print("Monitoring here")            
    #                controller._queue_monitoring(w)
                    controller._queue_monitoring(w,congestion_control_queues_k1.backlogs_,congestion_control_queues_k2.backlogs_,congestion_control_queues_k3.backlogs_)  
                    #print("//// backlog_samples:", controller.containers_k1_[0].U_.backlog_samples_)  
                    print("d_T_offset",d_T_offset)
                    d_T_offset += 1
                    print("d_T_offset_",d_T_offset," -> d_T_offset += 1")
                    d_T_s = d_T * d_T_offset
                    print("d_T_s_",d_T_s," = d_T_",d_T," * d_T_offset_",d_T_offset)
                    #w += 1
                    w = (w + 1) % W
                
                arrivals(containers_k1,a_param_k1,containers_k2,a_param_k2,containers_k3,a_param_k3,q_flag)
                output = [congestion_control_queues_k1.Dequeue_th_[0],congestion_control_queues_k1.service_rates_[0],congestion_control_queues_k1.backlogs_[0],congestion_control_queues_k1.pkt_drop_[0]]
                output = ', '.join(map(str, output)) 
                output += '\n'

                file.write(output)
                #print("containers_k1.arrivals_",containers_k1.arrivals_)
                #arrivals("P",arrival_rate_pps,containers_k1,containers_k2,containers_k3)      
                t += 1            
                queueing(containers_k1,congestion_control_queues_k1,containers_k2,congestion_control_queues_k2,containers_k3,congestion_control_queues_k3,q_flag)
                # if (np.any(congestion_control_queues_k1.backlog_ > 100)) : 
                #     print("\n *** congestion_control_queues_k1.backlog_",congestion_control_queues_k1.backlog_)
                print("congestion_control_queues_k1.backlog_",congestion_control_queues_k1.backlogs_)
                print("congestion_control_queues_k1.throughput_",congestion_control_queues_k1.Dequeue_th_)
                print("congestion_control_queues_k1.pkt_drop_",congestion_control_queues_k1.pkt_drop_)
                print("****")
                print("congestion_control_queues_k2.backlog_",congestion_control_queues_k2.backlogs_)
                print("congestion_control_queues_k2.throughput_",congestion_control_queues_k2.Dequeue_th_)
                print("congestion_control_queues_k2.pkt_drop_",congestion_control_queues_k2.pkt_drop_)
                print("****")
                print("congestion_control_queues_k3.backlog_",congestion_control_queues_k3.backlogs_)
                print("congestion_control_queues_k3.throughput_",congestion_control_queues_k3.Dequeue_th_)
                print("congestion_control_queues_k3.pkt_drop_",congestion_control_queues_k3.pkt_drop_)
                print("--------------------------------------------------",)
        

if __name__ == "__main__":
    mec_server()
