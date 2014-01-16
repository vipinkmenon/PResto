##############################################################################################################################
#    module     : base_partition                                                                                             #
#    descript   : base partition class and functions for partitioning                                                        #
#    dependency :                                                                                                            #
#    additional package : math                                                                                               #
#    author     : Vipin.K                                                                                                    #
#                                                                                                                            #
#                                                                                                                            #
##############################################################################################################################

import math

class base_partition:                                  #node class type
    def __init__(self,name,num_modules,modules,resources):
        self.name      = name
        self.num_modules = num_modules
        self.modules   = modules
        self.slicel    = resources[0]
        self.slicem    = resources[1]
        self.dsp       = resources[2]
        self.bram      = resources[3]
        
def find_mergability(in_module,partition_list,configurations):
    not_together = 0
    neighbour_found = 0
    first_neighbour = None
    not_in_conf = 0
    partition_not_in_conf = 0 
    module_not_in_conf = 0
    not_compatiable = 0
    #print 'input module is ',in_module
    for partition in partition_list:                        #Take one partition
        #print partition.name
        #print 'num modules ',str((partition.num_modules))
        #print 'num modules ',str(len(partition.modules))
        for configuration in configurations:                #Take each configuration
            module_list = configuration.find('modules').text.split(',') #Find the modules in the configuration
            part_in_config = check_part_in_config(partition,module_list)            
            if part_in_config and (in_module in module_list):                
                righ_most_module = partition.modules[-1] 
                if module_list.index(righ_most_module) != len(module_list)-1:   #and if the rightmost module in the partition is not the last one in the configuration
                    if module_list[module_list.index(righ_most_module)+1] != in_module:
                        not_compatiable = 1
                else:
                    not_compatiable = 1 
            elif part_in_config and  (in_module not in module_list):                  
                not_compatiable = 1
            elif not part_in_config and  (in_module in module_list): 
                not_compatiable = 1
        if not not_compatiable:   
            #print 'module ',in_module,' and partition ',partition.name,' are mergable'
            return partition
        else:
            not_compatiable = 0
    return None            
        
    
def check_part_in_config(partition,module_list):    
    for module in partition.modules:                #Take each module in the partition
        if module not in module_list:               #If any module in the partition is not in the configuration, no need to check further
            return 0
    return 1        
    
#Function to select a partition from a list of partitions based on the partition name
def find_partition(partitions,module):
    for partition in partitions:
        if partition.name == module:
            return partition

def find_compatiable_set(partition,bp_list,configurations):
    not_compatiable = 0
    compatible_set = []
    for bp in bp_list:    #take a base partition from the partition list
        for module in bp.modules: #for each module in the base partition
            for p_module in partition.modules:    #for each module in the comparing partition
                for configuration in configurations: #for each configuration
                    conf_modules = (configuration.find('modules').text).split(',') #get the modules in the configuration
                    if (module in conf_modules) and (p_module in conf_modules):
                        not_compatiable = 1
        if not not_compatiable:
            compatible_set.append(bp)
        not_compatiable = 0
    return compatible_set
    
def compare_resource_variance(resource1,resource2):
    par1_slicel = resource1[0]
    par1_slicem = resource1[1]
    par1_dsp = resource1[2]
    par1_bram = resource1[3]
    par2_slicel = resource2[0]
    par2_slicem = resource2[1]
    par2_dsp = resource2[2]
    par2_bram = resource2[3]

    if par1_dsp < par2_dsp:
        return 0
    elif par1_dsp == par2_dsp:
        if par1_bram < par2_bram:
            return 0
        elif par1_bram == par2_bram:
            if par1_slicem < par2_slicem:
                return 0
            elif par1_slicem == par2_slicem:
                if par1_slicel < par2_slicel:
                    return 0
                else:
                    return 1
            else:
                return 1
        else:
            return 1
    else:
        return 1



def find_resource_variance (partition1,partition2):
    slicel_variance = abs(partition1.slicel - partition2.slicel)
    slicem_variance = abs(partition1.slicem - partition2.slicem)
    dsp_variance = abs(partition1.dsp - partition2.dsp)
    bram_variance = abs(partition1.bram - partition2.bram)
    return [slicel_variance,slicem_variance,dsp_variance,bram_variance]

def merge_partitions(partition_1,partition_2):
    tmp_name = partition_1.name+'_'+partition_2.name
    tmp_num_modules = partition_1.num_modules + partition_2.num_modules
    tmp_modules = partition_1.modules + partition_2.modules
    tmp_slicel = partition_1.slicel + partition_2.slicel
    tmp_sliced = partition_1.slicem + partition_2.slicem
    tmp_dsp = partition_1.dsp + partition_2.dsp
    tmp_bram = partition_1.bram + partition_2.bram
    return base_partition(tmp_name,tmp_num_modules,tmp_modules,[tmp_slicel,tmp_sliced,tmp_dsp,tmp_bram])
    
    
