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
from queue import PriorityQueue

# project import
from rand48 import *
from process import *
from c_queue import *

POSSIBLE_IDS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DEBUG_TIME = 1000

def main():
    assert(len(sys.argv) >= 8)
    n = int(sys.argv[1]);
    assert(1 <= n and n <= 26)
    seed = int(sys.argv[2]);
    l = float(sys.argv[3])
    upper_bound = float(sys.argv[4])
    tcs = int(sys.argv[5])     # context switch
    alpha = float(sys.argv[6]) # used to calculate new tau's
    tslice = int(sys.argv[7])
    global DEBUG_TIME
    DEBUG_TIME = 1000
    if len(sys.argv) == 9 and sys.argv[8] == 'debug': DEBUG_TIME = 2<<31

    # print("Read in arguments")
    simout = open("simout.txt", "a")
    # the pdf says to "reset" the simulation after each method and regenerate stuff.
    # I don't think generating the processes again is really needed, but we will see
    processes = generate_processes(n, seed, l, upper_bound)
    for i in processes:
        print(i)
    print("\ntime 0ms: Simulator started for FCFS [Q: empty]")
    fcfs_return = fcfs(processes, tcs, n)
    print_fcfs(fcfs_return)
    print(f"time {fcfs_return[0]}ms: Simulator ended for FCFS [Q: empty]\n")
    processes = generate_processes(n, seed, l, upper_bound)
    sjf(processes, tcs, alpha)
    processes = generate_processes(n, seed, l, upper_bound)
    srt(processes, tcs, alpha)
    processes = generate_processes(n, seed, l, upper_bound)
    print(f"time 0ms: Simulator started for RR with time slice {tslice}ms [Q: empty]")
    rr_return = rr(processes, tcs, tslice, n)
    print_rr(rr_return)
    print(f"time {rr_return[0]}ms: Simulator ended for RR [Q: empty]")

def print_fcfs(fcfs_return):
    # return [time, avg_burst_time, avg_wait_time, avg_ta_time, context_switches, preemptions, cpu_utilization]
    #            0               1              2            3                 4            5                6
    simout = open("simout.txt", "w")
    simout.write(f"Algorithm FCFS\n")
    simout.close()
    simout = open("simout.txt", "a")
    simout.write(f"-- average CPU burst time: {fcfs_return[1] :.3f} ms\n")
    simout.write(f"-- average wait time: {fcfs_return[2] :.3f} ms\n")
    simout.write(f"-- average turnaround time: {fcfs_return[3] :.3f} ms\n")
    simout.write(f"-- total number of context switches: {fcfs_return[4]}\n")
    simout.write(f"-- total number of preemptions: {fcfs_return[5]}\n")
    simout.write(f"-- CPU utilization: {fcfs_return[6] :.3f}%\n")
    simout.close()



def print_rr(rr_return):
    # return [time, avg_burst_time, avg_wait_time, avg_ta_time, context_switches, preemptions, cpu_utilization]
    #            0               1              2            3                 4            5                6
    simout = open("simout.txt", "a")
    simout.write(f"Algorithm RR\n")
    simout.write(f"-- average CPU burst time: {rr_return[1] :.3f} ms\n")
    simout.write(f"-- average wait time: {rr_return[2] :.3f} ms\n")
    simout.write(f"-- average turnaround time: {rr_return[3] :.3f} ms\n")
    simout.write(f"-- total number of context switches: {rr_return[4]}\n")
    simout.write(f"-- total number of preemptions: {rr_return[5]}\n")
    simout.write(f"-- CPU utilization: {rr_return[6] :.3f}%\n")
    simout.close()


def sort_by_arrival(processes):
    processes.sort(key=lambda x: x.arrival_time)
    return processes

def sort_by_next_burst(processes):
    processes.sort(key=lambda x: x.curr_burst)
    return processes

def sort_io(processes):
    processes.sort(key=lambda x: x.curr_io)
    return processes

def fcfs(processes, tcs, n):
    # call RR with an infinite tslice
    time = rr(processes, tcs, 2**31-1, n)
    return time

