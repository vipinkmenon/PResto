##############################################################################################################################
#    module     : gui                                                                                                        #
#    descript   : The PResto GUI                                                                                             #
#    dependency :                                                                                                            #
#    additional package :                                                                                                    #
#    author     : Vipin.K                                                                                                    #
#                                                                                                                            #
#                                                                                                                            #
##############################################################################################################################

import wx
import shutil
import thread
import scripts.check_script
import os
import sys
import time
from wx import html
import xml
import xml.etree.ElementTree as ET


class design_module:                                  #node class type
    def __init__(self,name,path,src_tstamp,nlist_tstamp,imp_stat,slicem,slicel,bram,dsp):
        self.name          = name
        self.path          = path
        self.src_tstamp    = src_tstamp
        self.nlist_tstamp  = nlist_tstamp
        self.imp_stat      = imp_stat
        self.slicem        = slicem
        self.slicel        = slicel
        self.bram          = bram
        self.dsp           = dsp

class PrestoFrame(wx.Frame):
    def __init__(self,parent):
        self.title = "PResto"
        wx.Frame.__init__(self,parent,-1,self.title,wx.DefaultPosition,size=(860,420),style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        
        self.main = wx.SplitterWindow(self)
        self.main.SetMinimumPaneSize(100) #project panel
        self.pp = wx.SplitterWindow(self.main)
        self.pp.SetMinimumPaneSize(100) #project panel
        self.ap = wx.SplitterWindow(self.main)
        self.ap.SetMinimumPaneSize(100) #action panel
        self.sp = wx.SplitterWindow(self.ap)
        self.sp.SetMinimumPaneSize(100) #source panel
        
        self.source_pane = wx.ScrolledWindow(self.pp,-1)
        self.task_pane = wx.Panel(self.pp,style=wx.SUNKEN_BORDER)
        self.stat_pane = wx.Panel(self.sp,style=wx.SUNKEN_BORDER)
        self.name_pane = wx.Panel(self.sp,style=wx.SUNKEN_BORDER)
        self.log_pane = wx.Panel(self.ap,style=wx.SUNKEN_BORDER)

        self.source_pane.SetBackgroundColour("white")
        self.task_pane.SetBackgroundColour("white")
        self.name_pane.SetBackgroundColour("grey")
        self.stat_pane.SetBackgroundColour("white")
        self.log_pane.SetBackgroundColour("white")

        self.main.SplitVertically(self.pp,self.ap,150)
        self.pp.SplitHorizontally(self.source_pane,self.task_pane,200)
        self.ap.SplitHorizontally(self.sp,self.log_pane,250)
        self.sp.SplitVertically(self.stat_pane,self.name_pane,150)

        text = wx.StaticText(self.name_pane,-1,"PResto",(250,100))
        font = wx.Font(40,wx.FONTFAMILY_DEFAULT,wx.ITALIC,wx.NORMAL)
        text.SetFont(font)
        self.initStatusBar()
        self.createMenuBar()
        self.synth = None
        self.part = None
        text = wx.StaticText(self.source_pane,-1,"Sources",(5,10))
        text = wx.StaticText(self.task_pane,-1,"Processes",(5,10))
        text = wx.StaticText(self.task_pane,-1,"------------",(5,21))
        text = wx.StaticText(self.stat_pane,-1,"Properties",(5,10))
        thread.EVT_RESULT(self,self.OnResult)
        self.filename = ""
        self.moduleNameList = []
        top_module_list = []   
        self.rb = None
        self.synth_stat = None
        self.module_list = {}
        self.configuration = None
        #self.log_file = open('presto_log.txt','w')
        self.log = wx.TextCtrl(self.log_pane,-1,size=(700,100),style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        redir=RedirectText(self.log)
        sys.stdout=redir
        self.saveFlag = 1
        self.Bind(wx.EVT_CLOSE,self.OnCloseWindow)
        self.State = "0"

    def initStatusBar(self):
        self.statusbar = self.CreateStatusBar()

    def menuData(self):
        data = [("&File",(
                  ("&New Project","New Project",self.OnNew),
                  ("&Open Project","Open Project",self.OnOpen),
                  ("&Save","Save",self.OnSave),
                  ("Save&As","Save As",self.OnSaveAs),
                  ("","",""),
                  ("&Quit","Quit",self.OnCloseWindow))),
                ("&Edit",(
                  ("&Add Files","Add Verilog source files",self.OnAddfiles),
                  ("&Remove Files","Remove Verilog source files",self.OnRemovefiles),
                  ("&Add Configuration","Add the system Configuration file",self.OnAddConfiguration),
                  ("&Clear Transcript","Clear the transcript window",self.OnClearTrnc),
                  ("&Clear Project files","Remove all project files",self.OnClearPrj),
                )),
                ("&Run",(
                  ("&Start","Run the project",self.OnRun),
                  ("&Abort","Abort currently running process",self.OnAbort),
                )),
                ("&About",(
                  ("&Help","Help",self.OnHelp),
                  ("&About","About",self.OnAbout),
               ))]
        return data

    def createMenuBar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1]
            menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)

    def createMenu(self,menuData):
        menu = wx.Menu()
        for eachItem in menuData:
            if len(eachItem) == 2:
                label = eachItem[0]
                subMenu = self.createMenu(eachItem[1])
                menu.AppendMenu(wx.NewId(), label, subMenu)
            else:
                self.createMenuItem(menu, *eachItem)
        return menu

    def createMenuItem(self,menu,label,status,handler,kind=wx.ITEM_NORMAL):
        if not label:
            menu.AppendSeparator()
            return
        menuItem = menu.Append(-1,label,status,kind)
        self.Bind(wx.EVT_MENU,handler,menuItem)

    def OnCloseWindow(self,event):
        if self.saveFlag:
            self.Destroy()
            #self.log_file.close()
        else:
            dlg = wx.MessageDialog(self,"Do you want to save the changes?",'Save',wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
            retCode = dlg.ShowModal()
            if (retCode == wx.ID_YES):
                self.OnSave(event)
                self.Destroy()
            elif (retCode == wx.ID_NO):
                self.Destroy()
            else:
                pass

    def SaveFile(self):
        if self.filename:
            f = open(self.filename,'w')
            f.write("<pr_design>\n")
            f.write("\t<modules>\n")
            modules = self.module_list.keys()
            for module in modules:
                f.write("\t\t<module name = \"%s\">\n"%(self.module_list[module].name))
                f.write("\t\t\t<path>%s</path>\n"%(self.module_list[module].path))
                f.write("\t\t\t<src_ts>%s</src_ts>\n"%(self.module_list[module].src_tstamp))
                f.write("\t\t\t<nlist_tstamp>%s</nlist_tstamp>\n"%(self.module_list[module].nlist_tstamp))
                f.write("\t\t\t<imp_stat>%s</imp_stat>\n"%(self.module_list[module].imp_stat))
                f.write("\t\t\t<slicel>%s</slicel>\n"%(self.module_list[module].slicel))  
                f.write("\t\t\t<slicem>%s</slicem>\n"%(self.module_list[module].slicem))                              
                f.write("\t\t\t<bram>%s</bram>\n"%(self.module_list[module].bram))
                f.write("\t\t\t<dsp>%s</dsp>\n"%(self.module_list[module].dsp))          
                f.write("\t\t</module>\n")
            f.write("\t</modules>\n")
            
            f.write("\t<partitions>\n")
            f.write("\t</partitions>\n")
            f.write("\t<floorplan>\n")
            f.write("\t</floorplan>\n")
            f.write("\t<state>\n")
            f.write("\t\t<proj_state>%s</proj_state>\n"%(self.State))
            f.write("\t</state>\n")
            f.write("</pr_design>\n")
            f.close()
            self.saveFlag = 1

    def ReadProjectFile(self):
        if self.filename:
            design_tree = ET.parse(self.filename)
            root        = design_tree.getroot()                  
            for module in root[0] :  
                module_name = module.get('name')
                self.module_list[module_name] = design_module(module_name,module.find('path').text,module.find('src_ts').text,module.find('nlist_tstamp').text,module.find('imp_stat').text,module.find('slicem').text,module.find('slicel').text,module.find('bram').text,module.find('dsp').text)
                self.moduleNameList.append(module_name)
            self.State = root[3].find('proj_state').text
            self.AddRadio()
        else:
            wx.MessageBox("%s is not a PResto file."%self.filename,"Error!",style=wx.OK|wx.ICON_EXCLAMATION)

    wildcard1 = "PResto files (*.prf) | *.apr|All files (*.*)|*.*"
    wildcard2 = "Verilog files (*.v) | *.v|All files (*.*)|*.*"
    wildcard3 = "Configuration file (*.conf) | *.conf|All files (*.*)|*.*"


    def OnNew(self,event):
        dlg = wx.FileDialog(self, "New PResto project...", os.getcwd(),style=wx.OPEN,wildcard=self.wildcard1)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            f = open(self.filename,'w')
            self.SetTitle(self.title+'--'+self.filename)
            f.close()
        dlg.Destroy()

    def OnOpen(self,event):
        dlg = wx.FileDialog(self, "Open PResto project...", os.getcwd(),style=wx.OPEN,wildcard=self.wildcard1)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.ReadProjectFile()
            self.SetTitle(self.title+'--'+self.filename)
            if self.State == "1":
                wx.StaticText(self.task_pane,-1,"Resource estimate: Finished",(0,40))
                wx.StaticText(self.task_pane,-1,"Design partitioning: Not started",(0,60))
                wx.StaticText(self.task_pane,-1,"Floorplanning: Not started",(0,80))
                wx.StaticText(self.task_pane,-1,"BitGen: Not started",(0,100))
            elif self.State == "2":
                wx.StaticText(self.task_pane,-1,"Resource estimate: Finished",(0,40))
                wx.StaticText(self.task_pane,-1,"Design partitioning: Finished",(0,60))
                wx.StaticText(self.task_pane,-1,"Floorplanning: Not started",(0,80))
                wx.StaticText(self.task_pane,-1,"BitGen: Not started",(0,100))
            elif self.State == "3":
                wx.StaticText(self.task_pane,-1,"Resource estimate: Finished",(0,40))
                wx.StaticText(self.task_pane,-1,"Design partitioning: Finished",(0,60))
                wx.StaticText(self.task_pane,-1,"Floorplanning: Finished",(0,80))
                wx.StaticText(self.task_pane,-1,"BitGen: Not started",(0,100))
            elif self.State == "4":
                wx.StaticText(self.task_pane,-1,"Resource estimate: Finished",(0,40))
                wx.StaticText(self.task_pane,-1,"Design partitioning: Finished",(0,60))
                wx.StaticText(self.task_pane,-1,"Floorplanning: Finished",(0,80))
                wx.StaticText(self.task_pane,-1,"BitGen: Finished",(0,100))
            else:
                wx.StaticText(self.task_pane,-1,"Resource estimate: Not started",(0,40))
                wx.StaticText(self.task_pane,-1,"Design partitioning: Not started",(0,60))
                wx.StaticText(self.task_pane,-1,"Floorplanning: Not started",(0,80))
                wx.StaticText(self.task_pane,-1,"BitGen: Not started",(0,100)) 

    def OnAddfiles(self,event):
        if not self.filename:
            wx.MessageBox("No project is open","Error!",style=wx.OK|wx.ICON_EXCLAMATION)
        else:
            dlg = wx.FileDialog(self, "Add source files...", os.getcwd(),style = wx.OPEN | wx.MULTIPLE,wildcard=self.wildcard2)
            if dlg.ShowModal() == wx.ID_OK:
                for path in dlg.GetPaths():
                    module_name = path.split("\\")[-1][:-2]
                    if module_name not in self.moduleNameList:                         
                        self.moduleNameList.append(module_name)                    
                        self.module_list[module_name] = design_module(module_name,path,(time.ctime(os.path.getmtime(path))),None,'out',None,None,None,None)
                        self.saveFlag = 0
                self.AddRadio()
            dlg.Destroy()                

    def OnRemovefiles(self,event):
        if self.module_list:
            dialog = wx.MultiChoiceDialog(self,"Select files","Remove files",self.moduleNameList)
            temp_list = self.moduleNameList[:]
            if dialog.ShowModal() == wx.ID_OK:
                for index in dialog.GetSelections():
                    temp_list.remove(self.moduleNameList[index])
                    self.module_list.pop(self.moduleNameList[index])                
                    self.saveFlag = 0  
            self.moduleNameList = temp_list
            self.AddRadio() 
            dialog.Destroy
        else:
            wx.MessageBox("No files to remove","Warning!",style=wx.OK|wx.ICON_EXCLAMATION)   

    def AddRadio(self):
        x = 15
        y = 25
        f = open("design_files/specs/specs.xml",'w')
        f.write("<modules>\n")
        if self.rb:
            self.rb.Destroy()         
        for module in self.moduleNameList:  
            f.write("    <module name =\""+self.module_list[module].name+"\" lang = \"verilog\" file = \"%s\"></module>\n"%(self.module_list[module].path))
        f.write("</modules>")  
        f.close()            
        self.source_pane.SetScrollbars(1,1,200,250+len(self.moduleNameList)*25)
        self.rb = wx.RadioBox(self.source_pane,-1, "",(x,y), wx.DefaultSize, self.moduleNameList, 1,wx.RA_SPECIFY_COLS)
        self.Bind(wx.EVT_RADIOBOX, self.OnRb, self.rb)  
            
    def OnAddConfiguration(self,event):
        if not self.filename:
            wx.MessageBox("No project is open","Error!",style=wx.OK|wx.ICON_EXCLAMATION)
        else :
            dlg = wx.FileDialog(self, "Add system configuration...", os.getcwd(),style=wx.OPEN,wildcard=self.wildcard3)
            if dlg.ShowModal() == wx.ID_OK:
                self.configuration = dlg.GetPath()
            dlg.Destroy()       

    def OnClearTrnc(self,event):
        redir = None
        self.log.Destroy()
        self.log = wx.TextCtrl(self.log_pane,-1,size=(700,100),style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        redir=RedirectText(self.log)
        sys.stdout=redir

    def OnClearPrj(self,event):
        os.system('del design_files\\netlists\\*.ngc /s /q')
        self.State = "0"
        wx.StaticText(self.task_pane,-1,"Resource estimate: Not started",(0,40))
        wx.StaticText(self.task_pane,-1,"Design partitioning: Not started",(0,60))
        wx.StaticText(self.task_pane,-1,"Floorplanning: Not started",(0,80))
        wx.StaticText(self.task_pane,-1,"BitGen: Not started",(0,100))
        self.saveFlag = 0
                

    def OnSave(self,event):
        if not self.filename:
            self.OnSaveAs(event)
        else:
            self.SaveFile()

    def OnSaveAs(self,event):
        dlg = wx.FileDialog(self,"Save project as...",os.getcwd(),style=wx.SAVE|wx.OVERWRITE_PROMPT,wildcard=self.wildcard1)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:
                filename = filename + '.apr'
            self.filename = filename
            self.SaveFile()
            self.SetTitle(self.title+'--'+self.filename)
        dlg.Destroy()

    def OnAbout(self,event):
        dlg = PRestoAbout(self)
        dlg.ShowModal()
        dlg.Destroy()

    def OnHelp(self,event):
        dlg = PRestoAbout(self)
        dlg.ShowModal()
        dlg.Destroy()


    def OnRun(self,event):
        if not self.filename:
            wx.MessageBox("No project is open","Error!",style=wx.OK|wx.ICON_EXCLAMATION)
        else:
            if len(self.moduleNameList):
                if self.State == "0":
                    self.top_module_list = scripts.module_tree_generator.create_module_tree('design_files\specs\specs.xml') #Get the list of top level modules, which are not submodules of other modules
                    if not self.synth: 
                        wx.StaticText(self.task_pane,-1,"Resource estimate: Running...",(0,40))
                        self.saveFlag = 0
                        self.synth = thread.SynthThread(self)   
                elif self.State == "1":
                    if not self.part: 
                        wx.StaticText(self.task_pane,-1,"Partitioning: Running...",(0,60))
                        self.saveFlag = 0
                        self.part = thread.PartitionThread(self)
            else:
                wx.MessageBox("There are no files in the project","Error!",style=wx.OK|wx.ICON_EXCLAMATION)

    def OnAbort(self,event):
        if self.synth:
            wx.MessageBox("Are you sure??","Warning",style=wx.OK|wx.ICON_EXCLAMATION)
            self.synth.abort()

    def OnResult(self, event):
        """Show Result status."""
        if event.data is None:
            wx.StaticText(self.task_pane,-1,"Resource estimate: Aborted",(0,40))
            if self.synth:
                self.synth = None    
        elif event.data is 1:   #This shows the synthesis step is over and all the resource utilisation figures are available
            wx.StaticText(self.task_pane,-1,"Resource estimate: Finished",(0,40))
            f = open("intermediate_files/resources.xml",'w')                    
            f.write("<resources>\n")
            for module in self.top_module_list:
                module_name = module.name
                f.write("    <module name =\"%s\" "%(module_name))
                f.write("SLICEL = \"%s\" SLICEM = \"%s\" DSP = \"%s\" BRAM = \"%s\"></module>\n"%(self.module_list[module_name].slicel,self.module_list[module_name].slicem,self.module_list[module_name].dsp,self.module_list[module_name].bram))
            f.write("</resources>")            
            f.close()
            wx.StaticText(self.task_pane,-1,"Design partitioning: Running...",(0,60))
            self.State = "1"
            self.part = thread.PartitionThread(self)
        elif event.data is 2:
            wx.StaticText(self.task_pane,-1,"Design partitioning: Finished",(0,60))
            wx.StaticText(self.task_pane,-1,"Floorplanning: Running...",(0,80))
            self.State = "2"
            if self.part:
                self.part = None
        elif event.data is 3:
            wx.StaticText(self.task_pane,-1,"Floorplanning: Finished",(0,80))
            wx.StaticText(self.task_pane,-1,"BitGen: Running...",(0,100))
            self.State = "3"
        elif event.data is 4:
            wx.StaticText(self.task_pane,-1,"BitGen: Finished",(0,100))
            self.State = "4"      

    def OnRb(self, event):
        module_name = self.moduleNameList[event.GetInt()]
        if self.synth_stat:
            self.synth_stat.Destroy()
        self.synth_stat = wx.TextCtrl(self.stat_pane,-1,"Resources\nSliceL : " + str(self.module_list[module_name].slicel) + "\nSliceM : " + str(self.module_list[module_name].slicem) + "\nDSP     : " + str(self.module_list[module_name].dsp) + "\nBRAM  : " + str(self.module_list[module_name].bram),
                (10,30),(150,100), wx.TE_READONLY|wx.TE_MULTILINE)

class PRestoAbout(wx.Dialog):
    text = '''
    <html>
        <body bgcolor = "#ACAA60">
            <center><table bgcolor = "#455481" width="100%"cellspacing="0"
            cellpadding="0" border-"1">
            <tr>
                <td align="center"><h1>PResto</h1></td>
            </tr>
            </table>
            </center>
            <p><b>PResto:</b> A tool for automatic generation of partial reconfiguration based systems </b></p>
            <p>Copyright &copy 2012-2013 Vipin K & Suhaib Fahmy, Nanyang Technological University, Singapore</p>
        </body>
    </html>
    '''
    def __init__(self,parent):
        
        wx.Dialog.__init__(self,parent,-1,'About PResto',size=(400,300))
        html = wx.html.HtmlWindow(self)
        html.SetPage(self.text)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(html,1,wx.EXPAND|wx.ALL,5)
        self.SetSizer(sizer)
        self.Layout()

class RedirectText:
    def __init__(self,aWxTextCtrl):
        self.out=aWxTextCtrl

    def write(self,string):
        self.out.WriteText(string)