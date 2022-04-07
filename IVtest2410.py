import os
import time
import datetime
#import numpy as np
#import pylab as plt
import pyvisa
import KeithleySMU

rm = pyvisa.ResourceManager()
rlst = rm.list_resources()

k2410 = 0

for r in rlst:
    if "GPIB" in r:
        inst = rm.open_resource(r)
        idn = inst.query("*IDN?")
        if "2410" in idn:
            k2410 = KeithleySMU.KeithleySMU(r)

k2410.print_name()


sensorname = "FBK_2022v1_2x2_13_T9"
npad = 1

v0 = 0
v1 = -250
dv = 1 
if dv:
    nstp = int(abs(v1 - v0)/dv)+1
else:
    nstp = 251

option = ""
option += "_AfterBreakdown"

date = datetime.date.today().isoformat()
opath = f"C:\\Users\\summa\\OneDrive\\Works\\2022-02-07_CMS LGAD\\I-V test"
opath += f"\\{date}_{sensorname}"
try:
    os.mkdir(opath)
except:
    pass
ofname = f"I-V_2410_{sensorname}_PAD{npad}_{time.strftime('%Y-%m-%dT%H.%M.%S')}_{v0}_{v1}{option}"
ofname = opath + "\\" + ofname

dat = k2410.measure_IV(v0, v1, nstp, navg=10, ofname=ofname)
k2410.plot_IV(ofname=ofname)

print("finished!")
print(f"The result has been written in {ofname}.")