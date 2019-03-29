# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 15:11:28 2018

@author: Martin Krause (wbk)

"""

import tkinter as tk
from tkinter import *
import Robotop_Backend
import MultiColumnListbox
import MultipleChoiceDropdown
import inspect
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from itertools import cycle, islice
import re


glob_suitable_gripper = {}
glob_suitable_robot ={}
glob_data_gripper ={}
glob_data_robot ={}
glob_entries={}
glob_user_input=[]



DEBUG = False
def log(s):
    if DEBUG:
        print(s)

    



def carried_load():

    workpiece = Page_Gripper.user_input["workpiece_weight"][0] * Page_Gripper.user_input["workpiece_weight"][1]
    adapter = Page_Adapter.user_input["adapter_weight"][0] * Page_Adapter.user_input["adapter_weight"][1]
    gripper = Robotop_Backend.pd.Series(Page_Gripper.applied_component.gripper_mass).values[0]
    mass = workpiece + adapter + gripper
    
    Page.change_entry(Page_Robot.ents, "max_carry_weight", str(mass)) 
    Page.change_info(Page_Robot.ents, "max_carry_weight", \
                'gripper_mass + workpiece_weight + adapter_weight= ' + str(gripper) + \
                ' + ' + str(workpiece) + ' + ' + str(adapter))
    

    Page.change_info(Page_Adapter.ents, "adapter_weight", "Puffer Traglast Roboter: " + \
            str(Robotop_Backend.pd.Series(Page_Robot.applied_component.max_carry_weight).values[0] - mass) + " kg")    
    

    
    return mass 
    


        

class MainView(tk.Frame):

     #---------------main_loop in the loop--------------
    data_gripper = Robotop_Backend.import_excel('gripper')
    data_robot = Robotop_Backend.import_excel('robot') 
    data_robot_typ = Robotop_Backend.import_excel('robot_type') 
    data_version = Robotop_Backend.import_excel('versionen') 
    

    log("loaded data of components")
    
    data_gripper, data_robot = Robotop_Backend.component_costs(data_gripper, data_robot)
    log("added costs to components")   

    global glob_data_gripper, glob_data_robot      
    glob_data_gripper = data_gripper
    glob_data_robot = data_robot

    
    def __init__(self, *args, **kwargs):

        tk.Frame.__init__(self, *args, **kwargs)
        
        
        p1 = Page_Gripper(self)
        p2 = Page_Process(self)
        p3 = Page_Robot(self)
        p4 = Page_Adapter(self)

        buttonframe = tk.Frame(self)
        container = tk.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        p4.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tk.Button(buttonframe, text="Greifer", command=p1.lift)
        b2 = tk.Button(buttonframe, text="Prozess", command=p2.lift)
        b3 = tk.Button(buttonframe, text="Roboter", command=p3.lift)
        b4 = tk.Button(buttonframe, text="Adapter", command=p4.lift)
        
        '''
        self.button=[]
        for i in range(3):

            #self.button.append( Button(self, width=15, text=i, command= lambda: self.callback1))
            #self.button[i].pack(side="left")
            MainView.button_n(self,i,tk)
            '''

        
        

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")
        b4.pack(side="left")
        
        p1.show()
   

     
    def callback1(number):
        log("button", number)
    def button_n(self,i,tk):
        button = tk.Button(self, width=15, text=i, command= lambda: log(i))
        button.pack(side="left")






class Page(tk.Frame):
    
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        
        
    def show(self):
        self.lift()


    def makeform(self, fields, step):
        entries = []
        Label(self,text=step).pack()
        for key in fields:
            row = Frame(self)
            lab = Label(row, width=15, text=key, anchor='w')
            
            
            try:
                minmax = Label(row, width=20, text=" (min = " + str(fields[key][3])+ "/max = " + str(fields[key][4])+ ")", anchor='w')            
            except:
                minmax = Label(row, width=20, text='', anchor='w')  
            
            try:
                unit = Label(row, width=4, text=fields[key][2], anchor='w')
            except:
                unit = Label(row, width=4, text='', anchor='w')
    
    
                   
            info = Label(row, width=45, text='', anchor='w')
            
            try: 
                if type(fields[key][0])==int:
                    int(fields[key][0])
                else:
                    list(map(float ,fields[key][0].split(',')))
                    
                ent = Entry(row)
                ent.insert(END, fields[key][0])            
            except:
                ent = MultipleChoiceDropdown.MultipleChoiceDropdown(row, key, fields[key][0])
                
            var = IntVar()
            var.set(fields[key][1])
            log('fields[key][1]=' + str(fields[key][1]))
            chk = Checkbutton(row, variable = var)
            
            
            
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            minmax.pack(side=LEFT)
            chk.pack(side=LEFT, expand=YES, fill=X)
            ent.pack(side=LEFT, expand=YES, fill=X)
            unit.pack(side=LEFT, expand=YES, fill=X)
            info.pack(side=LEFT, expand=YES, fill=X)
            
    
            entries.append((key, ent, var, unit, info)) 
    
    
        return entries  

    def fetch_user_input(self, entries):
        
        user_input = {}
        for entry in entries:
            field = entry[0]        #discription/ attribute of component
            text  = entry[1].get()  #value of attribute
            state = entry[2].get()  #state of attribute (used for limitation of configuration)
            info  = entry[3]
            unit  = entry[4]
            try:
                text =float(text)
                user_input[field] = [text,state] 
            except:
                user_input[field] = [text,state]
                #entry[1].delete(0,END)
                #entry[1].insert(END, "only num")
              
            log('%s: "%s"' % (field, text))
    
        #Label(root, text=entry[1].get()).pack()
        #log(entries[0][1].get())
        #log(entries[1][1].get())
        for key in user_input:
            log(key + ':' + str(user_input[key][0]) + ' ' + str(user_input[key][1]))
    
        return user_input

    @staticmethod
    def change_entry(entries, attribut, value):
        for entry in entries:
            field = entry[0]        #discription/ attribute of component
            #text  = entry[1].get()  #value of attribute
            #state = entry[2].get()  #state of attribute (used for limitation of configuration)
            #unit  = entry[3].get()
            #info  = entry[4].get()
            if field == attribut:
                entry[1].delete(0,END)
                entry[1].insert(END, value) 
    
    @staticmethod
    def change_info(entries, attribut, info):
        for entry in entries:
            field = entry[0]        #discription/ attribute of component
            #text  = entry[1].get()  #value of attribute
            #state = entry[2].get()  #state of attribute (used for limitation of configuration)
            #unit  = entry[3].get()
            #info  = entry[4].get()
            if field == attribut:
                entry[4]['text'] = info
                
                
    @staticmethod
    def get_entry(entries, attribut):
        value = []
        for entry in entries:
            field = entry[0]        #discription/ attribute of component
            if field == attribut:
                value =float(entry[1].get()) 
                chk   =float(entry[2].get()) 
        return value, chk

    def apply_component_callback(self,component):
        log(component)
        self.T.delete(1.0, END)   # empty widget to log new text
        self.T.insert(END, "%s\n" %component) 
        self.applied_component = component

        
            

class Page_Gripper(Page):
    
    applied_component=MainView.data_gripper.iloc[0]
    suitable_component=MainView.data_gripper.iloc[0]
    
    user_input = {"workpiece_weight":[22, 1, 'kg', 0, MainView.data_gripper.max_workpiece_weight.max()],  \
                          "stroke_per_jaw":[10, 1, 'mm', 0, MainView.data_gripper.stroke_per_jaw.max()],  \
                          "finger_length":[10, 1, 'mm', 0, MainView.data_gripper.max_allowed_finger_length.max()], \
                          "version":[list(MainView.data_version.version),1],\
                          "manufacturer":["Schunk",0],\
                          "energy_system":["pneumatic",0]} 
    
    test_var=0
    row=[]
    
    ents = []

    
    def __init__(self,  *args, **kwargs):

        Page.__init__(self,  *args, **kwargs)    

        
        Page_Gripper.ents = Page.makeform(self, Page_Gripper.user_input, "Gripper Configuration")
        T = tk.Text(self, height=25, width=100)
        
        left_row = Frame(self)
        left_row.pack(side=LEFT, fill=X, padx=5, pady=5)
        
        b1 = Button(left_row, text='Zeige kompatible Greifer',
              command=(lambda e=Page_Gripper.ents: Page_Gripper.your_gripper_list(self, Page.fetch_user_input(self, e),T)))

        b1.grid(row=0,column=0)  
        

        b2 = Button(left_row, text='Nehme markierten Greifer',
              command=(lambda: Page.apply_component_callback(self,self.suitable_component.loc[self.suitable_component.id==listbox_gripper.selectItem(self)[0]].T)))
        #self.listbox.selectItem(self)[0] --> Item aus MultiColumnListbox
        #referenziert auf suitable_component
        b2.grid(row=2,column=0)  

        
        T.pack()
        T.insert(END, "Info\n")     
        
        
    def your_gripper_list(self, user_input,T):
        self.T = T   
        T.delete(1.0, END)   # empty widget to log new text
        
        Page_Gripper.user_input = user_input
        global glob_user_input
        glob_user_input = user_input["version"][0]
        
        Page_Gripper.suitable_component, Page_Gripper.applied_component = Robotop_Backend.config_your_gripper(MainView.data_gripper,user_input)
        T.insert(END, "%s\n" %Page_Gripper.applied_component.T)   
        Page_Gripper.test_var=Robotop_Backend.pd.Series(Page_Gripper.applied_component.gripper_mass).values[0]
        
        
        
        carried_load()
    
        #log("Page_Gripper.test_var="+str(Page_Gripper.test_var))
        #return suitable_component
        global glob_suitable_gripper
        glob_suitable_gripper = Page_Gripper.suitable_component    
        
    
        
        
        
        listbox_gripper.destroy()
        listbox_gripper.__init__(list(Page_Gripper.suitable_component.columns),Page_Gripper.suitable_component.values.tolist(),container_list_gripper)
        


  

           

class Page_Process(Page):
    user_input = {        "Pick":['0.0, 1.0, 2.0', 1, '<x,y,z> mm'], \
                          "Place":['100, 150, 0', 1, '<x,y,z> mm'],  \
                          "Robot":['50, 50, 0', 1, '<x,y,z> mm'],  \
                          "Rotate":['0, 0, 90', 1, '<rx,ry,rz> °']}    


    var = 0
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ents = []
    
    
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        Page_Process.ents = Page.makeform(self, Page_Process.user_input, "Process Configuration")

        left_row = Frame(self)
        left_row.pack(side=LEFT, fill=X, padx=5, pady=5)
        right_row = Frame(self)
        right_row.pack(side=RIGHT, fill=X, padx=5, pady=5)

        
        Page_Process.var = IntVar()
        Page_Process.var.set(0)
        chk = Checkbutton(left_row, variable = Page_Process.var)
        
        self.canvas = FigureCanvasTkAgg(Page_Process.fig, master = right_row)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        
        
        b1 = Button(left_row, text='Berechne Prozess',
              command=(lambda e=Page_Process.ents: Page_Process.your_process(self, Page.fetch_user_input(self, e))))

        b1.grid(row=0,column=0)
        chk.grid(row=0,column=1)
        


        
        
        self.canvas._tkcanvas.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1) 

        
        #self.toolbar.update()
        #self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        Page_Process.update_fig(self)
        
        
        
    
    def update_fig(self):
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    

    def your_process(self, user_input):
        log(user_input)
        
        P_pick = np.array(list(map(float ,user_input['Pick'][0].split(','))))
        P_place = np.array(list(map(float ,user_input['Place'][0].split(','))))
        P_robi = np.array(list(map(float ,user_input['Robot'][0].split(','))))
        Rotation = np.array(list(map(float ,user_input['Rotate'][0].split(','))))
        
        

        
        P, dist, positioning_range = Robotop_Backend.positioning(P_pick,P_place,P_robi)
        log('Needed positioning range: '+str( positioning_range) +' mm')
        
        P_label=['P_pick','P_place','P_robi']
    
        #fig = plt.figure()
    
        Page_Process.ax = Page_Process.fig.add_subplot(111, projection='3d')
        #Page_Process.ax.clear()
    
        Page_Process.ax.text2D(0.05, 0.95, ('Needed positioning range (maximum_range): '+str( positioning_range) +' mm'), transform=Page_Process.ax.transAxes)
        Page_Process.ax.scatter(P[0], P[1], P[2], zdir='z', s=20, c=None, depthshade=True)
        Page_Process.ax.set_xlabel('x [mm]'),Page_Process.ax.set_ylabel('y [mm]'),Page_Process.ax.set_zlabel('z [mm]')
        for label, x, y, z in zip(P_label, P[0], P[1], P[2]):
            label = '%s=(%d, %d, %d)' % (label, x, y, z)
            Page_Process.ax.text(x, y, z, label, None)
        
        
        Page_Process.ax.text( (P_pick[0]+P_robi[0])/2,(P_pick[1]+P_robi[1])/2,(P_pick[2]+P_robi[2])/2, ['pick:' + str(round(dist[0],1))+ ' mm'], P_pick-P_robi)
        Page_Process.ax.plot(P[0][[0,2]], P[1][[0,2]], P[2][[0,2]])
        Page_Process.ax.text( (P_place[0]+P_robi[0])/2, (P_place[1]+P_robi[1])/2, (P_place[2]+P_robi[2])/2, ['place: ' + str(round(dist[1],1))+ ' mm'], P_place-P_robi)
        Page_Process.ax.plot(P[0][[1,2]], P[1][[1,2]], P[2][[1,2]])
        #Page_Process.toolbar.update()
        Page_Process.update_fig(self)
    
        Page.change_entry(Page_Robot.ents, "maximum_range", positioning_range)
        Page.change_info(Page_Robot.ents, "maximum_range", "Eintragung aufgrund Prozess")
        #"maximum_range"
        
        #Page_Process.canvas.draw(Page_Process.fig)

       

class Page_Robot(Page):
    applied_component=MainView.data_robot.iloc[0]
    suitable_component=MainView.data_robot.iloc[0]    
    user_input = {"max_carry_weight":[5, 1, 'kg', 0, MainView.data_robot.max_carry_weight.max()],\
                                            "maximum_range":[1100, 1, 'mm', 0, MainView.data_robot.maximum_range.max()],\
                                            "repetition_accuracy":[1, 1, 'mm', MainView.data_robot.repetition_accuracy.min(), MainView.data_robot.repetition_accuracy.max()],\
                                            "typical_movement_speed":[1, 0, 'mm', 0, MainView.data_robot.typical_movement_speed.max()],\
                                            "type":[[x for x,y in MainView.data_robot.groupby(['type'])], 0, 'mm']  
                                            
                                            
                                            } 
    list(MainView.data_version.version)
    
    
    ents = []
    

    
    def __init__(self, *args, **kwargs):
        
     
        
        
        
        Page.__init__(self, *args, **kwargs)
       
        
        Page_Robot.ents = Page.makeform(self, Page_Robot.user_input, "Robot Configuration")
        T = tk.Text(self, height=20, width=100)
        
        
        left_row = Frame(self)
        left_row.pack(side=LEFT, fill=X, padx=5, pady=5)        
        
        
        b1 = Button(left_row, text='Zeige kompatible Roboter',
              command=(lambda e=Page_Robot.ents: Page_Robot.your_robot_list(self, Page.fetch_user_input(self, e),T)))
        b1.grid(row=0,column=0) 
        
        b2 = Button(left_row, text='Nehme markierten Roboter',
              command=(lambda: Page.apply_component_callback(self,self.suitable_component.loc[self.suitable_component.id==listbox_robot.selectItem(self)[0]].T)))

        b2.grid(row=2,column=0)          
        
        
        T.pack()
        T.insert(END, "Info\n")  

    def update_form(self):
        ents = Page.makeform(self, Page_Robot.user_input, "Robot Configuration")


    def your_robot_list(self, user_input,T):
        self.T = T
    
        Page_Robot.user_input = user_input
        #ents = makeform(self, Page_Gripper.user_input, "Gripper Configuration")
        
        log("Page_Gripper.test_var="+str(Robotop_Backend.pd.Series(Page_Gripper.applied_component.gripper_mass).values[0]))
        log("user_input[max_carry_weight][0]="+str(user_input["max_carry_weight"][0]))
        log("user_input[maximum_range][0]="+str(user_input["maximum_range"][0]))
        log("user_input[type][0]="+str(user_input["type"][0]))
        
        T.delete(1.0, END)   # empty widget to log new text
        Page_Robot.suitable_component, Page_Robot.applied_component = Robotop_Backend.config_your_robot(MainView.data_robot,user_input)
        T.insert(END, "%s\n" %Page_Robot.applied_component.T)    
        
        global glob_suitable_robot
        glob_suitable_robot = Page_Robot.suitable_component
        
    
        carried_load = Page_Adapter.user_input["adapter_weight"][0] + Page_Gripper.user_input["workpiece_weight"][0] + Robotop_Backend.pd.Series(Page_Gripper.applied_component.gripper_mass).values[0]
        Page.change_info(Page_Adapter.ents, "adapter_weight", "Puffer Traglast Roboter: " + \
                    str(Robotop_Backend.pd.Series(Page_Robot.applied_component.max_carry_weight).values[0] - carried_load) + " kg")
        # - Robotop_Backend.pd.Series(Page_Robot.applied_component.max_carry_weight).values[0]
    
    
        
        listbox_robot.destroy()
        listbox_robot.__init__(list(Page_Robot.suitable_component.columns),Page_Robot.suitable_component.values.tolist(),container_list_robot)
    
        
        return Page_Robot.suitable_component, Page_Robot.applied_component
        
        
class Page_Adapter(Page):
    #Adapter_Weight = 2
    user_input = {"adapter_weight":[2,1]} 
    


    
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        Page_Adapter.ents = Page.makeform(self, Page_Adapter.user_input, "Adapter Configuration")
        T = tk.Text(self, height=20, width=100)
        
        
        left_row = Frame(self)
        left_row.pack(side=LEFT, fill=X, padx=5, pady=5)   
        
        b1 = Button(left_row, text='Zeige kompatible Adapter',
              command=(lambda e=Page_Adapter.ents: Page_Adapter.your_adapter_list(self, Page.fetch_user_input(self, e),T)))
        b1.grid(row=0,column=0)         
        
        T.pack()
        T.insert(END, "Info\n") 

    def your_adapter_list(self, user_input, T):
        log(user_input)
        Page_Adapter.user_input = user_input
        carried_load()             

        

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ROBOTOP")    
    
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("1000x800")
    
    list_gripper = tk.Tk()
    list_gripper.title("Geeignete Greifer")
    container_list_gripper = tk.Frame(list_gripper)      
    listbox_gripper = MultiColumnListbox.MultiColumnListbox(list(MainView.data_gripper.columns),MainView.data_gripper.values.tolist(),container_list_gripper)
    
    list_robot = tk.Tk()
    list_robot.title("Geeignete Roboter")
    container_list_robot = tk.Frame(list_robot)      
    listbox_robot = MultiColumnListbox.MultiColumnListbox(list(MainView.data_robot.columns),MainView.data_robot.values.tolist(),container_list_robot)

    root.mainloop()
    
    
    