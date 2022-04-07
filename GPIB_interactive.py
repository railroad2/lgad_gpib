import pyvisa

rm = pyvisa.ResourceManager()
rlst = rm.list_resources()

for r in rlst:
    inst = rm.open_resource(r)
    idn = inst.query("*IDN?")
    print (r, idn)

dev = input("Select device to connect: ")

inst = rm.open_resource(dev)

try:
    while True:
        cmd = input("GPIB> ")
        cmd = cmd.strip()
        res = inst.write(cmd)
        if '?' in cmd:
            try:
                res = inst.read()
                print (res)
            except pyvisa.errors.VisaIOError as e:
                print (e)
                continue
                
except KeyboardInterrupt:
    print ('Finishing...')
    rm.close()
    exit()

    
