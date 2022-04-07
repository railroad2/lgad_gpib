import pylab as plt
import pyvisa
import KeithleySMU

rm = pyvisa.ResourceManager()
rlst = rm.list_resources()

k2400 = 0

for r in rlst:
    inst = rm.open_resource(r)
    idn = inst.query("*IDN?")
    if "2400" in idn:
        k2400 = KeithleySMU.KeithleySMU(r)

k2400.print_name()
dat = k2400.measure_IV(0, 0.4, 41)

k2400.plot_IV()