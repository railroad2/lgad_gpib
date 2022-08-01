import numpy as np
import time

import numpy as np
import pyvisa

class WKLCR():
    inst = []
    onoff = 0
    srcdelay = 0.1
    Vdc = 0
    vstep = 1

    def __init__(self, rname):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(rname)
        if ('USB' in rname) or ('usb' in rname):
            self.inst.read_termination = '\n'
            self.inst.write_termination = '\n'

        self.rname = rname
        self.idn = self.inst.query("*IDN?")
        if ('WAYNE KERR' not in self.idn):
            print ('Incorrect device is assigned...')
            self.inst = []
            return 
            
        self.initialize()
    
    def print_name(self):
        print(self.inst.query("*IDN?"))

    def reset(self):
        self.onoff = 0
        self.inst.write("*RST")

    def initialize(self): 
        self.reset()
        self.inst.write(":MEAS:NUM-OF-TESTS 1")
        self.inst.write(':MEAS:FUNC1 C')
        self.inst.write(':MEAS:FUNC2 R')
        self.inst.write(':MEAS:FREQ 1000')
        self.inst.write(':MEAS:LEV 0.1')
        self.inst.write(':MEAS:SPEED MED')

    def read(self):
        val = self.inst.query(":READ?")
        val = val.strip()
        val = val.split(',') 
        val = [float(v) for v in val]
        return val

    def set_freq(self, freq):
        self.inst.write(f":MEAS:FREQ {freq}")
        pass

    def get_freq(self, freq):
        return self.inst.query(f":MEAS:FREQ?")

    def set_source_volt(self, vset):
        if self.onoff:
            vcurr = self.get_source_volt()
            vdiff = vset - vcurr
            if abs(vdiff) > 5:
                self._set_source_volt_slow(vset)

        self.inst.write(f":MEAS:V-BIAS {vset}V")
        self.Vdc = vset
        time.sleep(self.srcdelay)

    def get_source_volt(self):
        return float(self.inst.query(f":MEAS:V-BIAS?"))

    def output_on(self):
        vset = self.get_source_volt()
        self.set_source_volt(0)
        self.onoff = 1

        if self.get_source_volt() == 0:
            self.inst.write(":MEAS:BIAS ON")
        else:
            self.set_source_volt(0)
            self.inst.write(":MEAS:BIAS ON")

        self.set_source_volt(vset)

    def output_off(self):
        if self.get_source_volt() == 0:
            self.inst.write(":MEAS:BIAS OFF")
        else:
            self.set_source_volt(0)
            self.inst.write(":MEAS:BIAS OFF")
        self.onoff = 0
    
    def _set_source_volt_slow(self, vset):
        if  self.onoff == 0:
            print("Please turn the output on first. Terminating...")
            return -1

        print ("Please wait. Sweeping the dc voltage...")
        vcurr = self.get_source_volt()
        vstep = self.vstep * np.sign(vset - vcurr) 
        varr = np.arange(vcurr, vset, vstep)
        for v in varr:
            self.inst.write(f":SOUR:VOLT:LEV {v}")
            self.vcurr = v
            time.sleep(self.srcdelay)

        self.inst.write(f":SOUR:VOLT:LEV {vset}")

        return 0
