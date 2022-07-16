#!/usr/bin/env python3

import math


class Process:
    def __init__(self, pid, arrival_time, cpu_bursts, burst_times, io_times, l):
        self.pid = pid                   # A-Z
        self.arrival_time = arrival_time # in miliseconds
        self.cpu_bursts = cpu_bursts     # number of bursts
        self.burst_times = burst_times   # how long each burst is
        self.oburst_times = burst_times.copy()
        self.num_preemp = 0
        self.io_times = io_times         # how long each IO is
        self.tau = math.ceil(1 / l)      # Initial tau value
        self.finish = None               # Finish time for the process
        self.curr_burst = burst_times[0] # Time left on burst that the process is currently on
        self.wait_times = cpu_bursts*[0] # keeps track of the waiting time for each cpu burst (indices will match up with burst_times
        # self.wait_times = []
        self.ta_times = cpu_bursts*[0]               # keeps track of the turnaround time for each cpu burst (indices will match up with burst_times
        self.sjf_ta_times = []
        self.queue_entry = 0             # keeps track of the time when process enters the queue (for wait time)
        self.ta_entry = 0                # keeps track of the time when the process enters the queue for the first time (for turnaround time)
        self.burst_start = 0             # keep track of time when burst starts
        if len(io_times) > 0:
            self.curr_io = io_times[0]   # I/O end time for current burst (time+io_time)

        self.remaining_bursts = self.cpu_bursts
        self.was_preempted = False
        self.remaining_tau = self.tau

    def get_full_burst_time(self):
        return self.oburst_times [self.cpu_bursts - self.rbursts()]
    def get_other_burst_time(self):
        return self.oburst_times [self.cpu_bursts - self.rbursts() - 1]
    def update_remaining_tau(self, time):
        self.remaining_tau -= time


    def add_context_switch(self):
        self.num_cs += 1

    def preempted(self):
        self.was_preempted = True

    def add_peemp(self):
        self.num_preemp += 1

    def get_index(self):
        self.cpu_bursts - len(self.cpu_bursts)
    def set_ta_entry(self, time):
        self.ta_entry = time

    def set_ta_exit(self, time):
        self.ta_times[self.cpu_bursts - self.remaining_bursts] += (time - self.ta_entry)

    def set_queue_entry(self, time):
        # Gets called everytime a process enters a queue. Used for calculating statistics
        self.queue_entry = time

    def set_queue_exit(self, time):
        # Gets called everytime a process exits a queue. Used for calculating statistics
        self.wait_times[self.cpu_bursts-self.remaining_bursts] += (time-self.queue_entry)
        # self.wait_times.append(time - self.queue_entry)

    def started_burst(self, time):
        self.burst_start = time

    def finished_burst(self, time):
        self.sjf_ta_times.append(time - self.burst_start)

    def get_total_wait_time(self):
        total = 0
        for i in self.wait_times:
            total += i
        return total

    def get_ta_times(self):
        return self.ta_times
    def get_sjf_ta_times(self):
        return self.sjf_ta_times

    def set_finish_time(self, time):
        self.finish = time

    def get_total_time(self):
        assert(self.finish is not None)
        return self.finish - self.arrival_time

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
        self.was_preempted = False
        return self.burst_times.pop(0)

    def run_io(self):
        return self.io_times.pop(0)

    def rbursts(self):
        return len(self.burst_times)

    def __str__(self):
        string = ""
        plural = "s" if self.rbursts() > 1 else ""
        string += f"Process {self.pid}: arrival time {self.arrival_time}ms; tau {self.tau}ms; {self.remaining_bursts} CPU burst{plural}:\n"
        for i in range(self.cpu_bursts - 1):
            string += f"--> CPU burst {self.burst_times[i]}ms --> I/O burst {self.io_times[i]}ms\n"
        string += f"--> CPU burst {self.burst_times[-1]}ms"
        return string

    def __repr__(self):
        return self.__str__

    def sprint(self):
        return f"Process {self.pid} (tau {self.tau}ms)"
    def calc_new_tau(self, curr_time, alpha, time = None):
        if time is None: time = self.oburst_times [self.cpu_bursts - self.rbursts() - 1]
        old_tau = self.tau
        self.tau = math.ceil(alpha * time + (1 - alpha) * old_tau)
        self.remaining_tau = self.tau
        return[old_tau, self.tau]

    # def reset_process(self):
    #     self.finish = None # prcess hasn't finished
    #     self.tau = self.itau # reset to initial tau value
    #     self.remaining_bursts = self.cpu_bursts


class Event:
    CPU_BURST_END = 0
    PCS_IN = 2.10 # TODO Not sure what these values should be
    CS_IN = 2.11 # TODO Not sure what these values should be
    CS_OUT = 2.2
    PREEMPT_QADD = 2.3
    IO = 3 # IO COMPLETION
    ARRIVAL = 4
    # PREMPTION = "PREMPTION"

    def __init__(self, process, start, time, etype):
        self.process = process
        self.start = start
        self.time = time
        self.etype = etype

    def get_time(self):
        return self.start + self.time

    def __lt__(self, other):
        if self.get_time() == other.get_time():
            if self.etype == other.etype: return self.process.pid < other.process.pid
            else: return self.etype < other.etype

        return self.get_time() < other.get_time()

    def __str__(self):
        string = f"EVENT: time: {self.time} start: {self.start} end: {self.get_time()} type: {self.etype} process: {self.process.sprint()}"
        return string

    def __repr__(self):
        return self.__str__()
