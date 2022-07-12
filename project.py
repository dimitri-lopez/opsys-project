#!/usr/bin/env python3

# Pretty sure the random number generators are borked (very much so). They should be good
# enough for the time being though.

# Example usage from command line:
# python project.py 1 19 0.01 4096 4 0.5 64
#
# Piping into a file example:
# python project.py 1 19 0.01 4096 4 0.5 64 > output02-full.txt

import sys
import os
import math

# project import
from rand48 import *
from process import *

POSSIBLE_IDS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

def main():
    assert(len(sys.argv) == 8)
    n = int(sys.argv[1]);
    assert(1 <= n and n <= 26)
    seed = int(sys.argv[2]);
    l = float(sys.argv[3])
    upper_bound = float(sys.argv[4])
    tcs = int(sys.argv[5])
    alpha = float(sys.argv[6]) # I still don't really know what this one does...
    tslice = int(sys.argv[7])

    print("Read in arguments")

    # the pdf says to "reset" the simulation after each method and regenerate stuff.
    # I don't think generating the processes again is really needed, but we will see
    processes = generate_processes(n, seed, l, upper_bound)
    for i in processes:
        print(i)
    fcfs(processes, tcs)
    processes = generate_processes(n, seed, l, upper_bound)
    srt(processes, tcs, alpha)
    processes = generate_processes(n, seed, l, upper_bound)
    sjf(processes, tcs, alpha)
    processes = generate_processes(n, seed, l, upper_bound)
    rr(processes, tcs, tslice)
    print("Finished simulation.")

def fcfs(processes, tcs): # TODO FCFS
    # sort based on arrival time
    pass
def srt(processes, tcs, alpha): # TODO SRT
    pass
def sjf(processes, tcs, alpha): # TODO SJF
    pass
def rr(processes, tcs, tslice): # TODO RR
    pass


# Exponential Distribution
def next_exp(l, upper_bound):
    num = upper_bound + 1
    while math.ceil(num) > upper_bound: # skip the super high values
        r = drand48()
        num = -1 * math.log(r) / l
    return math.ceil(num)

# TODO Really not sure what is supposed to be here tbh. Or if it is even needed?
# See project.pdf for argv[6]
def get_cpu_burst_time(alpha):
    pass


def generate_processes(n, seed, l, upper_bound):
    processes = []
    # Seed the random bit generator
    srand48(seed)
    for i in range(n): # produce n processes
        pid = POSSIBLE_IDS[i]
        arrival_time = math.floor(next_exp(l, upper_bound)) # step 1
        cpu_bursts = math.ceil(drand48() * 100) # step 2
        burst_times = []
        io_times = []
        for j in range(cpu_bursts): # step 3
            burst_time = next_exp(l, upper_bound)
            burst_times.append(burst_time)
            if j == cpu_bursts - 1: continue # don't generate io_time for last burst
            io_time = next_exp(l, upper_bound) * 10
            io_times.append(io_time)
        p = Process(pid, arrival_time, cpu_bursts, burst_times, io_times, l)
        processes.append(p)
    return processes

if __name__ == '__main__':
    main()
