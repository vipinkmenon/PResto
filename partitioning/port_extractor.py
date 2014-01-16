import re
def port_gen(file):
    f = open(file,'r')
    pattern = '^\s*module\s*(?P<mod>([a-z0-9_,]+)).*$'
    module_name = re.compile(pattern)
    for line in f:
        result = module_name.search(line)
        if result:
            name = result.group('mod')
    f.close()
    f = open(file,'r')
    port_list = []
    pattern = '^\s*(?P<direction>(input|output|inout))\s*(?P<type>(reg|wire))*\s*(?P<port_width>(\\[.*?\\]))*\s*(?P<port_name>([A-Za-z0-9_]+)).*$'
    regexp = re.compile(pattern,re.IGNORECASE|re.DOTALL)
    for line in f:
        result = regexp.search(line)
        if result:
            port = [result.group('direction'),result.group('type'),result.group('port_width'),result.group('port_name')]
            port_list.append(port)
    f.close()
    return port_list

def data_extract(file):
    f = open(file,'r')
    pattern = '^.*(\\);).*$'
    end_found_flag = 0
    end_port = re.compile(pattern,re.IGNORECASE|re.DOTALL)
    data = ""
    f = open(file,'r')
    for line in f:
        result = end_port.search(line)
        if end_found_flag:
            data += str(line)
        if result:
            end_found_flag = 1
    f.close()
    return data