def sjf(processes, tcs, alpha):
    # based on shortest anticipated CPU burst time
    events = SortedQueue(None) # Will store all the events
    rqueue = SortedQueue(lambda process: (process.tau, process.pid)) # this will be our ready queue

    # Place arrival times in events
    for p in processes:
        events.add(Event(p, 0, p.arrival_time, Event.ARRIVAL))

    time = 0
    in_use = False # whether or not the CPU is in use

    # STAT COLLECTIONS
    context_switches = 0 # incremented at the start of every context switch
    burst_times = []     # collects the amount of time that each burst runs for
    cpu_running = 0      # the total amount of time the cpu was running

    print(f"time {time}ms: Simulator started for SJF {rqueue}")
    while events.size() != 0 or rqueue.size () != 0: # run until out of events
        # cpu not in use, start a new process
        if time != events.get_next_time() and not in_use and rqueue.size() != 0:
            process = rqueue.pop()
            events.add(Event(process, time, math.ceil(tcs / 2), Event.CS_IN)) # add half a context switch
            process.set_queue_exit(time)
            process.started_burst(time) # TODO
            in_use = True # TODO
            continue

        event = events.pop()     # get the next event
        time = event.get_time()  # get the new time
        process = event.process  # get the current process

        if   event.etype == Event.ARRIVAL:  # a process has arrived
            rqueue.add(process)
            process.set_queue_entry(time) # Set queue entry time, used for gettting the total amount of waiting time
            process.set_ta_entry(time)
            if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} arrived; added to ready queue {rqueue}")

        elif event.etype == Event.IO: # a process finished IO blocking, enters the ready queue
            rqueue.add(process)
            process.set_queue_entry(time) # Set queue entry time, used for gettting the total amount of waiting time
            process.set_ta_entry(time)
            if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} completed I/O; added to ready queue {rqueue}")

        elif event.etype == Event.CS_IN: # the process has finished being loaded into the CPU
            burst_time = process.run_burst()
            events.add(Event(process, time, burst_time, Event.CPU_BURST_END))
            if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} started using the CPU for {burst_time}ms burst {rqueue}")

            context_switches += 1 # STATS
        elif event.etype == Event.CPU_BURST_END: # the process finished its cpu burst
            cpu_running += event.time # STATS
            burst_times.append(event.time) # STATS
            process.set_ta_exit(time + math.ceil(tcs / 2)) # STATS
            if process.rbursts() == 0: # process finished its last CPU burst
                print(f"time {time}ms: Process {process.pid} terminated {rqueue}") # always gets printed
                events.add(Event(process, time, math.ceil(tcs / 2), Event.CS_OUT)) # switch out of cpu
                process.set_finish_time(time) # process has finished
                continue

            plural = "s" if process.rbursts() > 1 else ""
            if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} completed a CPU burst; {process.rbursts()} burst{plural} to go {rqueue}")

            # Calculating new tau
            old_tau, new_tau = process.calc_new_tau(time, alpha, event.time)
            if time < DEBUG_TIME: print(f"time {time}ms: Recalculated tau for process {process.pid}: old tau {old_tau}ms; new tau {new_tau}ms {rqueue}")

            # Switching out of the CPU
            io_time = process.run_io() + math.ceil(tcs / 2) # adding in an end context switch
            events.add(Event(process, time, io_time, Event.IO))
            if time < DEBUG_TIME: print(f"time {time}ms: Process {process.pid} switching out of CPU; will block on I/O until time {time + io_time}ms {rqueue}")

            events.add(Event(process, time, math.ceil(tcs / 2), Event.CS_OUT)) # move process out of CPU
        elif event.etype == Event.CS_OUT: # the process is being moved out of the CPU
            in_use = False # cpu no longer being used

    print(f"time {time}ms: Simulator ended for SJF {rqueue}\n")

    # Statistics Calculations
    simout = open("simout.txt", "a")
    simout.write(f"Algorithm SJF\n")
    simout.write(f"-- average CPU burst time: {mean3(burst_times) :.3f} ms\n")
    wait_times = []
    for i in processes: wait_times += i.get_all_wait_times()
    simout.write(f"-- average wait time: {mean3(wait_times) :.3f} ms\n")
    ta_times = []
    for i in processes: ta_times += i.get_ta_times()
    simout.write(f"-- average turnaround time: {mean3(ta_times) :.3f} ms\n")
    simout.write(f"-- total number of context switches: {context_switches}\n")
    simout.write(f"-- total number of preemptions: 0\n")
    simout.write(f"-- CPU utilization: {round3(cpu_running / time * 100) :.3f}%\n")
    simout.close()



    return time

def mean3(nums):
    return round3(mean(nums))
def round3(num):
    return math.ceil(num * 1000) / 1000
