# test LCR meter
import os
import numpy as np
import pylab as plt
import pyvisa
import time
import signal
import matplotlib as mp

mp.rcParams.update({'font.size':15})

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
    inst.write(":MEAS:FUNC2 D")
    inst.write(":meas:equ-cct par")
    inst.write(":MEAS:SPEED slow")
    inst.write(":MEAS:LEV 0.1")
    inst.write(":MEAS:V-BIAS 0V")
    inst.write(f":MEAS:FREQ {freq}")

    def handler(signum, frame):
        print ("User interrupt. Turning off the output ...")
        inst.write(":MEAS:V-BIAS 0V")
        inst.write(":MEAS:BIAS OFF")
        inst.close()
        print ("WARNING: Please make sure the output is turned off!")

        exit(1)

    signal.signal(signal.SIGINT, handler)

    ## C-V
    V0 = 0
    V1 = -40
    npts = 41
    Varr = np.linspace(V0, V1, npts)
    if return_sweep:
        Varr = np.concatenate([Varr, Varr[::-1]])

    CV_arr = []
    RV_arr = []

    inst.write("meas:bias ON")
    time.sleep(1)
    t0 = time.time()
    for Vdc in Varr:
        inst.write(f':MEAS:V-BIAS {Vdc}V')
        time.sleep(0.01)
        res = inst.query('meas:trig?')

        #res = res[:-1]
        C0, R0 = res.split(',')
        try:
            C0 = float(C0)
            R0 = float(R0)
        except:
            print (C0, R0) 
            C0 = 0
            R0 = 0
            break

        CV_arr.append(C0)
        RV_arr.append(R0)

        print(Vdc, C0, R0)

    t1 = time.time()
    print(f"* Bias sweep of {npts} samples between {V0} and {V1}")
    print(f"   * Return sweep: {return_sweep}")
    print(f"   * Elapsed time = {t1-t0} s")
    inst.write(":MEAS:V-BIAS 0V")
    inst.write(":MEAS:BIAS OFF")
    inst.close()
    
    fname = f'CVtest_{freq}Hz.txt'
    i = 0
    while os.path.isfile(fname):
        fname = f'CVtest_{freq}Hz_{i}.txt'
        i += 1

    header = 'Vdc(V)\tC(F)\tR(Ohm)'
    plt.savetxt(fname, np.array([Varr, CV_arr, RV_arr]).T, header=header)
    plot_cv(fname, freq) 


def CVmeasurement_4fnc(freq):
    rm = pyvisa.ResourceManager()
    rlist = rm.list_resources()
    print (rlist)

    inst = rm.open_resource('USB0::0x0B6A::0x5346::21436652::INSTR')
    inst.read_termination = '\n'
    inst.write_termination = '\n'
    #inst.write('*RST')

    print(inst.query('*IDN?'))
    inst.write(":MEAS:NUM-OF-TESTS 2")
    inst.write(":MEAS:TEST 1")
    inst.write(":MEAS:FUNC1 C")
    inst.write(":MEAS:FUNC2 R")
    inst.write(":meas:equ-cct par")
    inst.write(":MEAS:SPEED med")
    inst.write(":MEAS:LEV 0.1")
    inst.write(":MEAS:V-BIAS 0V")
    inst.write(f":MEAS:FREQ {freq}")

    inst.write(":MEAS:TEST 2")
    inst.write(":MEAS:FUNC1 R")
    inst.write(":MEAS:FUNC2 Z")
    inst.write(":meas:equ-cct ser")
    inst.write(":MEAS:SPEED med")
    inst.write(":MEAS:LEV 0.1")
    inst.write(":MEAS:V-BIAS 0V")
    inst.write(f":MEAS:FREQ {freq}")

    def handler(signum, frame):
        print ("User interrupt. Turning off the output ...")
        inst.write(":MEAS:V-BIAS 0V")
        inst.write(":MEAS:BIAS OFF")
        inst.close()
        print ("WARNING: Please make sure the output is turned off!")

        exit(1)

    signal.signal(signal.SIGINT, handler)

    ## C-V
    V0 = 0
    V1 = -40
    npts = 101
    Varr = np.linspace(V0, V1, npts)

    CV_arr = []
    RV_arr = []
    Rs_arr = []
    Zs_arr = []

    inst.write("meas:bias ON")
    time.sleep(1)
    for Vdc in Varr:
        inst.write(':meas:test 1')
        inst.write(f':MEAS:V-BIAS {Vdc}V')
        inst.write(':meas:test 2')
        inst.write(f':MEAS:V-BIAS {Vdc}V')
        time.sleep(0.01)
        res = inst.query('meas:trig?')

        #res = res[:-1]
        try:
            Cp, Rp, Rs, Zs = res.split(',')
        except ValueError as e:
            print (e)
            print (res)

        try:
            Cp = float(Cp)
            Rp = float(Rp)
            Rs = float(Rs)
            Zs = float(Zs)
        except:
            break

        CV_arr.append(Cp)
        RV_arr.append(Rp)
        Rs_arr.append(Rs)
        Zs_arr.append(Zs)

        print(Vdc, Cp, Rp, Rs, Zs)

    inst.write(":MEAS:V-BIAS 0V")
    inst.write(":MEAS:BIAS OFF")
    inst.close()
    
    fname = f'CVtest_{freq}Hz.txt'
    i = 0
    while os.path.isfile(fname):
        fname = f'CVtest_{freq}Hz_{i}.txt'
        i += 1

    header = 'Vdc(V)\tCp(F)\tRp(Ohm)\tRs(Ohm)\tZs(Ohm)'
    plt.savetxt(fname, np.array([Varr, CV_arr, RV_arr, Rs_arr, Zs_arr]).T, header=header)
    plot_cv(fname, freq) 


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

    inst.write(f":MEAS:V-BIAS {Vdc}V")
    inst.write("meas:bias ON")
    time.sleep(1)
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


    inst.write(":MEAS:BIAS OFF")
    inst.close()
    
    fname = f"CFtest_{Vdc}V.txt"
    i = 0
    while os.path.isfile(fname):
        fname = f"CFtest_{Vdc}V_{i}.txt"
        i+=1

    header = 'Freq(Hz)\tC(F)\tR(Ohm)'
    plt.savetxt(fname, np.array([freqarr, CF_arr, RF_arr]).T, header=header)
    
    plot_cf(fname, Vdc)

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

    #plt.title(f"Frequency = {freq} Hz")
    fig.tight_layout()
    
def cftest():
    Vdc = -10
    CFmeasurement(Vdc)
    plt.show()
    return 

def cvtest():
    freq = int(1e3)
    return_sweep = False
    CVmeasurement(freq, return_sweep)
    #CVmeasurement_4fnc(freq)
    plt.show()
    return 


if __name__=='__main__':
    #cftest()
    cvtest()

    #plot_cv('CVtest_1000Hz_5.txt', freq=1000)
    plt.show()
