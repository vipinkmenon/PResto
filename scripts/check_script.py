import re
import math

def check_stat(report):
    f = open(report,'r')

    #Check whether synthesis error is there
    pattern= r"""^\s*Number of errors\s*:\s+(?P<num>\d+).*$"""
    regexp  = re.compile(pattern)
    for line in f:
        result = regexp.search(line)
        if result and int(result.group('num')) > 0:
            f.close()
            return None
    f.close()
    return 1

def check_timing(synth_report):

    f = open(synth_report,'r')
    print "\nTiming Summary\n"
    print "---------------\n"
    pattern = r"""^\s+(Minimum|Maximum) [a-z ]+:.+$"""
    regexp  = re.compile(pattern)

    for line in f:
        result = regexp.search(line)
        if result:
            print line
    f.close()

def check_resource(report):
    f = open(report,'r')
    Slicel = 0;
    Slicem = 0;
    DSP  = 0;
    BRAM = 0;
    pattern = r"""^\s*(?P<type>Number used as Logic|Number used as Memory|RAMB36E1/FIFO36E1s|RAMB18E1/FIFO18E1s|DSP48E1s)\s*:\s*(?P<num>\d{1,3}).*$"""
    regexp = re.compile(pattern)
    for line in f:
        result = regexp.search(line)
        if result:
            if result.group('type') ==  "Number used as Logic":
                Slicel += int(math.ceil((int(result.group('num')))/4.0))
            if result.group('type') ==  "Number used as Memory":
                Slicem += int(math.ceil((int(result.group('num')))/4.0))
            if result.group('type') ==  "RAMB36E1/FIFO36E1s":
                BRAM += int(result.group('num'))*2
            if result.group('type') ==  "RAMB18E1/FIFO18E1s":
                BRAM += int(result.group('num'))
            if result.group('type') ==  "DSP48E1s":
                DSP +=  int(result.group('num'))
    resource_list = (Slicem,Slicel,DSP,BRAM)
    return resource_list
    f.close()

def check_resource_file(resource_file,module_name):
    import xml
    from xml.dom import minidom
    try : 
       xmldoc = minidom.parse(resource_file)                                         #Parse the specification in xml format
    except xml.parsers.expat.ExpatError:
       return
    modulelist = xmldoc.getElementsByTagName('module')                        #get the list of modules from the spec      
    for module in modulelist:
        if module_name == module.attributes['name'].value :
            return[int(module.attributes['CLB'].value),int(module.attributes['DSP'].value),int(module.attributes['BRAM'].value)] #write module language and name into the project file
    return None
