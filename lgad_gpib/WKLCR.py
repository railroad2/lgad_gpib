import numpy as np
import time

import numpy as np
import pylab as plt
import pyvisa

class WKLCR():
    inst = []
    onoff = 0
    delay = 0.005

    def __init__(self, rname):
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(rname)
        if ('USB' in rname) or ('usb' in rname):
            self.inst.read_termination = '\n'
            self.inst.write_termination = '\n'

        idn = self.inst.query("*IDN?")
        if 'WAYNE' not in idn:
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
        self.reset()
        self.inst.write(':MEAS:FUNC1 C')
        self.inst.write(':MEAS:FUNC1 R')
        self.inst.write(':MEAS:FREQ 20')
        self.inst.write(':MEAS:LEV 0.1')

    def read(self):
        val = self.inst.query(":READ?")
        val = val.strip()
        val = val.split(',') 
        val = [float(v) for v in val]
        return val

    def set_freq(self, freq):
        self.inst.write(f":MEAS:FREQ {freq}")
        pass

    def check_freq(self, freq):
        return self.inst.query(f":MEAS:FREQ?")

    def set_dc_volt(self, volt):
        ## need implementation
        #self.inst.write(f":meas:volt {volt}")
        time.sleep(self.delay)

    def output_on(self):
        ## need implementation
        #self.inst.write("OUTP ON")
        self.onoff = 1

    def output_off(self):
        ## need implementation
        #self.inst.write("OUTP OFF")
        self.onoff = 0

    def measure_CF(self, fstart, fstop, npts=11, logf=True, navg=1, ofname=None, reverse=False, rtplot=False):
        if logf:
            fset_arr = np.linspace(np.log10(fstart), np.log10(fstop), npts)
            fset_arr = 10**fset_arr
        else:
            fset_arr = np.linspace(fstart, fstop, npts)
        ## need implemetation
        pass

    def measure_CV(self):
        ## need implemetation
        pass

    def measure_IV(self, vstart, vstop, npts=11, navg=1, ofname=None, reverse=True, rtplot=True):
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
         
        if rtplot:
            #plt.ion()
            fig, ax = plt.subplots()
            line1, = ax.plot([0], [0])

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

            if rtplot:
                line1.set_xdata(vmeas)
                line1.set_ydata(imeas)
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.001)

            vmeas_arr.append(vmeas)
            imeas_arr.append(imeas)
            vstd_arr.append(vstd)
            istd_arr.append(istd)

        self.output_off()
        self.varr = vmeas_arr
        self.iarr = imeas_arr
        if rtplot:
            plt.show()

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
