#!/usr/bin/env python3

class Process():
    def __init__(self, pid, arrival_time, cpu_bursts, burst_times, io_times):
        self.pid = pid                   # A-Z
        self.arrival_time = arrival_time # in miliseconds
        self.cpu_bursts = cpu_bursts     # number of bursts
        self.burst_times = burst_times   # how long each burst is
        self.io_times = io_times         # how long each IO is
