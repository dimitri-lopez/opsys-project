#!/usr/bin/env python3
import sys
import os
import * from rand

POSSIBLE_IDS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def fcfs(): # TODO FCFS
    pass
def srt(): # TODO SRT
    pass
def sjf(): # TODO SJF
    pass
def rr(): # TODO RR
    pass

class Process():
    def __init__(self, pid):
        self.pid = pid;
        self.state = pass # TODO


# returns the arrival time in miliseconds
def next_exp(l, upper_bound):
    num = upper_bound + 1
    while ceil(num) > upper_bound: # skip the super highi
        num = ceil(-1 * log( drand48() ) / l)
    return num

def get_cpu_burst_time(tau):
    # TODO use ceiling function

def next_exp():
    pass
    

if __name__ == '__main__':
    assert(len(sys.argv) == 8)
    n = int(sys.argv[1]);
    assert(1 <= n and n <= 26)
    seed = int(sys.argv[2]);
    l = float(sys.argv[3])
    upper_bound = float(sys.argv[4])
    tcs = int(sys.argv[5])
    alpha = int(sys.argv[6])
    tslice = int(sys.argv[7])


    # Seed the random bit generator
    srand48(seed)

    for i in range(n): # produce n processes
        pid = POSSIBLE_IDS[i]
        arrival_time = floor(next_exp(l, upper_bound)) # step 1
        cpu_bursts = ceil(drand48() * 100) # step 2
        for j in range(cpu_bursts): # step 3
            burst_time = next_exp(l, upper_bound)
            if j == cpu_bursts - 1: continue # don't generate io_time for last burst
            io_time = next_exp(l, upper_bound) * 10
        assert(type(cpu_bursts) is int); assert(cpu_bursts >= 0); assert(cpu_bursts <= 100); # TODO just for testing, remove later
        Process(pid, arrival_time)
