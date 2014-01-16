from threading import *
import scripts.make_xst_prj
import scripts.module_tree_generator
import scripts.check_script
import scripts.implement
import os
import wx
import shutil
from partitioning import partition_top
import time


EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class SynthThread(Thread):
    """Worker Thread Class."""
    def __init__(self,frame):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._want_abort = 0
        self.post_frame = frame
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        #Check whether the temp folders already exists If temp folders are there, remove
        os.system('IF EXIST xst (rmdir xst /s /q)')
        #Then recreate the required temp folders
        os.makedirs('xst')
        os.makedirs('xst\projnav.tmp')
        #Parse the XML file to the project generator
        project_name = scripts.make_xst_prj.make_prj('design_files\specs\specs.xml')        #Create the project file from the design specification   
        for module in self.post_frame.top_module_list:
            if not self._want_abort:    
                try:                                                              #Check whether the netlist is already generated
                    with open ('design_files/netlists/'+module.name+'.ngc'):
                        if self.post_frame.module_list[module.name].src_tstamp == time.ctime(os.path.getmtime(self.post_frame.module_list[module.name].path)):  #check whether source file has modified after being added to the project
                           pass
                        else:                        
                            xst_proj = scripts.make_xst_prj.make_xst_prj(project_name,module.name)   #For each module in the top module, create a new xst file
                            print "Running XST for %s...."%(module.name)
                            #self.post_frame.log_file.write("Running XST for %s...."%(module.name))
                            os.system('xst -ifn %s -intstyle ise'%(xst_proj+'.xst'))      #Call XST with the xst project as the input argument 
                            stat = scripts.check_script.check_stat(xst_proj+'.srp')
                            if not stat:
                                wx.PostEvent(self.post_frame, ResultEvent(None))
                                print "Synthesis Error"
                                return
                            print "Finished synthesis...."
                            os.system("ngc2edif -mdp2sp -w -secure %s %s"%(module.name+'.ngc','design_files\\netlists\\'+module.name+'.edf'))
                            shutil.copyfile(module.name+'.ngc','design_files/netlists/'+module.name+'.ngc')
                            if not self._want_abort: 
                                resource_list = scripts.check_script.check_resource(module.name+'.srp') #Check resource utilisation after MAP                        
                                print "SLICEM = %s SLICEL = %s DSP = %s BRAM = %s"%(resource_list[0],resource_list[1],resource_list[2],resource_list[3])   
                                self.post_frame.module_list[module.name].slicem =  str(resource_list[0])
                                self.post_frame.module_list[module.name].slicel =  str(resource_list[1])
                                self.post_frame.module_list[module.name].dsp    =  str(resource_list[2])
                                self.post_frame.module_list[module.name].bram   =  str(resource_list[3])
                                self.post_frame.module_list[module.name].nlist_tstamp =  time.ctime(os.path.getmtime('design_files/netlists/'+module.name+'.ngc'))
                                self.post_frame.module_list[module.name].src_tstamp   =  time.ctime(os.path.getmtime(self.post_frame.module_list[module.name].path))                                
                            else:
                                wx.PostEvent(self.post_frame, ResultEvent(None))
                                print "aborted"
                                return                       
                except:                                                           #If there is no netlist, run synthesis           
                    xst_proj = scripts.make_xst_prj.make_xst_prj(project_name,module.name)   #For each module in the top module, create a new xst file
                    print "Running XST for %s...."%(module.name)
                    #self.post_frame.log_file.write("Running XST for %s...."%(module.name))
                    os.system('xst -ifn %s -intstyle ise'%(xst_proj+'.xst'))      #Call XST with the xst project as the input argument 
                    stat = scripts.check_script.check_stat(xst_proj+'.srp')
                    if not stat:
                        wx.PostEvent(self.post_frame, ResultEvent(None))
                        print "Synthesis Error"
                        return
                    print "Finished synthesis...."
                    os.system("ngc2edif -mdp2sp -w -secure %s %s"%(module.name+'.ngc','design_files\\netlists\\'+module.name+'.edf'))
                    shutil.copyfile(module.name+'.ngc','design_files/netlists/'+module.name+'.ngc')
                    if not self._want_abort: 
                        resource_list = scripts.check_script.check_resource(module.name+'.srp') #Check resource utilisation after MAP                        
                        print "SLICEM = %s SLICEL = %s DSP = %s BRAM = %s"%(resource_list[0],resource_list[1],resource_list[2],resource_list[3])   
                        self.post_frame.module_list[module.name].slicem =  str(resource_list[0])
                        self.post_frame.module_list[module.name].slicel =  str(resource_list[1])
                        self.post_frame.module_list[module.name].dsp    =  str(resource_list[2])
                        self.post_frame.module_list[module.name].bram   =  str(resource_list[3])
                        self.post_frame.module_list[module.name].nlist_tstamp =  time.ctime(os.path.getmtime('design_files/netlists/'+module.name+'.ngc'))
                        self.post_frame.module_list[module.name].src_tstamp   =  time.ctime(os.path.getmtime(self.post_frame.module_list[module.name].path)) 
                    else:
                        wx.PostEvent(self.post_frame, ResultEvent(None))
                        print "aborted"
                        return
            else:
                wx.PostEvent(self.post_frame, ResultEvent(None))
                print "aborted"
                return
            #Remove temporary files
        os.system('rmdir xst /s /q')
        os.system('rmdir _xmsgs /s /q')
        os.system('rmdir _ngo /s /q')
        os.system('rmdir xlnx_auto_0_xdb /s /q')
        wx.PostEvent(self.post_frame, ResultEvent(1))
        #stat = partition_top.design_partition(self.post_frame)
        os.system('del *.ngc *.ngd *.pcf *.ncd *.mrp *.xrpt *.ngm *.bld *.srp *.ngr *.lso *.bgn *.drc *.map *.xst *.pad *.par *.ptwx *.csv *.html *.log *.xpi *.unroutes *.txt *.xwbt *.xml *.prj')
        print "done"
        

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1
        
        
        
class PartitionThread(Thread):
    """Worker Thread Class."""
    def __init__(self,frame):
        """Init partition Thread Class."""
        Thread.__init__(self)
        self._want_abort = 0
        self.post_frame = frame
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        stat = partition_top.design_partition(self.post_frame)
        wx.PostEvent(self.post_frame, ResultEvent(2))