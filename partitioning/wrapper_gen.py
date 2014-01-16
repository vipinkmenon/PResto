import os
import fileinput
import sys
import re
import port_extractor
import shutil
import scripts

#Function to create wrapper module to the list of input modules
#inputs : list of modules, project_file
#output : wrapper_name.v
def wrapper_gen(partition_no,module_list):
    added_ports = []
    current_ports = []
    partition_name = 'partition_'+str(partition_no)                #give a new name to the module
    for module in module_list:                                                    
        current_ports += port_extractor.port_gen('design_files/verilog/'+module+'.v')
    current_ports.sort()                                          #sort to make sure the smallest port is removed when both have same ports
    temp_ports = []
    for port in current_ports: 
        if not str(port[3]) in added_ports: 
            temp_ports.append(port)                        
            added_ports.append(str(port[3]))
    current_ports = temp_ports[:]
    for module in module_list:
        port_count = 1
        os.system('mkdir design_files\\verilog\\partitions\\%s\\%s'%(partition_name,module))      #create a directory to store the partition file
        f = open('design_files/verilog/partitions/'+partition_name+'/'+module+'/'+partition_name+'.v','w')      #create the wrapper file. always in verilog format
        f.write("module %s(\n"%(partition_name))                       #module declaration
        for port in current_ports:
            direction = str(port[0])
            if port[1]:
                type = str(port[1])
            else:
                type = " "
            if port[2]:
                size = str(port[2])
            else:
                size = " "
            name = str(port[3])
            if port_count != len(current_ports):
                f.write(direction+'  '+type+'  '+size+'  '+name+',\n')
                port_count += 1
            else:
                f.write(direction+'  '+type+'  '+size+'  '+name+'\n'+');\n')
        data = port_extractor.data_extract('design_files/verilog/'+module+'.v')
        f.write(data)                                            #add endmodule statement at the end of the wrapper
        f.close()
        f = open('temp_prj.prj','w')
        g = open('my_project.prj','r')
        source_files = g.read()
        g.close()
        f.write(source_files)
        f.write("verilog work \"%s\"\n"%('design_files/verilog/partitions/'+partition_name+'/'+module+'/'+partition_name+'.v')) #write module language and name into the project file
        f.close()
        os.system('IF EXIST xst (rmdir xst /s /q)')
        os.makedirs('xst')
        os.makedirs('xst\projnav.tmp')
        xst_proj = scripts.make_xst_prj.make_xst_prj('temp_prj.prj',partition_name)
        print "Running XST for %s...."%(partition_name)
        os.system('xst -ifn %s -intstyle ise'%(xst_proj+'.xst'))
        stat = scripts.check_script.check_stat(xst_proj+'.srp')
        os.system('mkdir design_files\\netlists\\partitions\\%s\\%s'%(partition_name,module))
        os.system("ngc2edif -mdp2sp -w -secure %s %s"%(partition_name+'.ngc','design_files\\netlists\\partitions\\'+partition_name+'\\'+module+'\\'+partition_name+'.edf'))
        shutil.copyfile(partition_name+'.ngc','design_files/netlists/partitions/'+partition_name+'/'+module+'/'+partition_name+'.ngc')