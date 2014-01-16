import os
import check_script
def implement(top_module):
    print "Running NGD build...."
    os.system('ngdbuild -intstyle ise -dd _ngo -nt timestamp -i -p %s %s %s'%('xc6vcx75t-ff484-2',top_module+'.ngc',top_module+'.ngd'))
    print "Finished NGD build...."
    stat = check_script.check_stat(top_module+'.bld')
    if not stat:
        return None
    print "Running MAP...."
    os.system('map -intstyle ise -p %s -w -logic_opt off -ol high -t 1 -xt 0 -register_duplication off -r 4 -global_opt off -mt off -ir off -pr off -u -lc off -power off -o %s %s %s'%('xc6vcx75t-ff484-2',top_module+'_map.ncd',top_module+'.ngd',top_module+'.pcf'))
    print "Finished MAP...."
    stat = check_script.check_stat(top_module+'_map.mrp')
    if not stat:
        return None
    return True
    #print "Running PAR....\n"
    #os.system('par -w -intstyle silent -ol high -mt off %s %s %s'%(top_module+'_map.ncd',top_module+'.ncd',top_module+'.pcf'))
    #print "Finished PAR....\n"
    #print "Running BITGEN....\n"                                         #Generate the bitstream
    #os.system('bitgen -intstyle silent -f %s %s'%(top_module+'.ut',top_module+'.ncd'))
    #print "\nFinished BITGEN....\n"