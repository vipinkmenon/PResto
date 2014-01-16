class module:
    def __init__(self,lang,name,file):
        self.name = name
        self.lang = lang
        self.file = file
        self.sub_modules = []
        self.LUTs = 0
        self.FFs  = 0
        self.DSP  = 0
        self.BRAM = 0
        self.is_submodule = 0
    def add_submodule(self,sub_module):
        self.sub_modules.append(sub_module)
    def num_submodule(self):
        return len(self.sub_modules)
    def update_resource(self,luts,ffs,dsp,bram):
        self.LUTs = luts
        self.FFs  = ffs
        self.DSP  = dsp
        self.BRAM = bram