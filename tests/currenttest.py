import os
import sys
import time
sys.path.append(r'C:\Users\summa\OneDrive\Works\2022-02-07_CMS_LGAD\GPIBctrl')
import numpy as np
import pyvisa

smu = []
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
    pau.write("SYST:zch ON")
    pau.write("curr:range 2e-5")
    pau.write("INIT")
    pau.write("syst:zcor:stat off")
    pau.write("syst:zcor:acq")
    pau.write("syst:zch off")
    pau.write("syst:zcor on")

    print (smu.query("*IDN?"))
    print (pau.query("*IDN?"))


init()


def iv_smu_pau():
    V0 = 0
    V1 = -10
    npts = 11

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

    resultpath = r'C:\Users\summa\OneDrive\Works\2022-02-07_CMS_LGAD\I-V_test\measurement2'
    date = '2022-06-29'
    sensorname = 'FBK_2022v1_2x2_55_T10'
    Npad = 2
    header = 'V, Vsmu, Ismu, Ipau'
    ofname = f'I-V_smu+pau_{sensorname}_{date}_{V0}_{V1}_pad{Npad}'
    try:
        os.mkdir(resultpath)
    except:
        pass
    try:
        os.mkdir(os.path.join(resultpath, date+'_'+sensorname))
    except:
        pass

    np.savetxt(os.path.join(resultpath, date+'_'+sensorname, ofname), arr, header=header)


if __name__=='__main__':
    iv_smu_pau()