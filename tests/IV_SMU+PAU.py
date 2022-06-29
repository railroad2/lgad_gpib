import os
import sys
import time
import datetime
import pathlib
sys.path.append(pathlib.Path(__file__).parent.resolve())
sys.path.append(r'C:\Users\summa\OneDrive\Works\2022-02-07_CMS_LGAD\GPIBctrl')
import numpy as np
import pyvisa
import pylab as plt

smu = []
smuI = []
pau = []

def init():
    global smu, pau
    ## initialize lcr and smu
    rm = pyvisa.ResourceManager()
    print (rm.list_resources())
    smu = rm.open_resource('GPIB0::25::INSTR') # 2410
    pau = rm.open_resource('GPIB0::22::INSTR') # 6487

    smu.write("SOUR:VOLT:MODE FIXED")
    smu.write("SOUR:VOLT:LEV 0")
    smu.write("SOUR:VOLT:RANG 200")
    smu.write(":SENS:CURR:PROT 10e-6")
    smu.write(":SENS:FUNC \"VOLT\"")
    smu.write(":SENS:FUNC \"CURR\"")
    smu.write(":FORM:ELEM VOLT,CURR")

    pau.write("*RST")
    #pau.write("SYST:zch ON")
    pau.write("curr:range 2e-6")
    pau.write("INIT")
    #pau.write("syst:zcor:stat off")
    #pau.write("syst:zcor:acq")
    pau.write("syst:zch off")
    #pau.write("syst:zcor on")

    print (smu.query("*IDN?"))
    print (pau.query("*IDN?"))


init()

def iv_smu_pau():
    V0 = 0
    V1 = -350
    npts = 351

    return_sweep = True

    Varr = np.linspace(V0, V1, npts)
    if return_sweep:
        Varr = np.concatenate([Varr, Varr[::-1]])

    smu.write(':sour:volt:lev 0')
    smu.write('outp on')

    time.sleep(1)
    print ("\n")

    arr = []
    for V in Varr:
        smu.write(f':sour:volt:lev {V}')

        Vsmu, Ismu = smu.query(":READ?").split(',')
        Ipau, _, _ = pau.query("READ?").split(',')

        Vsmu = float(Vsmu)
        Ismu = float(Ismu)
        Ipau = float(Ipau[:-1])

        print (V, Vsmu, Ismu, Ipau)
        arr.append([V, Vsmu, Ismu, Ipau])

    smu.write(':sour:volt:lev 0')
    smu.write('outp off')
    smu.close()
    pau.close()

    opathroot = r'C:\LGAD_test\I-V_test'
    date = datetime.datetime.today().isoformat()[:10]
    sensorname = 'FBK_2022v1_2x2_13_T9'

    mkdir(opathroot)
    mkdir(os.path.join(opathroot, f'{date}_{sensorname}'))

    ivplot(arr)
    Npad = 1
    ofname = f'I-V_smu+pau_{sensorname}_{date}_{V0}_{V1}_pad{Npad}.txt'
    np.savetxt(os.path.join(opathroot, f'{date}_{sensorname}', f'{ofname}'), arr)

def ivplot(arr):
    arr = np.array(arr).T
    plt.plot(arr[0], arr[3])
    plt.show()

def mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

if __name__=='__main__':
    iv_smu_pau()