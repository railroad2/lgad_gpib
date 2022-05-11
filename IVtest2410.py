import os
import time
import datetime
import signal 

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

def handler(signum, frame):
    print ("User interrupt. Turning off the output ...")
    k2410.output_off()
    print ("WARNING: Please make sure the output is turned off!")

    exit(1)

signal.signal(signal.SIGINT, handler)

sensorname = "FBK_2022v1_2x2_56_T10"
npad = 1

v0 = 0
v1 = -400
dv = 1
navg = 1

if dv:
    nstp = int(abs(v1 - v0) / dv) + 1
else:
    nstp = int(abs(v1 - v0) / 1) + 1

option = ""
option += "_totalCurrent"
option += "_breakdown"

date = datetime.date.today().isoformat()
opath = f"C:\\Users\\summa\\OneDrive\\Works\\2022-02-07_CMS_LGAD\\I-V_test"
opath += f"\\{date}_{sensorname}"

try:
    os.mkdir(opath)
except:
    pass

ofname = f"I-V_2410_{sensorname}_PAD{npad}_{time.strftime('%Y-%m-%dT%H.%M.%S')}_{v0}_{v1}"
if navg > 1:
    ofname += f"_navg{navg}"
ofname += f"{option}"
ofname = opath + "\\" + ofname

t0 = time.time()
dat = k2410.measure_IV(v0, v1, nstp, navg=navg, ofname=ofname, reverse=True, rtplot=False)
t1 = time.time()
print (f"Elapsed time for I-V measurement = {t1-t0} s.")
k2410.plot_IV(ofname=ofname)

print("finished!")
print(f"The result has been written in {ofname}.")
