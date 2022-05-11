# test with keithley 2400
import pyvisa
import time

rm = pyvisa.ResourceManager()
rlist = rm.list_resources()

k2400 = None
k6487 = None

for rl in rlist:
    inst = rm.open_resource(rl)
    idn = inst.query("*IDN?")
    print (idn)
    if "2400" in idn:
        k2400 = inst
    elif "6487" in idn:
        k6487 = inst
    else:
        print (f"New device found: {idn}")

fname = "firsttest.gpib"

with open(fname) as f:
    gpib = f.readlines()

for gi in gpib:
    gi = gi.strip()

print (gpib)
for gi in gpib:
    print (gi.strip())
    g = gi.strip()
    if len(g) > 0:
        k2400.write(g)
        time.sleep(1)

