# -*- coding: utf-8 -*-
"""
Created on Fri Nov 30 15:13:28 2018

@author: Krause
"""



# Import `os` 
import os
import pandas as pd
import qgrid #interactive panda
import math
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from itertools import cycle, islice
from matplotlib import cm
import re


plt.close("all")


input_flag=0



#-----------Directories------------
# Retrieve current working directory (`cwd`)
cwd = os.getcwd()
print(cwd)

# Change directory 
#os.chdir("")
'''
# List all files and directories in current directory
dir=os.listdir('.')
print(os.listdir('.'))
'''

#-----------Get data------------
# Assign spreadsheet filename to `file`
file = 'Robotop_SQL_Datenbank.xlsx'

# Load spreadsheet
xl = pd.ExcelFile(file)

'''
# Print the sheet names
print(xl.sheet_names)
'''
# Load a sheet into a DataFrame by name
data_gripper = xl.parse('gripper')
data_robot = xl.parse('robot')
data_robot_typ = xl.parse('robot_type')

print('Anzahl gripper: ' +str(len(data_gripper)))
print('Anzahl robot: ' +str(len(data_robot)))


data_gripper = data_gripper.sort_values(by=['id'])



len_groups=len(data_gripper.groupby(['version']))
color = cm.tab20b(np.linspace(.05,1, len_groups))




fig, ax = plt.subplots()
keys=[]
locator=[0]
i=0
for key, grp in data_gripper.groupby(['version']):
    ax = grp.plot(ax=ax, kind='scatter',x='max_workpiece_weight', y='stroke_per_jaw',label=key, c=color[i])#, y='number_fingers', c=key, label=key)
    print(color[i])
    keys.append(key)
    i+=1
    locator.append(i)
    


plt.legend(loc='best')
plt.show()


'''
fig, ax = plt.subplots()
keys=[]
locator=[0]
i=0
for key, grp in data_gripper.groupby(['version']):
    ax.scatter(grp['max_workpiece_weight'],[i for x in range(0, len(grp))])
    
    for row in grp[['max_workpiece_weight','name']].itertuples(index=False, name=None):
        text=re.findall(r'\d+', row[1])
        ax.text(row[0], i,'-'.join(text))    
    
    i+=1
    keys.append(key)
    locator.append(i)
    
ax.yaxis.set_ticks(locator)
ax.yaxis.set_ticklabels(keys)
ax.legend(keys)
ax.set_xlabel('max_workpiece_weight')
ax.set_ylabel('version' )
'''


def plot2d_versionen(data,x,y):
    fig, ax = plt.subplots()
    keys=[]
    locator=[0]
    i=0
    data_flow = []
    for key, grp in data.groupby(y):
        ax.scatter(grp[x],[i for l in range(0, len(grp))])
        
        for row in grp[[x,'name']].itertuples(index=False, name=None):
            text=re.findall(r'\d+', row[1])
            
            if [row[0], i] in data_flow:
                
                ax.text(row[0], i+0.28*data_flow.count([row[0], i]),'-'.join(text)) 
            else:
                ax.text(row[0], i,'-'.join(text))    
            data_flow.append([row[0], i])
        i+=1
        keys.append(key)
        locator.append(i)
    ax.set_xscale("log", nonposx='clip')
    ax.yaxis.set_ticks(locator)
    ax.yaxis.set_ticklabels(keys)
    #ax.legend(keys)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return data_flow

plot2d_versionen(data_gripper,'max_workpiece_weight','version')
plot2d_versionen(data_gripper,'stroke_per_jaw','version')
data_flow1 = plot2d_versionen(data_gripper,'closing_time','version')
plot2d_versionen(data_gripper,'opening_time','version')
plot2d_versionen(data_gripper,'max_allowed_finger_length','version')
plot2d_versionen(data_gripper,'gripper_mass','version')




def plot3d_versionen(data,x,y,z):
    len_groups=len(data.groupby(z))

    d3 = plt.figure().gca(projection='3d')
    keys=[]
    locator=[0]
    i=0
    for key, grp in data.groupby(z):
        d3.scatter(grp[x], grp[y],i)
        if i==0:
            for row in grp[[x,y,'name']].itertuples(index=False, name=None):
                text=re.findall(r'\d+', row[2])
                d3.text(row[0], row[1],i,'-'.join(text))

        keys.append(key)
        #print(key)
        i+=1
        locator.append(i)
    d3.zaxis.set_ticks(locator)
    d3.zaxis.set_ticklabels(keys)
    d3.legend(keys)
    d3.set_xlabel(x)
    d3.set_ylabel(y)
    d3.set_zlabel(z)
    plt.show()
    

plot3d_versionen(data_gripper,'max_workpiece_weight','stroke_per_jaw','version')
plot3d_versionen(data_gripper,'max_workpiece_weight','closing_time','version')
plot3d_versionen(data_gripper,'max_workpiece_weight','opening_time','version')
plot3d_versionen(data_gripper,'max_workpiece_weight','max_allowed_finger_length','version')
plot3d_versionen(data_gripper,'max_workpiece_weight','gripper_mass','version')



#%%


def plot3d_robots(data,x,y,z,gruppe):
    len_groups=len(data.groupby(gruppe))

    d3 = plt.figure().gca(projection='3d')
    keys=[]
    locator=[0]
    i=0
    for key, grp in data.groupby(gruppe):
        d3.scatter(grp[x], grp[y],grp[z])
        keys.append(key)
        #print(key)
        i+=1
        locator.append(i)
    d3.legend(keys)
    d3.set_xlabel(x)
    d3.set_ylabel(y)
    d3.set_zlabel(z)
    plt.show()


plot3d_robots(data_robot,'max_carry_weight', 'maximum_range', 'repetition_accuracy', 'type')
plot3d_robots(data_robot,'max_carry_weight', 'maximum_range', 'repetition_accuracy', 'manufacturer')

#%%

def plot2d_robots(data,x,y,gruppe1,gruppe2,axStyle=''):
    fig, ax = plt.subplots()
    keys=[]
    locator=[0]
    i=0
    data_flow = []
    for key, grp in data.groupby(gruppe1):
        ax.scatter(grp[x],grp[y])

        i+=1
        keys.append(key)
        locator.append(i)
        
        


    
    locator=[0]
    i=0
    data_flow = []    
    for key, grp in data.groupby(gruppe2):
        ax.scatter(grp[x],grp[y], marker='.')

        i+=1
        keys.append(key)
        locator.append(i)
        

    ax.legend(keys)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    if axStyle == "loglog":
        ax.set_xscale("log", nonposx='clip')
        ax.set_yscale("log", nonposy='clip')
    elif axStyle == "xlog":
        ax.set_xscale("log", nonposx='clip')
    elif axStyle == "ylog":
        ax.set_xscale("log", nonposx='clip')            
    

    

plot2d_robots(data_robot,'max_carry_weight', 'maximum_range', 'type','manufacturer')
plot2d_robots(data_robot,'max_carry_weight', 'repetition_accuracy', 'type','manufacturer')
plot2d_robots(data_robot,'repetition_accuracy', 'maximum_range', 'type','manufacturer')

