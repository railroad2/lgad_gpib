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

pau = []

opathroot = r'C:\LGAD_test\I-V_test'
sensorname = 'FBK_2022v1_2x2_35_T10'
Nmeas = 'measurement2'

Npad = 1

V0 = 0
V1 = -350
npts = 351
return_sweep = True

date = getdate()

def init():
    global pau
    ## initialize lcr and pau
    rm = pyvisa.ResourceManager()
    print (rm.list_resources())
    pau = rm.open_resource('GPIB0::22::INSTR') # 6487

    pau.write("*RST")
    pau.write("curr:range 2e-4")
    pau.write("INIT")
    pau.write("syst:zch off")
    pau.write("SOUR:VOLT:STAT off")
    pau.write("SOUR:VOLT:RANG 500")
    pau.write("SOUR:VOLT:ILIM 2.5e-5")
    pau.write("FORM:ELEM READ,UNIT,STAT,VSO")

    print (pau.query("*IDN?"))


init()

def iv_pau():

    def handler(signum, frame):
        print ("User interrupt. Turning off the output ...")
        pau.write("sour:volt:stat off")
        pau.write("sour:volt 0")
        pau.close()
        print ("WARNING: Please make sure the output is turned off!")

        exit(1)

    signal.signal(signal.SIGINT, handler)

    # voltages start/end


    Varr = np.linspace(V0, V1, npts)
    if return_sweep:
        Varr = np.concatenate([Varr, Varr[::-1]])

    time.sleep(1)
    print ("\n")

    arr = []
    pau.write("sour:volt:stat on")
    for V in Varr:
        pau.write(f':sour:volt {V}')

        Ipau, stat, Vpau = pau.query("READ?").split(',')

        Vpau = float(Vpau)
        Ipau = float(Ipau[:-1])

        print (V, Vpau, Ipau)
        arr.append([V, Vpau, 0, Ipau])

    pau.write(':sour:volt 0')
    pau.write(':sour:volt:stat off')
    pau.close()

    opath = os.path.join(opathroot, Nmeas, f'{date}_{sensorname}')
    mkdir(opath)

    fname = f'IV_PAU_{sensorname}_{date}_{V0}_{V1}_pad{Npad}'
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
    plt.plot(V, I)
    if yrange:
        plt.ylim(yrange)

if __name__=='__main__':
    iv_pau()
    plt.show()