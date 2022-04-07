import pyvisa

rm = pyvisa.ResourceManager()
rlst = rm.list_resources()

for r in rlst:
    if "GPIB" in r:
        inst = rm.open_resource(r)
        idn = inst.query("*IDN?")
        print (r, idn)