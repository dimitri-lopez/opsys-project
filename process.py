#!/usr/bin/env python3

import math

class Process():
    def __init__(self, pid, arrival_time, cpu_bursts, burst_times, io_times, l):
        self.pid = pid                   # A-Z
        self.arrival_time = arrival_time # in miliseconds
        self.cpu_bursts = cpu_bursts     # number of bursts
        self.burst_times = burst_times   # how long each burst is
        self.io_times = io_times         # how long each IO is
        self.tau = math.ceil(1 / l)      # Initial tau value
        self.finish = None               # Finish time for the process
        self.curr_burst = burst_times[0] # Time left on burst that the process is currently on
        self.num_cs = 0                  # counts the number of context switches
        self.num_premp = 0               # counts the number of preemptions
        self.ta_times = []               # keeps track of the turnaround time for each cpu burst (indices will match up with burst_times
        self.wait_times = []             # keeps track of the waiting time for each cpu burst (indices will match up with burst_times
        if len(io_times) > 0:
            self.curr_io = io_times[0]   # I/O end time for current burst (time+io_time)

        self.remaining_bursts = self.cpu_bursts

    def set_finish_time(self, time):
        self.finish = time

    def reset_curr_burst(self):
        index = self.cpu_bursts - self.remaining_bursts
        self.curr_burst = self.burst_times[index]

    def set_io_exit(self, time):
        self.curr_io += time

    def reset_curr_io(self):
        index = self.cpu_bursts - self.remaining_bursts
        if index < len(self.io_times):
            self.curr_io = self.io_times[index]

    def run_burst(self):
        return self.burst_times.pop(0)
    def run_io(self):
        return self.io_times.pop(0)
    def rbursts(self):
        return len(self.burst_times)

    def __str__(self):
        string = ""
        string += f"Process {self.pid}: arrival time {self.arrival_time}ms; tau {self.tau}ms; {self.remaining_bursts} CPU bursts:\n"
        for i in range(self.cpu_bursts - 1):
            string += f"--> CPU burst {self.burst_times[i]}ms --> I/O burst {self.io_times[i]}ms\n"
        string += f"--> CPU burst {self.burst_times[-1]}ms"
        return string
    def __repr__(self):
        return self.__str__
    def sprint(self):
        return f"Process {self.pid} (tau {self.tau}ms)"
    def calc_new_tau(self, curr_time, alpha, time):
        old_tau = self.tau
        self.tau = math.ceil(alpha * time + (1 - alpha) * old_tau)
        return[old_tau, self.tau]


    # def reset_process(self):
    #     self.finish = None # prcess hasn't finished
    #     self.tau = self.itau # reset to initial tau value
    #     self.remaining_bursts = self.cpu_bursts

class Event():
    ARRIVAL = "ARRIVAL"
    IO = "IO" # IO COMPLETION
    PREMPTION = "PREMPTION"
    CS_START = "CS_STAT"
    CS_END = "CS_END"
    CPU_BURST_END = "CPU_BURST"

    def __init__(self, process, start, time, etype):
        self.process = process
        self.start = start
        self.time = time
        self.etype = etype
    def __lt__(self, other):
        return self.start + self.time < other.start + other.time
    def __str__(self):
        string = f"EVENT: time: {self.start + self.time} start: {self.start} type: {self.etype}"
        return string
    def __repr__(self):
        return self.__str__()
