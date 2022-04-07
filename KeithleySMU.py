from tkinter import W
import numpy as np
import time

import numpy as np
import pylab as plt
import pyvisa

class KeithleySMU():
    inst = []
    onoff = 0
    delay = 0.005

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
        time.sleep(self.delay)
        val = self.inst.query(":READ?")
        val = val.strip()
        val = val.split(',') 
        val = [float(v) for v in val]
        return val

    def set_source_volt(self, volt):
        self.inst.write(f":SOUR:VOLT:LEV {volt}")

    def output_on(self):
        self.inst.write("OUTP ON")
        self.onoff = 1

    def output_off(self):
        self.inst.write("OUTP OFF")
        self.onoff = 0

    def measure_IV(self, vstart, vstop, npts=11, navg=1, ofname=None):
        varr = np.linspace(vstart, vstop, npts)
        varr_meas = []
        iarr = []
        self.initialize()
        self.inst.write(":FORM:ELEM VOLT,CURR")
        self.set_source_volt(0)
        self.output_on()

        for v in varr:
            self.set_source_volt(v)
            v_meas_list = []
            i_list = []
            for i in range(navg):
                v_meas, i = self.read()
                v_meas_list.append(v_meas)
                i_list.append(i)
                
            v_meas = np.average(v_meas_list)
            i = np.average(i_list)
            v_std = np.std(v_meas)
            i_std = np.std(i_list)
            print (v, i, v_meas, v_std, i_std)

            varr_meas.append(v_meas)
            iarr.append(i)

        self.output_off()
        self.varr = varr
        self.iarr = iarr

        if ofname is not None:
            if '.txt' not in ofname:
                ofname += ".txt"

            data = np.array([varr, iarr, varr_meas]).T
            hdr = "V_set I_meas V_meas"
            np.savetxt(ofname, data, header=hdr)

        return varr, iarr, varr_meas

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
