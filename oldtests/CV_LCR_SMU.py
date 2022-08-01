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
sensorname = r'FBK_2022v1_2x2_34_T9'
Npad = 4

V0 = 0 
V1 = -60
npts = 201

V2 = None
V3 = None
npts1 = 101

date = getdate()

def CVmeasurement(freq, return_sweep=True):
    rm = pyvisa.ResourceManager()
    rlist = rm.list_resources()
    print (rlist)

    smu = rm.open_resource('GPIB0::24::INSTR')
    lcr = rm.open_resource('USB0::0x0B6A::0x5346::21436652::INSTR')
    lcr.read_termination = '\n'
    lcr.write_termination = '\n'

    print(smu.query('*IDN?'))
    print(lcr.query('*IDN?'))

    smu.write("SOUR:VOLT:MODE FIXED")
    smu.write("SOUR:VOLT:LEV 0")
    smu.write("SOUR:VOLT:RANG 60")
    smu.write(":SENS:CURR:PROT 100e-6") # compliance = 100 uA
    smu.write(":SENS:FUNC \"VOLT\"")
    smu.write(":SENS:FUNC \"CURR\"")
    smu.write(":FORM:ELEM VOLT,CURR")

    lcr.write(":MEAS:NUM-OF-TESTS 1")
    lcr.write(":MEAS:FUNC1 C")
    lcr.write(":MEAS:FUNC2 R")
    lcr.write(":meas:equ-cct par")
    lcr.write(":MEAS:SPEED med")
    lcr.write(":MEAS:LEV 0.1")
    lcr.write(":MEAS:V-BIAS 0V")
    lcr.write(f":MEAS:FREQ {freq}")

    def handler(signum, frame):
        print ("User interrupt. Turning off the output ...")
        smu.write(":sour:volt:lev 0")
        smu.write("outp off")
        lcr.write(":MEAS:BIAS OFF")
        lcr.write(":MEAS:V-BIAS 0V")
        lcr.close()
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

    Vsmu_arr = []
    Ismu_arr = []
    CV_arr = []
    RV_arr = []

    smu.write(":sour:volt:lev 0")
    smu.write("outp on")
    lcr.write(":MEAS:V-BIAS 0V")
    lcr.write("meas:bias ON")
    time.sleep(1)

    t0 = time.time()
    for Vdc in Varr:
        if Vdc > 0:
            print ("Warning: positive bias is not allowed. Setting DC voltage to 0.")
            Vdc = 0

        smu.write(f':sour:volt:lev {Vdc}')
        time.sleep(0.01)
        Vsmu, Ismu = smu.query(":READ?").split(',')

        Vsmu = float(Vsmu)
        Ismu = float(Ismu)

        res = lcr.query('meas:trig?')
        C0, R0 = res.split(',')
        try:
            C0 = float(C0)
            R0 = float(R0)
        except:
            break

        Vsmu_arr.append(Vsmu)
        Ismu_arr.append(Ismu)
        CV_arr.append(C0)
        RV_arr.append(R0)

        print(Vdc, Vsmu, Ismu, C0, R0)

    t1 = time.time()
    print(f"* Bias sweep of {npts} samples between {V0} and {V1}")
    print(f"   * Return sweep: {return_sweep}")
    print(f"   * Elapsed time = {t1-t0} s")
    smu.write(":sour:volt:lev 0")
    smu.write("outp off")
    smu.close()
    lcr.write(":MEAS:BIAS OFF")
    lcr.write(":MEAS:V-BIAS 0V")
    lcr.close()

    opath = os.path.join(opathroot, Nmeas, f"{date}_{sensorname}")
    mkdir(opath)
    fname = f'CV_LCR+SMU_{sensorname}_{date}_{freq}Hz_pad{Npad}'
    ofname = os.path.join(opath, fname)
    i = 0
    while os.path.isfile(ofname+'.txt'):
        fname = f'CV_LCR+SMU_{sensorname}_{date}_{freq}Hz_pad{Npad}_{i}'
        ofname = os.path.join(opath, fname)
        i += 1

    header = 'Vdc(V)\tC(F)\tR(Ohm)'

    np.savetxt(ofname+'.txt', np.array([Varr, CV_arr, RV_arr]).T, header=header)
    plot_cv(ofname+'.txt', freq) 
    plt.savefig(ofname+'.png')


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
    ax2 = ax1.twinx()
    ax2.plot(V, R, 'x-', color='tab:red')
    ax2.set_ylabel('R (Ohm)', color='tab:red')
    ax2.set_yscale('log')
    ax3 = ax1.twinx()
    ax3.plot(V, 1/(C)**2, 'x-', color='tab:green', markersize=5, linewidth = 0.5, label="$1/C^2$")
    ax3.set_ylabel('$1/C^2 ($F$^{-2})$', color='tab:green')
    ax3.set_yscale('log')

    fig.tight_layout()


def cvtest():
    freq = int(1e3)
    return_sweep = True
    CVmeasurement(freq, return_sweep)
    plt.show()
    return 


if __name__=='__main__':
    cvtest()

    plt.show()
