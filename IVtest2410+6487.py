import time
import numpy as np
import pylab as plt
import pyvisa
import KeithleySMU
import KeithleyPAU


def measure_IV(vstart, vstop, npts, sensorname="", ofname=None, option="", npad=0, opath='./'):
    rm = pyvisa.ResourceManager()
    rlst = rm.list_resources()

    k2410 = 0
    k6487 = 0

    for r in rlst:
        if "GPIB" in r:
            inst = rm.open_resource(r)
            idn = inst.query("*IDN?")
            if "2410" in idn:
                k2410 = KeithleySMU.KeithleySMU(r)
            if "6487" in idn:
                k6487 = KeithleyPAU.KeithleyPAU(r)

    k2410.print_name()
    k6487.print_name()

    ofname = f"I-V_2410+6487_{sensorname}_{npad}_{time.strftime('%Y-%m-%dT%H.%M.%S')}_{v0}_{v1}{option}"
    ofname = opath + "\\" + ofname

    varr = np.linspace(vstart, vstop, npts)
    varr_meas = []
    iarr = []
    k2410.set_source_volt(0)
    k2410.output_on()

    v6487_arr = []
    for v in varr:
        v_meas, i = k2410.read()
        i6487 = k6487.read()
        print (v, i, v_meas, i6487)
        varr_meas.append(v_meas)
        iarr.append(i)

    k2410.output_off()

    if ofname is not None:
        if '.txt' not in ofname:
            ofname += ".txt"

        data = np.array([varr, iarr, varr_meas]).T
        hdr = "V_set, I_meas, V_meas,"
        np.savetxt(ofname, data, header=hdr)


    #k2410.plot_IV(ofname=ofname)

if __name__=="__main__":
    #opath = r"C:\Users\summa\OneDrive\Works\2022-02-07_CMS LGAD\I-V test\2022-03-15 HPK 5x5"
    v0 = 0
    v1 = -100
    npts = 11

    measure_IV(v0, v1, npts) 