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
Npad = 3

V0 = 0 
V1 = -40
npts = 201

V2 = -19
V3 = -24
npts1 = 101

date = getdate()

def CVmeasurement(freq, return_sweep=True):
    rm = pyvisa.ResourceManager()
    rlist = rm.list_resources()
    print (rlist)

    inst = rm.open_resource('USB0::0x0B6A::0x5346::21436652::INSTR')
    inst.read_termination = '\n'
    inst.write_termination = '\n'
    #inst.write('*RST')

    print(inst.query('*IDN?'))
    inst.write(":MEAS:NUM-OF-TESTS 1")
    inst.write(":MEAS:FUNC1 C")
    inst.write(":MEAS:FUNC2 R")
    inst.write(":meas:equ-cct par")
    inst.write(":MEAS:SPEED med")
    inst.write(":MEAS:LEV 0.1")
    inst.write(":MEAS:V-BIAS 0V")
    inst.write(f":MEAS:FREQ {freq}")

    def handler(signum, frame):
        print ("User interrupt. Turning off the output ...")
        inst.write(":MEAS:BIAS OFF")
        inst.write(":MEAS:V-BIAS 0V")
        inst.close()
        print ("WARNING: Please make sure the output is turned off!")

        exit(1)

    signal.signal(signal.SIGINT, handler)

    ## C-V
    Varr = np.linspace(V0, V1, npts)

    if (V2 is not None):
        if (V2 > V1) and (V3 > V1):
            VarrL = Varr[Varr > V2]
            VarrH = Varr[Varr < V3]
            VarrM = np.linspace(V2, V3, npts1)
            Varr = np.concatenate([VarrL, VarrM, VarrH])

    print (Varr)

    if return_sweep:
        Varr = np.concatenate([Varr, Varr[::-1]])

    CV_arr = []
    RV_arr = []

    inst.write("meas:bias ON")
    time.sleep(1)
    t0 = time.time()
    for Vdc in Varr:
        if Vdc > 0:
            print ("Warning: positive bias is not allowed. Setting DC voltage to 0.")
            Vdc = 0

        inst.write(f':MEAS:V-BIAS {Vdc}V')
        time.sleep(0.01)
        res = inst.query('meas:trig?')

        #res = res[:-1]
        C0, R0 = res.split(',')
        try:
            C0 = float(C0)
            R0 = float(R0)
        except:
            break

        CV_arr.append(C0)
        RV_arr.append(R0)

        print(Vdc, C0, R0)

    t1 = time.time()
    print(f"* Bias sweep of {npts} samples between {V0} and {V1}")
    print(f"   * Return sweep: {return_sweep}")
    print(f"   * Elapsed time = {t1-t0} s")
    inst.write(":MEAS:BIAS OFF")
    inst.write(":MEAS:V-BIAS 0V")
    inst.close()

    opath = os.path.join(opathroot, Nmeas, f"{date}_{sensorname}")
    mkdir(opath)
    fname = f'CV_{sensorname}_{date}_{freq}Hz_pad{Npad}'
    ofname = os.path.join(opath, fname)
    i = 0
    while os.path.isfile(ofname+'.txt'):
        fname = f'CVtest_{sensorname}_{date}_{freq}Hz_pad{Npad}_{i}'
        ofname = os.path.join(opath, fname)
        i += 1

    header = 'Vdc(V)\tC(F)\tR(Ohm)'

    np.savetxt(ofname+'.txt', np.array([Varr, CV_arr, RV_arr]).T, header=header)
    plot_cv(ofname+'.txt', freq) 
    plt.savefig(ofname+'.png')



