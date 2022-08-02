import numpy as np
import time

import numpy as np
import pylab as plt
import pyvisa

class KeithleySMU():
    inst = []
    onoff = 0
    srcdelay = 0.01
    vjump_max = 10
    vstep = 1

    def __init__(self, rname):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(rname)

        idn = self.inst.query("*IDN?")
        if 'MODEL 24' not in idn:
            print ('The assigned device is not Keithley 2400 series SMU...')
            self.inst = []
            return -1
            
        self.rname = rname
        self.initialize()
    
    def print_name(self):
        print(self.inst.query("*IDN?"))

    def reset(self):
        self.onoff = 0
        self.inst.write("*RST")

    def initialize(self):
        self.reset()
        self.inst.write(":SOUR:VOLT:MODE FIXED")  # voltage fixed mode. 
        self.inst.write(":SOUR:VOLT:RANG 20")     # voltage range
        self.inst.write(":SOUR:VOLT:LEV 0")       # voltage output level
        self.inst.write(":SENS:CURR:PROT 100E-6") # current compliance, 100 uA by default
        self.inst.write(':SENS:FUNC "VOLT"')      # voltage will be measured
        self.inst.write(':SENS:FUNC "CURR"')      # current will be measured
        self.inst.write(":FORM:ELEM VOLT,CURR")   # output format is (voltage, current). Both are measured values. 

    def read(self):
        val = self.inst.query(":READ?")
        val = val.strip()
        val = val.split(',') 
        val = [float(v) for v in val]

        return val

    def set_source_range(self, vset):
        self.inst.write(f":SOUR:VOLT:RANG {vset}")

    def set_compliance(self, iset):
        if iset > 100e-6:
            print ("Warning: You're trying to set the compliance too high. Please consider to reduce it.")

        self.inst.write(f":SENS:CURR:PROT {iset}")

    def get_source_volt(self):
        return float(self.inst.query(":SOUR:VOLT:LEV?"))

    def set_source_volt(self, vset):
        vcurr = self.get_source_volt()
        if abs(vset - vcurr) > self.vjump_max:
            self._set_source_volt_slow(vset)

        self.inst.write(f":SOUR:VOLT:LEV {vset}")
        self.vcurr = vset
        time.sleep(self.srcdelay)

        return 

    def output_on(self):
        if abs(self.vcurr) > self.vjump_max:
            self.inst.write(":SOUR:VOLT:LEV 0")
            time.sleep(self.srcdelay)
            self.set_source_volt(self, self.vcurr)
        self.inst.write("OUTP ON")
        self.onoff = 1

        return 0

    def output_off(self):
        self.inst.write("OUTP OFF")
        self.onoff = 0

        return 0

    def _set_source_volt_slow(self, vset):
        if self.onoff == 0:
            print("Please turn the output on first. Terminating...")
            return -1

        print ("Please wait. Sweeping the source voltage...")
        vcurr = self.get_source_volt()
        vstep = self.vstep * np.sign(vset - vcurr) 
        varr = np.arange(vcurr, vset, vstep)
        for v in varr:
            self.inst.write(f":SOUR:VOLT:LEV {v}")
            self.vcurr = v
            time.sleep(self.srcdelay)

        return 0
