import re
import module_db
from xml.dom import minidom

def check_module_in_module(module_name,module_file,submodule_name):

    f = open(module_file,'r')

    pattern = "^\s*"+submodule_name+".*"
    regexp = re.compile(pattern)
    for line in f:
        result = regexp.search(line)
        if result:
            #print "Module %s is a submodule of %s"%(submodule_name,module_name)
            return True
    f.close()

def create_module_tree(spec_file):
    xmldoc = minidom.parse(spec_file) 
    modules = xmldoc.getElementsByTagName('module')
    module_list = []
    top_module_list = []
    for element in modules :
        module_list.append(module_db.module(element.attributes['lang'].value,element.attributes['name'].value,element.attributes['file'].value))       #create one object for each module

    #Find which is the top most module
    for submodule in module_list:
        for module in module_list: 
            if module.name != submodule.name:
                if check_module_in_module(module.name,module.file,submodule.name) :
                    submodule.is_submodule = 1
                    module.add_submodule(submodule)
    
    for module in module_list: 
        if not module.is_submodule:
            #top_most_module = module
            top_module_list.append(module)
            print "Top Level module is "+module.name
    
    
    #for module in module_list: #Now find modules instantiated in the top module
    #    if check_module_in_module(top_most_module.name,top_most_module.file,module.name) :
    #        top_module_list.append(module)
    #top_module_list.append(top_most_module)  #Finally append the top most module also
    return top_module_list