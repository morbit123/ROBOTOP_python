# -*- coding: utf-8 -*-
"""
Created on Fri Aug 31 10:07:23 2018

@author: Krause
"""
from tkinter import *
import os
import pandas as pd
#import qgrid #interactive panda
import math
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
#import vectormath as vmath


DEBUG = False
def log(s):
    if DEBUG:
        print(s)



def import_excel2(database):
    # Assign spreadsheet filename to `file`
    file = 'Robotop_SQL_Datenbank.xlsx'
    
    # Load spreadsheet
    xl = pd.ExcelFile(file)

    # Load a sheet into a DataFrame by name
    data_gripper = xl.parse('gripper')
    data_robot = xl.parse('robot')
    data_robot_typ = xl.parse('robot_type')
    
   
    len_grippers  = len(data_gripper.name)
    len_robots  = len(data_robot.name)
    return data_gripper, data_robot, data_robot_typ

def import_excel(database_name):
    # Assign spreadsheet filename to `file`
    file = 'Robotop_SQL_Datenbank.xlsx'
    
    # Load spreadsheet
    xl = pd.ExcelFile(file)

    # Load a sheet into a DataFrame by name
    database = xl.parse(database_name)
    return database

def component_costs(data_gripper, data_robot):
    
    Preisklasse_Robi={"Vertikalknickarm (7-Achsen)":12,
                "Vertikalknickarm (6-Achsen)":10, 
                 "Vertikalknickarm (5-Achsen)":8,
                 "Vertikalknickarm (4-Achsen)":6,
                 "Vertikalknickarm (3-Achsen)":4,
                 "Scara (Horizontalknickarm)":1}
    Preisklasse_Robi_list=[]
    for rob_type in data_robot.type:
        Preisklasse_Robi_list.append(Preisklasse_Robi[rob_type])
    #cost, relative of robot with sum of properties: repetition_accuracy,max_carry_weight,maximum_range,type
    data_robot = data_robot.assign(cost_dummy=round((pd.to_numeric(max(data_robot.repetition_accuracy)/data_robot.repetition_accuracy, errors='coerce')**0.2 \
         + data_robot.max_carry_weight/max(data_robot.max_carry_weight)*0.5 \
         + data_robot.maximum_range/max(data_robot.maximum_range)*1)*Preisklasse_Robi_list \
         ,2))    
    
    
    #cost, relative of Gripper with sum of properties: 
    data_gripper=data_gripper.assign(cost_dummy=round(data_gripper.number_fingers/max(data_gripper.number_fingers) \
            + data_gripper.stroke_per_jaw/max(data_gripper.stroke_per_jaw) \
            + data_gripper.max_workpiece_weight/max(data_gripper.max_workpiece_weight) \
            + (max(data_gripper.gripper_mass)-data_gripper.gripper_mass)/max(data_gripper.gripper_mass)/5 \
            ,2))
    
    return data_gripper, data_robot


def reduce_components_greater_than(data, attribute, user_input):
    '''
    #andere Schreibweise
    #          & (glob_data_gripper['version'].str.contains([gripper_user_input["version"][0]])) | (not gripper_user_input["version"][1])) \    
    Krit=(((data_gripper.max_workpiece_weight>=gripper_user_input["workpiece_weight"][0]) | (not gripper_user_input["workpiece_weight"][1])) \
          & ((data_gripper.stroke_per_jaw>=gripper_user_input["stroke_per_jaw"][0]) | (not gripper_user_input["stroke_per_jaw"][1])) \
          & ((data_gripper.max_allowed_finger_length>=gripper_user_input["finger_length"][0]) | (not gripper_user_input["finger_length"][1])) \
          )

    suitable_gripper=data_gripper.loc[Krit]
    '''    
    for key  in attribute.keys():
        if user_input[key][1]:
            data=data.loc[data[attribute[key]]>=user_input[key][0]]
    return data
                
def reduce_components_per_str(data, attribute, user_input):
    #suche von strings
    #weitere Schreibweisen
    #data_gripper['version'].str.find('IS')
    #data_gripper.set_index('version').loc[[gripper_user_input["version"][0]]]  # finde exklusive str
    #data_gripper.loc[data_gripper['version'].str.contains("IS|AS")]
    #data_gripper.loc[glob_data_gripper['version'].isin(['K','IS'])]
    for key  in attribute.keys():

        if user_input[key][1]:
            data = data.loc[data[attribute[key]].isin(user_input[key][0])]        
    return data

def show_rest_in_data(data, attribute, user_input):
    data_tmp = data
    for key  in attribute.keys():
        data_tmp[key+"_rest"]=data[attribute[key]]-user_input[key][0]
        data[key+"_rest"]  = data_tmp[key+"_rest"].astype(str).str.cat(data_tmp[attribute[key]].astype(str), sep=' von ')
        if user_input[key][0]!=0:
            data_tmp[key+"_prozent"]=round((data[attribute[key]]-user_input[key][0])/user_input[key][0]*100,1)
            data[key+"_rest"]  = data[key+"_rest"].astype(str).str.cat(data_tmp[key+"_prozent"].astype(str), sep=' %+')
            #data = data.drop([key+"_prozent"], axis=1)
    for key  in attribute.keys():    
        if user_input[key][0]!=0:
            data = data.drop(columns=[key+"_prozent"])
    return data