def mean(nums):
    total = 0
    for i in nums: total += i
    if len(nums) > 0:
        return total / len(nums)
    else:
        return 0

def event_print(time, string):
    DEBUG = DEBUG_TIME
    if time < DEBUG: print(string)
# processes, tcs, alpha, time, context_switches, preemptions

def find_current_burst(events):
    for index, event in enumerate(events.queue):
        if event.etype == Event.CPU_BURST_END:
            return index
    return -1


def srt_preemption_check(time, process, events):
    ievent = find_current_burst(events)
    if ievent == -1: return (False, None)
    event = events.pop(ievent)

    # eprocess_full_burst_time = process.get_full_burst_time()
    # eprocess_remaining_time = event.time
    # eprocess_running_time = eprocess_full_burst_time - eprocess_remaining_time
    # previous_times = event.process.get_other_burst_time() - event.time

    time_ran = time - event.start
    remaining_time = event.process.remaining_tau - time_ran
    # print(f"\t burst process {event.process.sprint()}, remaining_tau: {event.process.remaining_tau} remaining_time: {remaining_time}")
    # print(f"\treplacing process {process.sprint()} remainig_tau: {process.remaining_tau}")
    # print(f"\t CPU BURST process: {process.sprint()} time: {time} burst: {event}")

    if process.remaining_tau < remaining_time:
        # print(f"\t process.tau: {process.tau} remaining_time: {remaining_time}")
        # print(f"\t FOUND A PREEMPTION process: {process.sprint()} time: {time} burst: {event} remaining_time: {remaining_time}")
        # print(f"\t FOUND A PREEMPTION process: {process.sprint()} time: {time} burst: {event} remaining_time: {remaining_time}")
        return (True, event)

    events.add(event)

    return (False, None)

