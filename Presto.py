##############################################################################################################################
#    module     : Presto                                                                                                     #
#    descript   : The top most file                                                                                          #
#    dependency : base_partition.py                                                                                          #
#    additional package :                                                                                                    #
#    author     : Vipin.K                                                                                                    #
#                                                                                                                            #
#                                                                                                                            #
##############################################################################################################################

import wx
from gui import gui



class App(wx.App):
    def __init__(self,redirect=False,filename=None):
        wx.App.__init__(self,redirect,filename)

    def OnInit(self):
        self.frame = gui.PrestoFrame(None)
        self.frame.Show(True)
        return True

if __name__=='__main__':
    app = App()
    app.MainLoop()