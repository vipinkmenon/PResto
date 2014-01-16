##############################################################################################################################
#    module     : pre_process                                                                                                #
#    descript   : preprocessing functions for partitioning                                                                   #
#    dependency : base_partition.py,spec.py,pre_process.py,edge.py,node.py,general.py                                        #
#    additional package : math                                                                                               #
#    author     : Vipin.K                                                                                                    #
#                                                                                                                            #
#                                                                                                                            #
##############################################################################################################################
import math

def check_feasibility(fpga_slicel,fpga_slicem,fpga_bram,fpga_dsp,resources,configurations,clb_tile,bram_tile,dsp_tile):
    not_fit_flag = 0
    for i in range (0,len(configurations)):                    #consider each configuration
        slicel  = 0                                            #initialise resource requirement to zero
        slicem  = 0                                            #initialise resource requirement to zero
        bram    = 0
        dsp     = 0
        modules = (configurations[i].find('modules').text).split(',')
        for j in range (0,len(modules)):                    #for each module      
            resource = find_resources(resources,modules[j])       
            slicel+= resource[0]
            slicem+= resource[1]
            dsp+= resource[2]
            bram+= resource[3]
            
        print 'Configuration:',i+1,'SLICEL: ',slicel,'SLICEM: ',slicem,'  BRAM: ',bram,'  DSP: ',dsp #consider the resource requirement in terms of tiles.
            
        if( slicel > fpga_slicel or slicem > fpga_slicem or bram > fpga_bram or dsp > fpga_dsp):      #If any of the configuration can not fit in the FPGA, exit the loop
            print '\n\nDue to configuration',conf[i]
            not_fit_flag = 1
            break

    return not not_fit_flag

def find_resources(resources,module_name):
    for i in range(0,len(resources)):
        if resources[i].get('name') == module_name:
            return [int(resources[i].get('SLICEL')),int(resources[i].get('SLICEM')),int(resources[i].get('DSP')),int(resources[i].get('BRAM'))]


def get_module_list(resources):
    module_list = []
    for module in resources:
        module_list.append(module.get('name'))
    return module_list

def find_arch_spec(arch_spec,fpga_family):
    for arch in arch_spec:
        if arch.get('name') == fpga_family:
            return [int(arch.find('clb_frame').text),int(arch.find('bram_frame').text),int(arch.find('dsp_frame').text),int(arch.find('clb_tile').text),int(arch.find('dsp_tile').text),int(arch.find('bram_tile').text),int(arch.find('frame_size').text)]