def srt(processes, tcs, alpha):
    # based on shortest anticipated CPU burst time
    events = SortedQueue(None) # Will store all the events
    rqueue = SortedQueue(lambda process: (process.remaining_tau, process.pid)) # this will be our ready queue

    # Place arrival times in events
    for p in processes:
        events.add(Event(p, 0, p.arrival_time, Event.ARRIVAL))

    time = 0
    in_use = False # whether or not the CPU is in use

    # STAT COLLECTIONS
    context_switches = 0 # incremented at the start of every context switch
    burst_times = []     # collects the amount of time that each burst runs for
    cpu_running = 0      # the total amount of time the cpu was running
    preemptions = 0      # total number of preemptions

    print(f"time {time}ms: Simulator started for SRT {rqueue}")
    # preemptions happen whenever a process enters the queue
    while events.size() != 0 or rqueue.size () != 0: # run until out of events
        # cpu not in use, start a new process
        if time != events.get_next_time() and not in_use and rqueue.size() != 0:
            process = rqueue.pop()
            if process.was_preempted == True:
                events.add(Event(process, time, math.ceil(tcs / 2), Event.PCS_IN)) # add half a context switch
            else:
                events.add(Event(process, time, math.ceil(tcs / 2), Event.CS_IN)) # add half a context switch
                process.set_queue_exit(time) # STATS
                process.started_burst(time)
            in_use = True
            continue

        event = events.pop()     # get the next event
        time = event.get_time()  # get the new time
        process = event.process  # get the current process

        if   event.etype == Event.ARRIVAL: # a process has arrived
            rqueue.add(process)
            process.set_queue_entry(time) # Set queue entry time, used for getting the total waiting time
            process.set_ta_entry(time)
            preemption, pevent = srt_preemption_check(time, process, events)
            if not preemption:
                if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} arrived; added to ready queue {rqueue}")
            else: # TODO DO PREMPTION CHECK HERE
                preemptions += 1
                if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} completed I/O; preempting {pevent.process.pid} {rqueue}")

                # add back the cpu burst?
                time_bursted = time - pevent.start
                pevent.process.add_peemp()
                pevent.process.preempted()
                pevent.process.burst_times.insert(0, pevent.time - time_bursted)
                # schedule cs_end
                events.add(Event(pevent.process, time, math.ceil(tcs / 2), Event.CS_OUT))
                events.add(Event(pevent.process, time, math.ceil(tcs / 2), Event.PREEMPT_QADD))
                pevent.process.update_remaining_tau(time_bursted)
        elif event.etype == Event.PREEMPT_QADD:
            rqueue.add(process)
            process.set_queue_entry(time) # Set queue entry time, used for getting the total waiting time
            process.set_ta_entry(time)

        elif event.etype == Event.IO: # a process finished IO blocking, enters the ready queue
            rqueue.add(process)
            process.set_queue_entry(time) # Set queue entry time, used for gettting the total amount of waiting time
            process.set_ta_entry(time)

            # TODO DO PREMPTION CHECK HERE
            preemption, pevent = srt_preemption_check(time, process, events)
            if not preemption:
                if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} completed I/O; added to ready queue {rqueue}")
            else:
                preemptions += 1
                if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} completed I/O; preempting {pevent.process.pid} {rqueue}")

                # add back the cpu burst?
                time_bursted = time - pevent.start
                pevent.process.add_peemp()
                pevent.process.preempted()
                pevent.process.burst_times.insert(0, pevent.time - time_bursted)
                # schedule cs_end
                events.add(Event(pevent.process, time, math.ceil(tcs / 2), Event.CS_OUT))
                events.add(Event(pevent.process, time, math.ceil(tcs / 2), Event.PREEMPT_QADD))
                pevent.process.update_remaining_tau(time_bursted)
        elif event.etype == Event.CS_IN: # the process has finished being loaded into the CPU
            burst_time = process.run_burst()
            events.add(Event(process, time, burst_time, Event.CPU_BURST_END))
            context_switches += 1 # STATS
            if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} started using the CPU for {burst_time}ms burst {rqueue}")

            preemption = False
            if rqueue.size() != 0:
                preemption, pevent = srt_preemption_check(time, rqueue[0], events)
            if preemption:
                preemptions += 1
                if time < DEBUG_TIME: print(f"time {time}ms: {rqueue[0].sprint()} will preempt {process.pid} {rqueue}")

                # add back the cpu burst?
                time_bursted = time - pevent.start
                pevent.process.add_peemp()
                pevent.process.preempted()
                pevent.process.burst_times.insert(0, pevent.time - time_bursted)
                # schedule cs_end
                events.add(Event(pevent.process, time, math.ceil(tcs / 2), Event.CS_OUT))
                events.add(Event(pevent.process, time, math.ceil(tcs / 2), Event.PREEMPT_QADD))
                pevent.process.update_remaining_tau(time_bursted)

        elif event.etype == Event.PCS_IN:
            full_burst_time = process.get_full_burst_time()
            remaining_time = process.run_burst()
            events.add(Event(process, time, remaining_time, Event.CPU_BURST_END)) # TODO Last line written
            context_switches += 1 # STATS
            if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} started using the CPU for remaining {remaining_time}ms of {full_burst_time}ms burst {rqueue}")
            preemption = False
            if rqueue.size() != 0:
                preemption, pevent = srt_preemption_check(time, rqueue[0], events)
            if preemption:
                preemptions += 1
                if time < DEBUG_TIME: print(f"time {time}ms: {rqueue[0].sprint()} will preempt {process.pid} {rqueue}")

                # add back the cpu burst?
                time_bursted = time - pevent.start
                pevent.process.add_peemp()
                pevent.process.preempted()
                pevent.process.burst_times.insert(0, pevent.time - time_bursted)
                # schedule cs_end
                events.add(Event(pevent.process, time, math.ceil(tcs / 2), Event.CS_OUT))
                events.add(Event(pevent.process, time, math.ceil(tcs / 2), Event.PREEMPT_QADD))
                pevent.process.update_remaining_tau(time_bursted)

        elif event.etype == Event.CPU_BURST_END: # the process finished its cpu burst
            cpu_running += event.time # STATS
            burst_times.append(event.time) # STATS
            process.set_ta_exit(time + math.ceil(tcs / 2)) # STATS
            if process.rbursts() == 0:
                print(f"time {time}ms: Process {process.pid} terminated {rqueue}")
                # Context switch to switch out of the CPU
                events.add(Event(process, time, math.ceil(tcs / 2), Event.CS_OUT))
                process.set_finish_time(time)
                continue

            plural = "s" if process.rbursts() > 1 else ""
            if time < DEBUG_TIME: print(f"time {time}ms: {process.sprint()} completed a CPU burst; {process.rbursts()} burst{plural} to go {rqueue}")

            # Calculating new tau
            old_tau, new_tau = process.calc_new_tau(time, alpha)
            if time < DEBUG_TIME: print(f"time {time}ms: Recalculated tau for process {process.pid}: old tau {old_tau}ms; new tau {new_tau}ms {rqueue}")

            # Switching out of the CPU
            io_time = process.run_io() + math.ceil(tcs / 2) # adding in an end context switch
            events.add(Event(process, time, io_time, Event.IO))
            if time < DEBUG_TIME: print(f"time {time}ms: Process {process.pid} switching out of CPU; will block on I/O until time {time + io_time}ms {rqueue}")

            events.add(Event(process, time, math.ceil(tcs / 2), Event.CS_OUT)) # move process out of CPU
        elif event.etype == Event.CS_OUT:
            in_use = False

    print(f"time {time}ms: Simulator ended for SRT {rqueue}\n")

    simout = open("simout.txt", "a")
    simout.write(f"Algorithm SRT\n")
    simout.write(f"-- average CPU burst time: {mean3(burst_times) :.3f} ms\n") # DONE
    wait_times = []
    for i in processes: wait_times += i.get_all_wait_times()
    simout.write(f"-- average wait time: {mean3(wait_times) :.3f} ms\n") # DONE?
    ta_times = []
    for i in processes: ta_times += i.get_ta_times()
    simout.write(f"-- average turnaround time: {mean3(ta_times) :.3f} ms\n") # TODO
    simout.write(f"-- total number of context switches: {context_switches}\n") # DONE
    simout.write(f"-- total number of preemptions: {preemptions}\n") # DONE
    simout.write(f"-- CPU utilization: {round3(cpu_running / time * 100) :.3f}%\n") # DONE
    simout.close()


    return time

    pass

