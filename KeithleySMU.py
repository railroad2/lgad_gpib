from tkinter import W
import numpy as np
import time

import numpy as np
import pylab as plt
import pyvisa

class KeithleySMU():
    inst = []
    onoff = 0
    delay = 0.1

    def __init__(self, rname):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(rname)
        idn = self.inst.query("*IDN?")
        if '24' not in idn:
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
        self.onoff = 0
        self.inst.write("*RST")
        self.inst.write(":SOUR:VOLT:MODE FIXED")
        self.inst.write(":SOUR:VOLT:RANG 1000")
        self.inst.write(":SOUR:VOLT:LEV 0")
        self.inst.write(":SENS:CURR:PROT 100E-6")
        self.inst.write(":SENS:FUNC \"VOLT\"")
        self.inst.write(":SENS:FUNC \"CURR\"")
        #self.inst.write(":SENS:CURR:RANG AUTO")
        self.inst.write(":FORM:ELEM VOLT,CURR")

    def read(self):
        val = self.inst.query(":READ?")
        val = val.strip()
        val = val.split(',') 
        val = [float(v) for v in val]
        return val

    def set_source_volt(self, volt):
        self.inst.write(f":SOUR:VOLT:LEV {volt}")
        time.sleep(self.delay)

    def output_on(self):
        self.inst.write("OUTP ON")
        self.onoff = 1

    def output_off(self):
        self.inst.write("OUTP OFF")
        self.onoff = 0

    def measure_IV(self, vstart, vstop, npts=11, navg=1, ofname=None, reverse=True):
        vset_arr = np.linspace(vstart, vstop, npts)
        if reverse:
            vset_arr = np.concatenate([vset_arr, vset_arr[::-1]])
            
        vmeas_arr = []
        imeas_arr = []
        vstd_arr = []
        istd_arr = []
        self.initialize()
        self.inst.write(":FORM:ELEM VOLT,CURR")
        self.set_source_volt(0)
        self.output_on()

        for vset in vset_arr:
            self.set_source_volt(vset)
            vmeas_list = []
            imeas_list = []
            for i in range(navg):
                vmeas, imeas = self.read()
                vmeas_list.append(vmeas)
                imeas_list.append(imeas)
                
            vmeas = np.average(vmeas_list)
            vstd = np.std(vmeas_list)
            imeas = np.average(imeas_list)
            istd = np.std(imeas_list)
            
            print (vset, vmeas, imeas, vstd, istd)

            vmeas_arr.append(vmeas)
            imeas_arr.append(imeas)
            vstd_arr.append(vstd)
            istd_arr.append(istd)

        self.output_off()
        self.varr = vmeas_arr
        self.iarr = imeas_arr

        if ofname is not None:
            if '.txt' not in ofname:
                ofname += ".txt"

            data = np.array([vset_arr, vmeas_arr, imeas_arr, vstd_arr, istd_arr]).T
            hdr = f"I-V measurement using Keithley 2400, Navg={navg}\n" 
            hdr += f"V_set, V_meas, I_meas, V_std, I_std"
            np.savetxt(ofname, data, header=hdr, fmt="%+.8e")

        return vset_arr, vmeas_arr, imeas_arr

    def plot_IV(self, varr=None, iarr=None, show=True, ofname=None):
        if varr is None:
            varr = self.varr

        if iarr is None:
            iarr = self.iarr

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
