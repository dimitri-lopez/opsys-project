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
from c_queue import *

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
    rr(processes, tcs, tslice, n)
    print("Finished simulation.")

def sort_by_arrival(processes):
    processes.sort(key=lambda x: x.arrival_time)
    return processes

def sort_io(processes):
    processes.sort(key=lambda x: x.curr_io)
    return processes

def fcfs(processes, tcs): # TODO FCFS
    # sort based on arrival time
    pass
def srt(processes, tcs, alpha): # TODO SRT
    pass
def sjf(processes, tcs, alpha): # TODO SJF
    pass
def rr(processes, tcs, tslice, n): # TODO RR
    time = 0
    queue = Queue()
    io_block = []
    finished = 0
    print(f"time {time}ms: Simulator started for RR with time slice {tslice}ms {queue}")
    process_queue = sort_by_arrival(processes)
    i = 0
    curr_p = process_queue[i]
    i += 1
    time += curr_p.arrival_time
    queue.append(curr_p)
    print(f"time {time}ms: Process {curr_p.pid} arrived; added to ready queue {queue}")
    time += (tcs / 2)
    curr_p = queue.pop(0)
    next_p = None
    print(f"time {time}ms: Process {curr_p.pid} started using the CPU for {curr_p.burst_times[0]}ms burst {queue}")

    while finished < n:
        next_io = 2 ** 30
        next_arrival = 2 ** 30
        # check if there is a process in I/O block
        if len(io_block) > 0:
            next_io = io_block[0].curr_io

        # check if there is a process waiting to arrive
        if i < n:
            next_p = process_queue[i]
            next_arrival = next_p.arrival_time

        # check if the CPU isn't being used
        if curr_p is None:
            # check if queue is empty
            if queue.is_empty():
                # find next process that gets added to the queue and add it
                if next_arrival < next_io:
                    time = next_arrival
                    queue.append(next_p)
                    print(f"time {time}ms: Process {next_p.pid} arrived; added to ready queue {queue}")
                    i += 1
                elif next_io < next_arrival:
                    time = next_io
                    io_p = io_block.pop(0)
                    io_p.reset_curr_io()
                    queue.append(io_p)
                    print(f"time {time}ms: Process {io_p.pid} completed I/O; added to ready queue {queue}")
                else:
                    if next_p.pid < io_block[0].pid:
                        time = next_arrival
                        queue.append(next_p)
                        print(f"time {time}ms: Process {next_p.pid} arrived; added to ready queue {queue}")
                    else:
                        time = next_io
                        queue.append(io_block.pop(0))
                        print(f"time {time}ms: Process {io_p.pid} completed I/O; added to ready queue {queue}")
            # now move the process from queue to CPU
            time += (tcs / 2)
            curr_p = queue.pop(0)
            # check to see if the current burst is already underway
            current_burst_initial_time = curr_p.burst_times[curr_p.cpu_bursts - curr_p.remaining_bursts]
            if curr_p.curr_burst < current_burst_initial_time:
                print(
                    f"time {time}ms: Process {curr_p.pid} started using the CPU for remaining {curr_p.curr_burst}ms of {current_burst_initial_time}ms burst {queue}")
            else:
                print(
                    f"time {time}ms: Process {curr_p.pid} started using the CPU for {curr_p.curr_burst}ms burst {queue}")


        # Now the CPU is being used, 4 things can happen: I/O ends, next process arrives, tslice, or burst ends
        next_tslice = time + tslice
        next_burst = time + curr_p.curr_burst
        next_io = 2 ** 30
        next_arrival = 2 ** 30

        # check if there is a process in I/O block
        if len(io_block) > 0:
            next_io = io_block[0].curr_io

        # check if there is a process waiting to arrive
        if i < n:
            next_p = process_queue[i]
            next_arrival = next_p.arrival_time

        #
        ######### next process arrives #################
        if next_arrival < next_tslice and next_arrival < next_burst and next_arrival < next_io:
            queue.append(next_p)
            next_p = processes[i]
            i += 1
            print(f"time {next_p.arrival_time}ms: Process {next_p.pid} arrived; added to ready queue {queue}")

        ###### I/O block process completes #######
        elif next_io < next_arrival and next_io < next_burst and next_io < next_tslice:
            io_process = io_block.pop(0)
            queue.append(io_process)
            print(f"time {next_io}ms: Process {io_process.pid} completed I/O; added to ready queue {queue}")

        ################# time slice happens ###################################
        elif next_tslice < next_arrival and next_tslice < next_burst and next_tslice < next_io:
            time += tslice
            curr_p.curr_burst -= tslice
            if queue.is_empty():
                print(f"time {time}ms: Time slice expired; no preemption because ready queue is empty {queue}")
            else:
                # switch to the next process in the queue
                print(f"time {time}ms: Time slice expired; process {curr_p.pid} preempted with {curr_p.curr_burst}ms remaining {queue}")
                time += (tcs / 2)       # switching out current process
                queue.append(curr_p)
                time += (tcs / 2)       # switching in next process
                curr_p = queue.pop(0)

                # check to see if the current burst is already underway
                current_burst_initial_time = curr_p.burst_times[curr_p.cpu_bursts - curr_p.remaining_bursts]
                if curr_p.curr_burst < current_burst_initial_time:
                    print(f"time {time}ms: Process {curr_p.pid} started using the CPU for remaining {curr_p.curr_burst}ms of {current_burst_initial_time}ms burst {queue}")
                else:
                    print(f"time {time}ms: Process {curr_p.pid} started using the CPU for {curr_p.curr_burst}ms burst {queue}")

        ####### current process finishes CPU burst and before next process is added and before tslice is up ######
        else:
            time += curr_p.curr_burst
            curr_p.remaining_bursts -= 1

            # check to see if process terminated
            if curr_p.remaining_bursts == 0:
                print(f"time {time}ms: Process {curr_p.pid} terminated {queue}")
                finished += 1
                curr_p.set_finish_time(time)
                time += int(tcs/2)   # remove process from CPU
                curr_p = None           # CPU has no process being run

            else:
                curr_p.reset_curr_burst()
                print(f"time {time}ms: Process {curr_p.pid} completed a CPU burst; {curr_p.remaining_bursts} bursts to go {queue}")
                print(f"time {time}ms: Process {curr_p.pid} switching out of CPU; ", end="")
                time += int(tcs/2)
                curr_p.set_io_exit(time)
                print(f"will block on I/O until time {curr_p.curr_io}ms {queue}")
                io_block.append(curr_p)
                io_block = sort_io(io_block)
                curr_p = None

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
