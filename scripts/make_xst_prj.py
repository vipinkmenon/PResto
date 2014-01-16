from xml.dom import minidom
import sys

def make_prj(spec_file):
    xmldoc = minidom.parse(spec_file)                                         #Parse the specification in xml format
    #topmodule = xmldoc.getElementsByTagName('topmodule') 
    #topmodule_name = topmodule[0].attributes['name'].value 
    modulelist = xmldoc.getElementsByTagName('module')                        #get the list of modules from the spec
    #proj_name =  topmodule_name+'.prj'
    proj_name =  'my_project.prj'                                             #create the project
    f = open(proj_name,'w')
    for module in modulelist :
        f.write("%s work \"%s\"\n"%(module.attributes['lang'].value,module.attributes['file'].value)) #write module language and name into the project file
    f.close()
    return proj_name

def make_xst_prj(proj_name,top_module_name):
    xst_name =  top_module_name+'.xst'
    rf = open('data_base/xst_spec.mt','r')
    xst_spec=rf.read()
    wf = open(xst_name,'w')
    wf.write("set -tmpdir \"xst/projnav.tmp\"\n")
    wf.write("set -xsthdpdir \"xst\"\n")
    wf.write("run\n")
    wf.write("-ifn %s\n"%(proj_name))
    wf.write("-ifmt mixed\n")
    wf.write("-ofn %s\n"%(top_module_name))
    wf.write("-ofmt NGC\n")
    wf.write("-p xc6vlx240t-1-ff1156\n")
    wf.write("-top %s\n"%(top_module_name))
    wf.write(xst_spec)
    rf.close()
    wf.close()
    #f = open('temp.mt','w')
    #f.write(top_module_name)
    #f.close()
    return top_module_name