def CFmeasurement(Vdc):
    rm = pyvisa.ResourceManager()
    rlist = rm.list_resources()
    print (rlist)

    inst = rm.open_resource('USB0::0x0B6A::0x5346::21436652::INSTR')
    inst.read_termination = '\n'
    inst.write_termination = '\n'
    #inst.write('*RST')

    print(inst.query('*IDN?'))
    inst.write(":MEAS:FUNC1 C")
    inst.write(":MEAS:FUNC2 R")
    inst.write(":MEAS:LEV 0.1")
    inst.write(":MEAS:V-BIAS 0V")

    ## C-F
    f0 = 20
    f1 = 1e6
    npts = 101
    freqarr = 10**np.linspace(np.log10(f0), np.log10(f1), npts)

    CF_arr = []
    RF_arr = []

    ## applying bias by increasing from 0
    inst.write(f":MEAS:V-BIAS {0}V")
    inst.write("meas:bias ON")
    time.sleep(1)
    for V in np.linspace(0, Vdc, int(abs(0-Vdc)+1)):
        inst.write(f":MEAS:V-BIAS {V}V")
        time.sleep(0.1)

    inst.write(f":MEAS:V-BIAS {Vdc}V")
    time.sleep(0.1)

    f0 = float(inst.query('meas:freq?'))

    ## frequency sweep
    for freq in freqarr:
        inst.write(f'meas:freq {freq}')
        time.sleep(0.01)
        res = inst.query('meas:trig?')

        res = res[:-1]
        C0, R0 = res.split(',')
        C0 = float(C0)
        R0 = float(R0)
        print(freq, C0, R0)
        CF_arr.append(C0)
        RF_arr.append(R0)


    inst.write(f"meas:freq {f0}")
    inst.write(":MEAS:BIAS OFF")
    inst.write(":meas:V-bias 0V")
    inst.close()
    
    opath = os.path.join(opathroot, Nmeas, f'{date}_{sensorname}')
    fname = f"CFtest_{sensorname}_{date}_{Vdc}V"
    mkdir(opath)
    i = 0
    while os.path.isfile(os.path.join(opath, fname)+'.txt'):
        fname = f"CFtest_{sensorname}_{date}_{Vdc}V_{i}"
        i+=1

    ofname = os.path.join(opath, fname)
    header = 'Freq(Hz)\tC(F)\tR(Ohm)'
    plt.savetxt(ofname+'.txt', np.array([freqarr, CF_arr, RF_arr]).T, header=header)
    
    plot_cf(ofname+'.txt', Vdc)
    plt.savefig(ofname+'.png')


def plot_cf(fname, Vdc=None):
    freq, C, R= np.genfromtxt(fname).T
    fig, ax1 = plt.subplots()
    
    ax1.semilogx(freq, C*1e9, 'x-', color='tab:blue')
    ax1.set_xlabel('Frequency (Hz)')
    ax1.set_ylabel('C (nF)', color='tab:blue')
    ax2 = ax1.twinx()
    ax2.semilogx(freq, R,'x-', color='tab:red')
    ax2.set_ylabel('R (Ohm)', color='tab:red')

    plt.title(f"Vdc = {Vdc} V")
    fig.tight_layout()

def plot_cv(fname, freq=None):
    try:
        V, C, R = np.genfromtxt(fname).T
    except:
        V, C, R, Rs, Zs = np.genfromtxt(fname).T
    fig, ax1 = plt.subplots()

    if (V[1] < 0):
        V = -1 * V
    
    ax1.plot(V, C*1e9, 'x-', color='tab:blue', markersize=5, linewidth=0.5, label="$C$")
    ax1.set_xlabel('Bias (V)')
    ax1.set_ylabel('C (nF)', color='tab:blue')
    #ax2 = ax1.twinx()
    #ax2.plot(V, R, 'x-', color='tab:red')
    #ax2.set_ylabel('R (Ohm)', color='tab:red')
    #ax2.set_yscale('log')
    ax3 = ax1.twinx()
    ax3.plot(V, 1/(C)**2, 'x-', color='tab:green', markersize=5, linewidth = 0.5, label="$1/C^2$")
    ax3.set_ylabel('$1/C^2 ($F$^{-2})$', color='tab:green')
    ax3.set_yscale('log')

    fig.tight_layout()

    
def cftest():
    Vdc = -10
    CFmeasurement(Vdc)
    plt.show()
    return 


def cvtest():
    freq = int(1e3)
    return_sweep = True
    CVmeasurement(freq, return_sweep)
    plt.show()
    return 


if __name__=='__main__':
    #cftest()
    cvtest()

    plt.show()