def mux_partitions(partition_1,partition_2):
    tmp_name = partition_1.name+'___'+partition_2.name
    tmp_num_modules = partition_1.num_modules + partition_2.num_modules
    tmp_modules = partition_1.modules + partition_2.modules
    tmp_slicel = max(partition_1.slicel,partition_2.slicel)
    tmp_sliced = max(partition_1.slicem,partition_2.slicem)
    tmp_dsp = max(partition_1.dsp,partition_2.dsp)
    tmp_bram = max(partition_1.bram,partition_2.bram)
    return base_partition(tmp_name,tmp_num_modules,tmp_modules,[tmp_slicel,tmp_sliced,tmp_dsp,tmp_bram])
    
    
def compare_partitions(temp_partition,prev_best_partition):
    if temp_partition.dsp < prev_best_partition.dsp:
        return temp_partition
    elif temp_partition.dsp == prev_best_partition.dsp:
        if temp_partition.bram < prev_best_partition.bram:
            return temp_partition
        elif temp_partition.bram == prev_best_partition.bram:
            if temp_partition.slicem < prev_best_partition.slicem:
                return temp_partition
            elif temp_partition.slicem == prev_best_partition.slicem:
                if temp_partition.slicel < prev_best_partition.slicem:
                    return temp_partition
                else:
                    return prev_best_partition
            else:
                return prev_best_partition
        else:
            return prev_best_partition
    else:
        return prev_best_partition


def find_reconfig_time(partition,conf,clb_tile,bram_tile,dsp_tile,clb_frame,bram_frame,dsp_frame):
    reconfig_time = 0
    for i in range (0,len(conf)-1):                  #for each configuration
        for part in partition:                       #take each partition
            if part.num_modules > 1:             #only if multiple base partitions in the region
                module_1 = modes_present_in_conf(part.modules,conf[i])  #if any of the modules in the configuration is present in the region
                if module_1:
                    for j in range(i+1,len(conf)):   #for other configurations
                        module_2 =  modes_present_in_conf(part.modules,conf[j]) #if any module in the configuration is present in the region
                        if module_1 != module_2: #if the modules are different
                            reconfig_time += math.ceil((part.slicem+part.slicel)/float(clb_tile))*clb_frame*2+math.ceil(part.bram/float(bram_tile))*bram_frame+math.ceil(part.dsp/float(dsp_tile))*dsp_frame
    return reconfig_time


def modes_present_in_conf(modules,config):
    conf_modules = (config.find('modules').text).split(',') #get the modules in the configuration
    for module in modules:                              #take each mode present in the region
        if module in conf_modules: #if a module is present in the configuration
            return module
    return None


def find_total_tile_area(partitions,clb_tile,bram_tile,dsp_tile):
    slicel = 0
    slicem = 0
    bram   = 0
    dsp    = 0
    for partition in partitions:
        slicel += partition.slicel
        slicem += partition.slicem
        dsp += partition.dsp
        bram += partition.bram
    clb   = int(math.ceil((slicel+slicem)/float(clb_tile)*2))
    dsp   = int(math.ceil(dsp/float(dsp_tile)))
    bram  = int(math.ceil(bram/float(bram_tile)))
    return [clb,dsp,bram]

#Function to find the total resource requirement for a partition in terms of slices, BRAM and DSP
#input   :   list of partitions
#output  :   Total area for all the partitions in the form of a list
def find_total_area(partitions):
    slicel = 0
    slicem = 0
    bram   = 0
    dsp    = 0
    for partition in partitions:
        slicel += partition.slicel
        slicem += partition.slicem
        dsp    += partition.dsp
        bram   += partition.bram
    return [slicel,slicem,dsp,bram]

def find_total_frames(partitions,clb_tile,bram_tile,dsp_tile,clb_frame,bram_frame,dsp_frame):
    frames = 0
    slicel = 0
    slicem = 0
    bram = 0
    dsp  = 0
    for partition in partitions:
        slicel += partition.slicel
        slicem += partition.slicem
        bram += partition.bram
        dsp  += partition.dsp
    frames = math.ceil(part.clb/float(clb_tile))*clb_frame+math.ceil(part.bram/float(bram_tile))*bram_frame+math.ceil(part.dsp/float(dsp_tile))*dsp_frame
    return frames