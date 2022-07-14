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
        self.curr_io = io_times[0]       # I/O end time for current burst (time+io_time)

        self.remaining_bursts = self.cpu_bursts

    def set_finish_time(self, time):
        self.finish = time

    def reset_curr_burst(self):
        index = self.cpu_bursts - self.remaining_bursts
        self.curr_burst = self.burst_times[index]

    def set_io_exit(self,time):
        self.curr_io += time

    def reset_curr_io(self):
        index = self.cpu_bursts - self.remaining_bursts
        if index < len(self.io_times):
            self.curr_io = self.io_times[index]

    def __str__(self):
        string = ""
        string += f"Process {self.pid}: arrival time {self.arrival_time}ms; tau {self.tau}ms; {self.remaining_bursts} CPU bursts:\n"
        for i in range(self.cpu_bursts - 1):
            string += f"--> CPU burst {self.burst_times[i]}ms --> I/O burst {self.io_times[i]}ms\n"
        string += f"--> CPU burst {self.burst_times[-1]}ms"
        return string
    def __repr__(self):
        string = ""
        string += f"Process {self.pid}: arrival time {self.arrival_time}ms; tau {self.tau}ms; {self.remaining_bursts} CPU bursts:\n"
        for i in range(len(self.cpu_bursts) - 1):
            string += f"--> CPU burst {self.burst_times[i]}ms --> I/O burst {self.io_times[i]}ms\n"
        string += f"--> CPU burst {self.burst_times[-1]}ms"
        return string

    # def reset_process(self):
    #     self.finish = None # prcess hasn't finished
    #     self.tau = self.itau # reset to initial tau value
    #     self.remaining_bursts = self.cpu_bursts

p = Process(1, 1, 2, [1, 2], [1], 1)
print(p)