def rr(processes, tcs, tslice, n):
    time = 0
    cpu_use_time = 0
    context_switches = 0
    preemptions = 0
    burst_times = []
    queue = Queue()
    io_block = []
    finished = 0
    process_queue = sort_by_arrival(processes)
    i = 0
    curr_p = process_queue[i]
    i += 1
    time += curr_p.arrival_time
    curr_p.set_ta_entry(time)
    queue.append(curr_p)
    print(f"time {time}ms: Process {curr_p.pid} arrived; added to ready queue {queue}")
    curr_p = queue.pop(0)   # remove process from queue
    time += int(tcs / 2)    # add process to CPU
    context_switches += 1   # STATS
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
                    next_p.set_ta_entry(time)
                    next_p.set_queue_entry(time)
                    queue.append(next_p)
                    if time < DEBUG_TIME: print(f"time {time}ms: Process {next_p.pid} arrived; added to ready queue {queue}")
                    i += 1
                elif next_io < next_arrival:
                    time = next_io
                    io_p = io_block.pop(0)
                    io_p.reset_curr_io()
                    io_p.set_ta_entry(time)
                    io_p.set_queue_entry(time)
                    queue.append(io_p)
                    if time < DEBUG_TIME: print(f"time {time}ms: Process {io_p.pid} completed I/O; added to ready queue {queue}")
                # check if there is a tie
                else:
                    if next_p.pid < io_block[0].pid:
                        time = next_arrival
                        next_p.set_ta_entry(time)
                        next_p.set_queue_entry(time)
                        queue.append(next_p)
                        if time < DEBUG_TIME: print(f"time {time}ms: Process {next_p.pid} arrived; added to ready queue {queue}")
                    else:
                        time = next_io
                        io_p.set_ta_entry(time)
                        io_p.set_queue_entry(time)
                        queue.append(io_block.pop(0))
                        if time < DEBUG_TIME: print(f"time {time}ms: Process {io_p.pid} completed I/O; added to ready queue {queue}")
            # now move the process from queue to CPU
            curr_p = queue.pop(0)
            curr_p.set_queue_exit(time)
            time += int(tcs / 2)
            context_switches += 1
            # check to see if the current burst is already underway
            current_burst_initial_time = curr_p.burst_times[curr_p.cpu_bursts - curr_p.remaining_bursts]
            if curr_p.curr_burst < current_burst_initial_time:
                if time < DEBUG_TIME: print(f"time {time}ms: Process {curr_p.pid} started using the CPU for remaining {curr_p.curr_burst}ms of {current_burst_initial_time}ms burst {queue}")
            else:
                if time < DEBUG_TIME: print(f"time {time}ms: Process {curr_p.pid} started using the CPU for {curr_p.curr_burst}ms burst {queue}")




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
            next_p.set_queue_entry(next_arrival)
            next_p.set_ta_entry(next_arrival)
            queue.append(next_p)
            next_p = processes[i]
            i += 1
            if time < DEBUG_TIME: print(f"time {next_arrival}ms: Process {next_p.pid} arrived; added to ready queue {queue}")

        ###### I/O block process completes #######
        elif next_io < next_arrival and next_io < next_burst and next_io < next_tslice:
            io_process = io_block.pop(0)
            io_process.set_queue_entry(next_io)
            next_p.set_ta_entry(next_io)
            queue.append(io_process)
            if time < DEBUG_TIME: print(f"time {next_io}ms: Process {io_process.pid} completed I/O; added to ready queue {queue}")

        ################# time slice happens ###################################
        elif next_tslice < next_arrival and next_tslice < next_burst and next_tslice < next_io:
            time += tslice
            cpu_use_time += tslice
            curr_p.curr_burst -= tslice
            if queue.is_empty():
                if time < DEBUG_TIME: print(f"time {time}ms: Time slice expired; no preemption because ready queue is empty {queue}")
            else:
                # switch to the next process in the queue
                if time < DEBUG_TIME: print(f"time {time}ms: Time slice expired; process {curr_p.pid} preempted with {curr_p.curr_burst}ms remaining {queue}")
                time += int(tcs / 2)       # switching out current process
                context_switches += 1
                preemptions += 1
                curr_p.set_queue_entry(time)
                queue.append(curr_p)
                curr_p = queue.pop(0)       # load up next process
                curr_p.set_queue_exit(time) # end wait time counter
                time += int(tcs / 2)       # switching in next process

                # check to see if the current burst is already underway
                current_burst_initial_time = curr_p.burst_times[curr_p.cpu_bursts - curr_p.remaining_bursts]
                if curr_p.curr_burst < current_burst_initial_time:
                    if time < DEBUG_TIME: print(f"time {time}ms: Process {curr_p.pid} started using the CPU for remaining {curr_p.curr_burst}ms of {current_burst_initial_time}ms burst {queue}")
                else:
                    if time < DEBUG_TIME: print(f"time {time}ms: Process {curr_p.pid} started using the CPU for {curr_p.curr_burst}ms burst {queue}")

        ####### current process finishes CPU burst and before next process is added and before tslice is up ######
        else:
            current_burst_initial_time = curr_p.burst_times[curr_p.cpu_bursts - curr_p.remaining_bursts]
            burst_times.append(current_burst_initial_time)
            time += curr_p.curr_burst
            cpu_use_time += curr_p.curr_burst
            exit_time = time+int(tcs/2)
            curr_p.set_ta_exit(exit_time)
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

                plural = "" if curr_p.remaining_bursts == 1 else "s"
                if time < DEBUG_TIME: print(f"time {time}ms: Process {curr_p.pid} completed a CPU burst; {curr_p.remaining_bursts} burst{plural} to go {queue}")
                if time < DEBUG_TIME: print(f"time {time}ms: Process {curr_p.pid} switching out of CPU; ", end="")
                time += int(tcs/2)
                curr_p.set_io_exit(time)
                if time < DEBUG_TIME: print(f"will block on I/O until time {curr_p.curr_io}ms {queue}")
                io_block.append(curr_p)
                io_block = sort_io(io_block)
                curr_p = None

    # print(f"-- average CPU burst time: {mean3(burst_times) :.3f} ms")
    avg_burst_time = mean3(burst_times)
    wait_times = []
    for i in processes: wait_times += i.get_all_wait_times()
    # print(f"-- average wait time: {mean3(total_wait_time) :.3f} ms")
    avg_wait_time = mean3(wait_times)
    ta_times = []
    for i in processes:
        ta_times += i.get_ta_times()
    # print(f"-- average turnaround time: {mean3(ta_times) :.3f} ms")
    avg_ta_time = mean3(ta_times)
    # print(f"-- total number of context switches: {context_switches}")
    # print(f"-- total number of preemptions: {preemptions}")
    # print(f"-- CPU utilization: {round3(cpu_use_time / time * 100) :.3f}%")
    cpu_utilization = round3(cpu_use_time / time * 100)

    return [time, avg_burst_time, avg_wait_time, avg_ta_time, context_switches, preemptions, cpu_utilization]


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
        arrival_time = math.floor(next_exp(l, upper_bound)) - 1 # step 1 #TODO not sure why there is a -1 here...
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
