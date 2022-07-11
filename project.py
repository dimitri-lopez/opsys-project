#!/usr/bin/env python3

import sys
import os
import rand

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



    

if __name__ == '__main__':
    assert(len(sys.argv) == 6)
    n = int(sys.argv[1]);
    assert(1 <= n and n <= 26)
    seed = int(sys.argv[2]);
    l = float(sys.argv[3])
    upper_bound = float(sys.argv[4])
    tcs = int(sys.argv[5])

    for i in range(n): # produce n processes
        pid = POSSIBLE_IDS[i]
        arrival_time = drand48(l)
        Process(pid, arrival_time)
