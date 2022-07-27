# test LCR meter
import os
import numpy as np
import pylab as plt
import pyvisa
import time
import signal
import matplotlib as mp
from util import mkdir, getdate

mp.rcParams.update({'font.size':15})

opathroot = r'C:\LGAD_test\C-V_test' 
Nmeas = r'measurement2'
sensorname = r'FBK_2022v1_2x2_34_T10'
Npad = 1

date = getdate()

def CFmeasurement(Vdc):
    rm = pyvisa.ResourceManager()
    rlist = rm.list_resources()
    print (rlist)

    pau = rm.open_resource('GPIB0::22::INSTR')
    lcr = rm.open_resource('USB0::0x0B6A::0x5346::21436652::INSTR')
    lcr.read_termination = '\n'
    lcr.write_termination = '\n'

    print(pau.query("*IDN?"))
    print(lcr.query('*IDN?'))

    pau.write("*RST")
    pau.write("curr:range 2e-5")
    #pau.write("curr:range auto")
    pau.write("INIT")
    pau.write("syst:zch off")
    pau.write("SOUR:VOLT:STAT off")
    pau.write("SOUR:VOLT:RANG 500")
    pau.write("SOUR:VOLT:ILIM 2.5e-5")
    pau.write("FORM:ELEM READ,UNIT,STAT,VSO")

    lcr.write(":MEAS:FUNC1 C")
    lcr.write(":MEAS:FUNC2 R")
    lcr.write(":MEAS:LEV 0.1")
    lcr.write(":MEAS:V-BIAS 0V")

    ## C-F
    f0 = 20
    f1 = 1e6
    npts = 101
    freqarr = 10**np.linspace(np.log10(f0), np.log10(f1), npts)

    CF_arr = []
    RF_arr = []

    ## applying bias by increasing from 0
    lcr.write(f":MEAS:V-BIAS {0}V")
    lcr.write("meas:bias ON")
    pau.write(":sour:volt 0")
    pau.write(":sour:volt:stat on")
    time.sleep(1)
    for V in np.linspace(0, Vdc, int(abs(0-Vdc)+1)):
        pau.write(f":sour:volt {V}")
        #lcr.write(f":MEAS:V-BIAS {V}V")
        time.sleep(0.1)

    pau.write(f":sour:volt {Vdc}")
    time.sleep(0.1)

    f0 = float(lcr.query('meas:freq?'))

    ## frequency sweep
    f1arr = []
    for freq in freqarr:
        lcr.write(f'meas:freq {freq}')
        time.sleep(0.01)
        f1 = float(lcr.query('meas:freq?'))
        f1arr.append(f1)

        res = lcr.query('meas:trig?')
        res = res[:-1]
        C0, R0 = res.split(',')
        C0 = float(C0)
        R0 = float(R0)
        print(f1, C0, R0)
        CF_arr.append(C0)
        RF_arr.append(R0)


    pau.write("sour:volt 0")
    pau.write("sour:volt:stat off")
    lcr.write(f"meas:freq {f0}")
    lcr.write(":MEAS:BIAS OFF")
    lcr.write(":meas:V-bias 0V")
    lcr.close()
    
    opath = os.path.join(opathroot, Nmeas, f'{date}_{sensorname}')
    fname = f"CFtest_{sensorname}_{date}_{Vdc}V"
    mkdir(opath)
    i = 0
    while os.path.isfile(os.path.join(opath, fname)+'.txt'):
        fname = f"CFtest_LCR_PAU_{sensorname}_{date}_{Vdc}V_{i}"
        i+=1

    ofname = os.path.join(opath, fname)
    header = 'Freq(Hz)\tC(F)\tR(GOhm)'
    plt.savetxt(ofname+'.txt', np.array([f1arr, CF_arr, RF_arr]).T, header=header)
    
    plot_cf(ofname+'.txt', Vdc)
    plt.savefig(ofname+'.png')


def plot_cf(fname, Vdc=None):
    freq, C, R = np.genfromtxt(fname).T
    fig, ax1 = plt.subplots()
    
    ax1.semilogx(freq, C*1e9, 'x-', color='tab:blue')
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('C (nF)', color='tab:blue')
    ax2 = ax1.twinx()
    ax2.semilogx(freq, R,'x-', color='tab:red')
    ax2.set_ylabel('R (GOhm)', color='tab:red')

    plt.title(f"Vdc = {Vdc} V")
    fig.tight_layout()
    
    return

def cftest():
    Vdc = -10
    CFmeasurement(Vdc)
    return 

if __name__=='__main__':
    cftest()

    plt.show()
