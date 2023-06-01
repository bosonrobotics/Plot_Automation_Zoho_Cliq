#!/usr/bin/env python3
# UPdated Year : JAN 2023

import subprocess
import os
from datetime import datetime as dt
import re
import sys


def plotter(to_run):
    for index in range(0,len(to_run),10):
        file = to_run[index:index+10]
        print("Plotting :",file)
        command = [subprocess.Popen(["python3", dir_path+"/route_plot_updated.py", "-b", dir_path+"/"+i]) for i in file]
        for cmd in command:
            cmd.wait()
        print(file)
        print("~-"*45)	
    print("End")
	
no=[]
to_run=[]
pending = []
#For getting the start date that is passed on the plot_automation_cliq.py script
date = sys.argv[1]
print("Date in plot_auto",date)
username = os.getlogin()
dir_path =f"/home/{username}/.bags"

# date=dt.now().strftime("%Y-%m-%d")
#date = date.split("-")
print("Plotting for",date)

for file in os.listdir(dir_path):
    try:
        filedate = re.findall(date,file)
        if len(filedate)>0:
            if file.split(".")[-1]=='bag':
                if file.split(".")[0]+".png" in os.listdir(dir_path):
                    print(f'{file} already completed plotting')
                    continue
                if os.path.exists(dir_path+"/"+file.split(".")[0]):pending.append(file)
                else:to_run.append(file)
    except Exception as e:
        no.append(file)
plotter(to_run)
print("~-"*45)
print("+-"*45)
print("The New Bag files plot is over\nChecking for Missed bag files")
print("+-"*45)
print("~-"*45)
plotter(pending)


