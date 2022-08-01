import os
import sys
import time
import pathlib

sys.path.append(pathlib.Path(__file__).parent.resolve())

import numpy as np
import pyvisa
import pylab as plt
import signal
from util import mkdir, getdate

smu = []
smuI = []
pau = []

opathroot = r'C:\LGAD_test\I-V_test'
sensorname = 'FBK_2022v1_2x2_13_T9'
Nmeas = 'test'

Npad = 1

V0 = 0
V1 = -250
npts = 251
return_sweep = False

date = getdate()

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
    smu.write(":SENS:CURR:PROT 100e-6") # compliance = 100 uA
    smu.write(":SENS:FUNC \"VOLT\"")
    smu.write(":SENS:FUNC \"CURR\"")
    smu.write(":FORM:ELEM VOLT,CURR")

    pau.write("*RST")
    #pau.write("SYST:zch ON")
    #pau.write("curr:range 2e-4")
    pau.write("curr:range auto")
    pau.write("INIT")
    #pau.write("syst:zcor:stat off")
    #pau.write("syst:zcor:acq")
    pau.write("syst:zch off")
    #pau.write("syst:zcor on")

    print (smu.query("*IDN?"))
    print (pau.query("*IDN?"))


init()

def iv_smu_pau():

    def handler(signum, frame):
        print ("User interrupt. Turning off the output ...")
        smu.write(':sour:volt:lev 0')
        smu.write('outp off')
        smu.close()
        pau.close()
        print ("WARNING: Please make sure the output is turned off!")

        exit(1)

    signal.signal(signal.SIGINT, handler)

    # voltages start/end


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

    opath = os.path.join(opathroot, Nmeas, f'{date}_{sensorname}')
    mkdir(opath)

    fname = f'IV_SMU+PAU_{sensorname}_{date}_{V0}_{V1}_pad{Npad}'
    ofname = os.path.join(opath, f'{fname}')
    k=0
    while (os.path.isfile(ofname)):
        ofname = f'{ofname}_{k}'
        k += 1

    np.savetxt(ofname+'.txt', arr)
    ivplot(arr)
    plt.savefig(ofname+'.png')
    plt.figure()
    ivplot(arr, yrange=(-2e-8, 0.5e-8))
    plt.savefig(ofname+'_zoom.png')

def ivplot(arr, yrange=None):
    arr = np.array(arr).T
    V = arr[0]
    I = arr[3]
    I[I>1e37] = min(I)
    plt.plot(arr[0], arr[3])
    if yrange:
        plt.ylim(yrange)

if __name__=='__main__':
    iv_smu_pau()
    plt.show()