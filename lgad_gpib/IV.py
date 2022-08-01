import numpy as np
import pylab as plt

import KeithleySMU
import KeithleyPAU

from .utils import mkdir, getdate

modes = ['SMU', 'PAU', '2SMU', 'SMU+PAU']

class IV():
    def __init__(self, mode='SMU', outpath='./', measname='test0', sensorname='sensor0', npad=1):
        if mode not in modes:
            print ('Invaild test mode...')
            return -1

        self.mode = mode
        self.outpath = outpath
        self.measname = measname
        self.sensorname = sensorname
        self.npad = npad
        self.print_parameters()
        return 

    def print_parameters(self):
        print (f"mode             : {self.mode}")
        print (f"output path      : {self.outpath}")
        print (f"measurement name : {self.outpath}")
        print (f"sensor name      : {self.sensorname}")
        print (f"output path      : {self.outpath}")

    def set_inst(self, smu_name, smuI_name=None, pau_name=None):
        self.smu_name  = smu_name
        self.smuI_name = smuI_name
        self.pau_name  = pau_name

        self.smu = KeithleySMU.KeithleySMU(smu_name) 

        try:
            self.pau = KeithleyPAU.KeithleyPAU(pau_name)
        except KeithleyPAU.pyvisa.VisaIOError as e:
            print (e)
            if 'PAU' in self.mode: 
                print ('PAU should be assigned for PAU and SMU+PAU mode.')
                return -1

        try:
            self.smuI = KeithleySMU.KeithleySMU(smuI_name) 
        except KeithleySMU.pyvisa.VisaIOError as e:
            print (e)
            if '2SMU' in self.mode: 
                print ('SMUI should be assigned for 2SMU mode.')
                return -1
    
    def measure(self, vstart, vstop, npts, navg, ofname, returnsweep=True, realtimeplot=False):
        self.vstart = vstart
        self.vstop = vstop
        self.npts = npts
        self.navg = navg
        self.ofname = ofname
        self.returnsweep = returnsweep
        self.realtimeplot = realtimeplot

        varr = np.linspace(vstart, vstop, npts)
        if returnsweep:
            varr = np.concatenate([varr, varr[::-1]])

def measure_IV(vstart, vstop, npts=11, navg=1, ofname=None, reverse=True, rtplot=True):
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