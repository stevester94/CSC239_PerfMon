#!/usr/bin/python

import sys
sys.path.append('/home/steven/School/CSC239/CSC239_PerfMon')

from proc import *

import Tkinter as tk
import time

class App():
    def __init__(self):
        self.procs = None
        self.root = tk.Tk()
        self.label = tk.Label(text="")
        self.label.pack()
        self.update_clock()
        self.root.mainloop()

    def update_procs(self):
        new_procs = dictify_procs(get_all_complete_procs())
        if self.procs != None:
            populate_all_proc_utilization_interval_percent(self.procs, new_procs)
        self.procs = new_procs


    def update_clock(self):
        now = time.strftime("%H:%M:%S")
        print "Updating procs"
        self.update_procs()
        self.label.configure(text=now)
        self.root.after(1000, self.update_clock)

app=App()
