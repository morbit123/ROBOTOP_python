# -*- coding: utf-8 -*-
'''
Here the TreeView widget is configured as a multi-column listbox
with adjustable column width and column-header-click sorting.
'''
try:
    import Tkinter as tk
    import tkFont
    import ttk
except ImportError:  # Python 3
    import tkinter as tk
    import tkinter.font as tkFont
    import tkinter.ttk as ttk



DEBUG = False
def log(s):
    if DEBUG:
        print(s)


class MultiColumnListbox(object):
    """use a ttk.TreeView as a multicolumn ListBox"""
    header=[]
    listval=[]    
    
    
    def __init__(self,header,listval,frame):
        self.header=header
        self.listval=listval
        
        self.tree = None
        self.msg = None
        #self.container = None
        #self.container.pack(fill='both', expand=True)
        self.container = frame
             
        self._setup_widgets()
        self._build_tree()
        #self.tree.bind('<ButtonRelease-1>', self.selectItem())
        self.tree.bind("<<TreeviewSelect>>", self.selectItem)
        self.container.pack(fill='both', expand=True)  
        
    def _setup_widgets(self):
        '''
        s = """\click on header to sort by that column
to change width of column drag boundary
        """
        self.msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
            padding=(10, 2, 10, 6), text=s)
        self.msg.pack(fill='x')
        '''
        #self.container = ttk.Frame()
        #self.container.pack(fill='both', expand=True)         

        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(self.container,columns=self.header, show="headings")
        
        self.vsb = ttk.Scrollbar(self.container,orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.container,orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=self.container)
        self.vsb.grid(column=1, row=0, sticky='ns', in_=self.container)
        self.hsb.grid(column=0, row=1, sticky='ew', in_=self.container)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

    def _build_tree(self):
        for col in self.header:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            self.tree.column(col,
                width=tkFont.Font().measure(col.title()))
            

        for item in self.listval:
            self.tree.insert('', 'end', values=item, tags='tag')
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(self.header[ix],width=None)<col_w:
                    self.tree.column(self.header[ix], width=col_w)
                    #self.tree.bind('<ButtonRelease-1>', self.selectItem())
                    #self.tree.get_children(self)
            #self.tree.item()         
            #self.tree.tag_bind('ttk', '1', proc{itemclicked}); # the item clicked can be found via 'tree.focus_item'
            #self.tree.tag_bind(self.tree.column,command = lambda: log(values))
        #self.tree.tag_configure('number_fingers', background='orange')
        
    '''       
    def selectItem(self, event):
        iid = self.tree.focus()
        path = self.tree.column#self.entries[iid]
        log("%s: %s" % (iid, path))
        log(iid)#self.entries.keys())
        #self.process_directory(iid, path)     
    '''
    def selectItem(self,event):
        curItem = self.tree.focus()
        tagItem = self.tree.item(curItem)
        dictItem = dict(tagItem.items())
        valItem = dictItem['values']
        log(str(curItem) + str(tagItem))
        #log(str(valItem[0]))
        
        return valItem
    
    def destroy(self):
        self.tree.destroy()
        #self.msg.destroy()
        self.hsb.destroy()
        self.vsb.destroy()
        #self.container.destroy()

def sortby(tree, col, descending):
    """sort tree contents when a column header is clicked on"""
    # grab values to sort
    try:  
        data = [(float(tree.set(child, col)), child) \
            for child in tree.get_children('')]
    except:
        data = [(tree.set(child, col), child) \
            for child in tree.get_children('')]        
        
    #log(data)
    # if the data to be sorted is numeric change to float
    # data =  change_numeric(data)
    #data = [float(i) for i in data]
    # now sort the data in place
    data.sort(reverse=descending)
    for ix, item in enumerate(data):
        tree.move(item[1], '', ix)
    # switch the heading so it will sort in the opposite direction
    tree.heading(col, command=lambda col=col: sortby(tree, col, \
        int(not descending)))



# the test data ...

car_header = ['car', 'repair','num']
car_list = [
('Hyundai', 'brakes', 1) ,
('Honda', 'light', 21) ,
('Lexus', 'battery', 2.5) ,
('Benz', 'wiper', 3) ,
('Ford', 'tire', 33) ,
('Chevy', 'air', 28) ,
('Chrysler', 'piston',4) ,
('Toyota', 'brake pedal', 38) ,
('BMW', 'seat', 'test')
]






if __name__ == '__main__':
    '''
    root = tk.Tk()
    root.title("1")
    container = ttk.Frame(root) 
    listbox = MultiColumnListbox(car_header,car_list,container)
    #listbox.__init__(car_header,car_list)
    
    listbox.destroy()
    listbox.__init__(car_header,car_list,container)
    '''
    
    #listbox = MultiColumnListbox(car_header,car_list,container)
    
    
    root2 = tk.Tk()
    root2.title("2")
    container2 = ttk.Frame(root2)        
    listbox2 = MultiColumnListbox(car_header,car_list,container2)
    
    listbox2.destroy()
    listbox2.__init__(car_header,car_list,container2)
    
    root2.mainloop()
    
   
    