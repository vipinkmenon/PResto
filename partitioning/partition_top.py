##############################################################################################################################
#    module     : partition_top                                                                                              #
#    descript   : for design partitioning based on PR                                                                        #
#    dependency : base_partition.py                                                                                          #
#    additional package : math                                                                                               #
#    author     : Vipin.K                                                                                                    #
#                                                                                                                            #
#                                                                                                                            #
##############################################################################################################################
   
import pre_process             #pre-processing methods
import math
import xml
import xml.etree.ElementTree as ET
import base_partition
#import wrapper_gen

def design_partition(frame):#frame
    #import design specifications
    arch_spec_tree     = ET.parse('data_base/fpga_arch_spec.xml')          #parse the xml files of fpga architecture,
    fpga_tree          = ET.parse('design_files/specs/target_fpga_spec.xml')        #target FPGA resource availability and
    configuration_tree = ET.parse('design_files/specs/configuration_spec.xml')  #configurations
    resource_tree      = ET.parse('intermediate_files/resources.xml')
    fpga               = fpga_tree.getroot()
    arch_spec          = arch_spec_tree.getroot()
    configurations     = configuration_tree.getroot()
    resources          = resource_tree.getroot()
    module_list        = pre_process.get_module_list(resources)      #contains the list of names of the modules
    num_modules        = len(module_list)
    fpga_slicel        = int(fpga[0].find('slicel').text)
    fpga_slicem        = int(fpga[0].find('slicem').text)
    fpga_bram          = int(fpga[0].find('bram').text)
    fpga_dsp           = int(fpga[0].find('dsp').text)
    fpga_family        = 'v6'
    [clb_frame,bram_frame,dsp_frame,clb_tile,bram_tile,dsp_tile,frame_size] = pre_process.find_arch_spec(arch_spec,fpga_family)   
    fpga_arch          = pre_process.find_arch_spec(arch_spec,fpga_family)   
    #Some basic info printing
    print "Target FPGA                    : ",fpga[0].get('name')
    print 'Maximum Available SLICEL       : ',fpga_slicel
    print 'Maximum Available SlICEM       : ',fpga_slicem
    print 'Maximum Available BRAM         : ',fpga_bram
    print 'Maximum Available DSP          : ',fpga_dsp   
    print 'Total Number of modules        : ',num_modules
    print 'Total Number of configurations : ',len(configurations)
    #frame.log_file.write("Target FPGA                    : ",fpga[0].get('name'))
    #Check implementation feasibility by checking whether largest configuration can fit into the fpga
    print 'Checking design feasibility.....\n'
    print 'Resource requirement for each configuration\n'
    feasible = pre_process.check_feasibility(fpga_slicel,fpga_slicem,fpga_bram,fpga_dsp,resources,configurations,clb_tile,bram_tile,dsp_tile)
    if not feasible:
        print 'Design can not fit in this FPGA\n'                                        
        return 0                                                                              #If not feasible return
    else:
        print '\nResource requirement for the largest configuration is less than or equal to the available resources, hence the design may fit in the FPGA.\n'
    
    fpga_fit_flag = 0                  #flag to indicate whether the partitioning can fit in the FPGA
    all_part_together_flag = 0         #flag indicating all modules should be implemented together for fitting in the FPGA
    final_partition = []               #initialise final partitioning array
    partition_resource = []
    compatibile_set = {}
    bp_list   = []
    tmp_module_list = module_list
    
    
    for module in module_list:
        bp_list.append(base_partition.base_partition(module,1,[module],pre_process.find_resources(resources,module)))
        #print module
    
    print "Checking for initial mergability"
    
    for module in module_list: 
        if bp_list:    
            mergable = base_partition.find_mergability(module,bp_list,configurations)
            if mergable:
                #print "partition ",mergable.name,"and module ",module," can be merged"
                merge_module_partition = base_partition.find_partition(bp_list,module)            
                tmp_modules = [module+'__'+mergable.name]
                tmp_slicel = mergable.slicel + merge_module_partition.slicel
                tmp_slicem = mergable.slicem + merge_module_partition.slicem
                tmp_dsp = mergable.dsp + merge_module_partition.bram
                tmp_bram = mergable.bram + merge_module_partition.dsp
                bp_list.remove(mergable)
                bp_list.remove(merge_module_partition)
                bp_list.append(base_partition.base_partition(module+'__'+mergable.name,1,tmp_modules,[tmp_slicel,tmp_slicem,tmp_dsp,tmp_bram]))  
    #print "After merging"    
    #for partition in bp_list:
    #    print partition.name            
    
    for partition in bp_list:
        tmp_bp_list = bp_list[:]
        tmp_bp_list.remove(partition)
        compatibile_set[partition] =  base_partition.find_compatiable_set(partition,tmp_bp_list,configurations)
        #for i in range (0,len(compatibile_set[partition])):
        #    print 'base partition ',partition.name,' compatiable set',compatibile_set[partition][i].name
    
    print 'Complete static implementation area requirement'
    print '________________________________________'
    partition_resource = base_partition.find_total_area(bp_list)
    print 'SLICEL  :',partition_resource[0],'  SLICEM  :',partition_resource[1],'  DSP  :',partition_resource[2],'  BRAM  :',partition_resource[3]
    
    progress = 1
   
    while progress:                             #iterate until there is no more base partitions in the list
        prev_resource_variance = ["inf","inf","inf","inf"]
        curr_config_time = float("inf")  #initialise the required configuration time to infinity
        progress = 0
        for bp in bp_list:
            #print 'comparing ',bp.name,'with '
            for partition in compatibile_set[bp]:                                 #Take a compariable partition
                #print partition.name
                temp_partition = base_partition.mux_partitions(bp,partition)      #Just create a partition by merging the two
                #print 'resource requirement ','SLICEL  :',temp_partition.slicel,'  SLICEM  :',temp_partition.slicem,'  DSP  :',temp_partition.dsp,'  BRAM  :',temp_partition.bram
                tmp_resource_variance = base_partition.find_resource_variance(bp,partition)       #Find the resource variance for the two partitons
                resource_variance_compare = base_partition.compare_resource_variance(tmp_resource_variance,prev_resource_variance)                               
                if resource_variance_compare < 1:
                    best_partition = temp_partition
                    part1 = bp
                    #print 'partition 1',part1.name
                    part2 = partition
                    #print 'partition 2',part2.name
                    prev_resource_variance = tmp_resource_variance
        #print 'best partitions are ',part1.name,'and ',part2.name
               
        bp_list.remove(part1)       
        bp_list.remove(part2)
        bp_list.append(best_partition)  
        
        #print "After merging"    
        #for partition in bp_list:
        #    print partition.name   
            
        for partition in bp_list:
            #print 'base partition ',partition.name
            tmp_bp_list = bp_list[:]
            tmp_bp_list.remove(partition)
            compatibile_set[partition] =  base_partition.find_compatiable_set(partition,tmp_bp_list,configurations)
            #for i in range (0,len(compatibile_set[partition])):
            #    print ' compatiable set',compatibile_set[partition][i].name
            if compatibile_set[partition]:
                progress = 1    
    
    candidate_partition = bp_list[:]
    print "Final partition"
    print "_________________________________"
    partition_no = 1
    f = open("intermediate_files/partitions.xml",'w')
    f.write("<partitions>\n")
    for i in range(0,len(candidate_partition)):
        if len(candidate_partition[i].modules) > 1:
            f.write("    <partition name = \"partition_%d\" num_modules = \"%d\" modules = \"%s\""%(partition_no,candidate_partition[i].num_modules,candidate_partition[i].modules))
            #wrapper_gen.wrapper_gen(partition_no,candidate_partition[i].modules)
            partition_no += 1
        else:
            f.write("    <partition name = \"%s\" num_modules = \"1\" modules = \"%s\""%(candidate_partition[i].name,candidate_partition[i].name))
        f.write(" SLICEL = \"%s\" SLICEM = \"%s\" DSP = \"%s\" BRAM = \"%s\"></partition>\n"%(candidate_partition[i].slicel,candidate_partition[i].slicem,candidate_partition[i].dsp,candidate_partition[i].bram))
    f.write("</partitions>\n")
    f.close()
    #print "Total reconfiguration time:   ",curr_config_time
    #print 'Total resource utilisation'
    #print '__________________________'
    partition_resource = base_partition.find_total_area(candidate_partition)
    print 'SLICEL  :',partition_resource[0],'SLICEM  :',partition_resource[1],'  DSPs :',partition_resource[2],'  BRAMs  :',partition_resource[3]
    #print 'Total tile utilisation'
    #print '______________________'
    partition_resource = base_partition.find_total_tile_area(candidate_partition,clb_tile,bram_tile,dsp_tile)
    print 'CLB Tiles  :',partition_resource[0],'  DSP Tiles  :',partition_resource[1],'  BRAM Tiles  :',partition_resource[2]
    
if __name__ == '__main__':
    design_partition(None)