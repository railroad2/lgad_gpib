import sys
import time
sys.path.append(r'C:\Users\summa\OneDrive\Works\2022-02-07_CMS_LGAD\GPIBctrl')
import numpy as np
import pyvisa

smu = []
smuI = []
pau = []

def init():
    global smu, smuI, pau
    ## initialize lcr and smu
    rm = pyvisa.ResourceManager()
    print (rm.list_resources())
    smu = rm.open_resource('GPIB0::25::INSTR') # 2410
    smuI = rm.open_resource('GPIB0::24::INSTR') # 2400
    pau = rm.open_resource('GPIB0::22::INSTR') # 6487

    smu.write("SOUR:VOLT:MODE FIXED")
    smu.write("SOUR:VOLT:LEV 0")
    smu.write("SOUR:VOLT:RANG 200")
    smu.write(":SENS:CURR:PROT 10e-6")
    smu.write(":SENS:FUNC \"VOLT\"")
    smu.write(":SENS:FUNC \"CURR\"")
    smu.write(":FORM:ELEM VOLT,CURR")

    smuI.write("SOUR:VOLT:MODE FIXED")
    smuI.write("SOUR:VOLT:LEV 0")
    smuI.write("SOUR:VOLT:RANG 200")
    smuI.write(":SENS:CURR:PROT 10e-6")
    smuI.write(":SENS:FUNC \"VOLT\"")
    smuI.write(":SENS:FUNC \"CURR\"")
    smuI.write(":FORM:ELEM VOLT,CURR")

    pau.write("*RST")
    pau.write("SYST:zch ON")
    pau.write("curr:range 2e-5")
    pau.write("INIT")
    pau.write("syst:zcor:stat off")
    pau.write("syst:zcor:acq")
    pau.write("syst:zch off")
    pau.write("syst:zcor on")

    print (smu.query("*IDN?"))
    print (smuI.query("*IDN?"))
    print (pau.query("*IDN?"))


init()


def iv_2smu_pau():
    V0 = 0
    V1 = -300
    npts = 301

    return_sweep = True

    Varr = np.linspace(V0, V1, npts)
    if return_sweep:
        Varr = np.concatenate([Varr, Varr[::-1]])

    smu.write(':sour:volt:lev 0')
    smuI.write(':sour:volt:lev 0')
    smu.write('outp on')
    smuI.write('outp on')

    time.sleep(1)
    print ("\n")

    arr = []
    for V in Varr:
        smu.write(f':sour:volt:lev {V}')

        Vsmu, Ismu = smu.query(":READ?").split(',')
        VsmuI, IsmuI = smuI.query(":READ?").split(',')
        Ipau, _, _ = pau.query("READ?").split(',')

        Vsmu = float(Vsmu)
        Ismu = float(Ismu)
        VsmuI = float(VsmuI)
        IsmuI = float(IsmuI)
        Ipau = float(Ipau[:-1])

        print (V, Vsmu, Ismu, VsmuI, IsmuI, Ipau)
        arr.append([V, Vsmu, Ismu, VsmuI, IsmuI, Ipau])

    smu.write(':sour:volt:lev 0')
    smu.write('outp off')
    smuI.write('outp off')
    smu.close()
    smuI.close()
    pau.close()

    resultpath = r'C:\Users\summa\OneDrive\Works\2022-02-07_CMS_LGAD\I-V_test\measurement2'
    date = '2022-06-29'
    sensorname = 'FBK_2022v1_2x2_55_T10'
    Npad = 2
    ofname = f'I-V_smu+pau_{sensorname}_{date}_{V0}_{V1}_pad{Npad}'
    np.savetxt(os.path.join(resultpath, ofname), arr)


if __name__=='__main__':
    iv_2smu_pau()
