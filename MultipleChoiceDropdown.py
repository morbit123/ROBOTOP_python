
import tkinter as tk
from tkinter import *

DEBUG = False
def log(s):
    if DEBUG:
        print(s)



class MultipleChoiceDropdown(tk.Frame):
    
    
    def __init__(self, parent, attribut, database_local):
        Frame.__init__(self, parent)

        menubutton = tk.Menubutton(self, text=attribut, 
                                   indicatoron=True, borderwidth=1, relief="raised")
        menu = Menu(menubutton, tearoff=False)
        menubutton.configure(menu=menu)
        menubutton.pack(padx=10, pady=10)

        self.choices = {}
        i=0
        if type(database_local) is str:
            self.choices[database_local] = IntVar(value=1)
            menu.add_checkbutton(label=database_local, variable=self.choices[database_local], 
                                 onvalue=1, offvalue=0, 
                                 command=self.printValues)                 

        else:
            for choice in database_local:
                if i==0:
                    self.choices[choice] = IntVar(value=1)
                else:
                    self.choices[choice] = IntVar(value=0)
                i +=1            
                menu.add_checkbutton(label=choice, variable=self.choices[choice], 
                                     onvalue=1, offvalue=0, 
                                     command=self.printValues)       
         
    
    def printValues(self):
        name_list = []
        for name, var in self.choices.items():
            log( "%s: %s" %(name, var.get()))
            if var.get():
                name_list.append(name)
        log(name_list)
        log(str(name_list))
        
    def get(self):
        name_list = []
        for name, var in self.choices.items():
            if var.get():
                name_list.append(name)        
        return name_list

if __name__ == "__main__":
    database = ("Iron Man", "Superman", "Batman")
    attribut = "Choose wisely"
    
    
    root = tk.Tk()
    MultipleChoiceDropdown(root, attribut, database).pack(fill="both", expand=True)
    root.mainloop()