def config_your_gripper(data_gripper,gripper_user_input):
    #data_gripper with max_workpiece_weight,  max_allowed_finger_length
    #gripper_user_input["property"] --> spezification of gripper properties (property has to be in dataframe)
    #gripper_user_krit["property"] --> used criteria (0--> not used, 1--> used)
    suitable_gripper=0
    applied_gripper=0
    #------------Logic----------------------------
    #If-Bedigungen: <, <=, >, >=, ==, !=
    #Verknüpfungen: &-->and;>=1 bzw |-->or
    
    if gripper_user_input["workpiece_weight"][1]: log("max_workpiece_weight>=" + str(gripper_user_input["workpiece_weight"][0]))
    if gripper_user_input["finger_length"][1]: log("max_allowed_finger_length>=" + str(gripper_user_input["finger_length"][0]))
    
    log(str(gripper_user_input["version"][0]))
    

    
    suitable_gripper=data_gripper
    
    attribute_num =  {'workpiece_weight': 'max_workpiece_weight',
                 'stroke_per_jaw': 'stroke_per_jaw',
                 'finger_length':'max_allowed_finger_length'}         
    suitable_gripper = reduce_components_greater_than(suitable_gripper, attribute_num, gripper_user_input)
    #suche nach strings    
    attribute_str =  {'version': 'version',
                 'manufacturer': 'manufacturer',
                 'energy_system':'energy_system'}
    log(gripper_user_input)
    suitable_gripper = reduce_components_per_str(suitable_gripper, attribute_str, gripper_user_input)
 

    suitable_gripper = show_rest_in_data(suitable_gripper, attribute_num, gripper_user_input)
    

    if len(suitable_gripper.name)==0:
        #sys.exit("No suitable gripper found!")
        suitable_gripper['name'] = "No suitable gripper found!"
        applied_gripper = suitable_gripper
    else:
        suitable_gripper=suitable_gripper.sort_values(by=['cost_dummy'])
        log("Kostengünstigster Greifer für deine Anwendung: ")
        log(suitable_gripper.nsmallest(1, 'cost_dummy').name)
        log(suitable_gripper.iloc[0])
        applied_gripper = suitable_gripper.nsmallest(1, 'cost_dummy')


    
    
    return suitable_gripper, applied_gripper






def config_your_robot(data_robot,robot_user_input):
    suitable_robot=data_robot
    
    attribute_num =  {'max_carry_weight': 'max_carry_weight',
                 'maximum_range': 'maximum_range',
                 'typical_movement_speed':'typical_movement_speed'}         
    suitable_robot = reduce_components_greater_than(suitable_robot, attribute_num, robot_user_input)
    

    #suche nach strings    
    attribute_str =  {'type': 'type'}
    suitable_robot = reduce_components_per_str(suitable_robot, attribute_str, robot_user_input)    
    
    
    '''
    Krit=(((data_robot.max_carry_weight>=robot_user_input["max_carry_weight"][0]) | (not robot_user_input["max_carry_weight"][1])) \
          & ((data_robot.maximum_range>=robot_user_input["maximum_range"][0]) | (not robot_user_input["maximum_range"][1])))
    
    suitable_robot=data_robot.loc[Krit]
    suitable_robot_tmp = suitable_robot 

    suitable_robot_tmp["max_carry_weight_rest"]=suitable_robot["max_carry_weight"]-robot_user_input["max_carry_weight"][0]
    suitable_robot["max_carry_weight_rest"]  = suitable_robot_tmp.max_carry_weight_rest.astype(str).str.cat(suitable_robot_tmp.max_carry_weight.astype(str), sep=' von ')
    suitable_robot_tmp["maximum_range_rest"]=suitable_robot["maximum_range"]-robot_user_input["maximum_range"][0]
    suitable_robot["maximum_range_rest"]  = suitable_robot_tmp.maximum_range_rest.astype(str).str.cat(suitable_robot_tmp.maximum_range.astype(str), sep=' von ')    
    '''
    #----------------------
    
    if len(suitable_robot.name)==0:
        #sys.exit("No suitable robot found!")
        suitable_robot['name'] = "No suitable robot found!"
        applied_robot = suitable_robot
    else:
        suitable_robot=suitable_robot.sort_values(by=['cost_dummy'])
        
        log("Kostengünstigster Roboter für deine Anwendung: ")
        log(suitable_robot.nsmallest(1, 'cost_dummy').name)
        log(suitable_robot.iloc[0])
        applied_robot = suitable_robot.nsmallest(1, 'cost_dummy')

    return suitable_robot, applied_robot



def positioning(P_pick,P_place,P_robi):

    
    P=np.array([P_pick,P_place,P_robi]).T
    
    
    dist = [np.linalg.norm(P_pick-P_robi), np.linalg.norm(P_place-P_robi)]
    positioning_range = round(max(dist),1)
    #log('Needed positioning range: '+str( positioning_range) +' mm')
    
    
    
    
    
    
    
    
    return P, dist, positioning_range

    
    


    

