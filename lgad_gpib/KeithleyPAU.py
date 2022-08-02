import time

import pylab as plt
import pyvisa

class KeithleyPAU():
    inst = []
    output_on = 0
    delay = 0.005

    def __init__(self, rname):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(rname)
        idn = self.inst.query("*IDN?")
        if '6487' not in idn:
            print ('Incorrect device is assigned...')
            self.inst = []
            return 

        self.initialize()
    
    def print_name(self):
        print(self.inst.query("*IDN?"))

    def reset(self):
        self.output_stat = 0
        self.inst.write("*RST")

    def setzero(self):
        self.inst.write("FUNC 'curr'")
        self.inst.write("SYST:ZCH ON")
        self.inst.write("CURR:RANG 2e-9")
        self.inst.write("INIT")
        self.inst.write("SYST:ZCOR:STAT OFF")
        self.inst.write("SYST:ZCOR:ACQ")
        self.inst.write("SYST:ZCOR ON")
        self.inst.write("CURR:RANG:AUTO ON")
        self.inst.write("SYST:ZCH OFF")

    def initialize(self):
        self.reset()
        #self.setzero()

    def read(self):
        time.sleep(self.delay)
        val = self.inst.query(":READ?")
        val = val.strip()
        val = val.split(',') 
        print (val)
        val1 = []
        for v in val:
            try:
                val1.append(float(v))
            except ValueError:
                val1.append(float(v[:-1])) 
        return val1

    def plot_IV(self, varr, iarr, show=True, ofname=None):
        plt.plot(varr, iarr, '*-')
        plt.xlabel('bias voltage (V)')
        plt.ylabel('current (A)')
        plt.tight_layout()

        if ofname is not None:
            if '.png' not in ofname:
                ofname += ".png"
            plt.savefig(ofname)

        if show:
            plt.show()
