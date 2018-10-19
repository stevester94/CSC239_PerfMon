#!/usr/bin/python
from time import sleep

from Tkinter import *

master = Tk()

def button_cb():
    print "click!"
    print listbox.curselection()

def timer_cb():
    pass    

b = Button(master, text="OK", command=button_cb)
c = Button(master, text="No!", command=button_cb)
b.pack()
c.pack()

listbox = Listbox(master)
listbox.pack()

listbox.insert(END, "a list entry")

for item in ["one", "two", "three", "four"]:
    listbox.insert(END, item)

print dir(listbox)
print
print listbox.curselection()

mainloop()

counter = 0
while True:
    listbox.insert(END, str(counter))
    counter = counter + 1
    print "Added"
    sleep(1)

