from http.client import LineTooLong
import os
import numpy as np
import pylab as plt

def fitVbd(V, I, VL0, VL1, IB0, IB1):
    ## breakdown voltage from IV measurements
    VL = V[V>VL0]
    IL = I[V>VL0]
    IL = IL[VL<VL1]
    VL = VL[VL<VL1]
    
    IB = I[I>IB0]
    VB = V[I>IB0]
    VB = VB[IB<IB1]
    IB = IB[IB<IB1]
    plt.figure()
    plt.plot(V, I, '+', linewidth=0.5, markersize=2)
    plt.plot(VL, IL, 'x', linewidth=0.5)
    plt.plot(VB, IB, 'x', linewidth=0.5)
    PL = np.polyfit(VL, IL, deg=1)
    PB = np.polyfit(VB, IB, deg=1)

    lineL = np.poly1d(PL)
    lineB = np.poly1d(PB)
    plt.plot(V, lineL(V), '-', linewidth=0.5)
    plt.plot(VB, lineB(VB), '-', linewidth=0.5)

    mL, bL = PL
    mB, bB = PB

    Vbd = (bB-bL)/(mL - mB)
    Ibd = lineL(Vbd) 
    plt.plot(Vbd, Ibd, 'o')

    return Vbd

def fitVd(V, C, VL0, VL1, VD0, VD1, VF0, VF1):
    ## depletion voltages from CV measurements
    plt.figure()
    plt.plot(V, 1/C**2, '+', markersize=2)
    VL = V[V>VL0]
    CL = C[V>VL0]
    CL = CL[VL<VL1]
    VL = VL[VL<VL1]

    VF = V[V>VF0]
    CF = C[V>VF0]
    CF = CF[VF<VF1]
    VF = VF[VF<VF1]

    if (VD0 is None) or (VD1 is None):
     #   CD0 = np.average(CL) / 10         #for b/w 40 and 60
     #   CD1 = np.average(CF) /0.9         #for b/w 40 and 60
        CD0 = np.average(CL) / 40         #for b/w 20 and 30   ,  when #43 40 -> 30
        CD1 = np.average(CF) / 0.9        #for b/w 20 and 30
        print (CD0, CD1)
        print ("mmmmmmmmmmmmmmmmmmm")
        CD = C[C<CD0]
        VD = V[C<CD0]
        VD = VD[CD>CD1]
        CD = CD[CD>CD1]

    else:
        VD = V[V>VD0]
        CD = C[V>VD0]
        CD = CD[VD<VD1]
        VD = VD[VD<VD1]

    plt.plot(VL, 1/CL**2, 'x')
    plt.plot(VD, 1/CD**2, 'x')
    plt.plot(VF, 1/CF**2, 'x')

    Vgd = 0
    Vfd = 0

    PL = np.polyfit(VL, 1/CL**2, deg=1)
    PD = np.polyfit(VD, 1/CD**2, deg=1)
    PF = np.polyfit(VF, 1/CF**2, deg=1)

    lineL = np.poly1d(PL)
    lineD = np.poly1d(PD)
    lineF = np.poly1d(PF)

    plt.plot(V, lineL(V), linewidth=0.5)
    plt.plot(VD, lineD(VD), linewidth=0.5)
    plt.plot(V, lineF(V), linewidth=0.5)

    mL, bL = PL
    mD, bD = PD
    mF, bF = PF

    Vgd = (bD - bL)/(mL - mD)
    Vfd = (bD - bF)/(mF - mD)

    plt.plot(Vgd, lineD(Vgd), 'o')
    plt.plot(Vfd, lineD(Vfd), 'o')

    return Vgd, Vfd


def doit(Npad):
    date = "2022-06-30"
    sensorname = "FBK_2022v1_2x2_13_T10"

#    ivpathroot ="C:\LGAD_test\I-V_test\measurement2"
    cvpathroot ="C:\LGAD_test\C-V_test\measurement2"

#    ivpath = fr"{ivpathroot}\{date}_{sensorname}"
    cvpath = fr"{cvpathroot}\{date}_{sensorname}"

#    ivfname = f"I-V_smu+pau_{sensorname}_{date}_0_-350_pad{Npad}.txt"
    cvfname = f"CV_{sensorname}_{date}_1000Hz_pad{Npad}.txt"
#    cvfname = f"CV_LCR+PAU_{sensorname}_{date}_1000Hz_pad{Npad}.txt"

#    ivfname = os.path.join(ivpath, ivfname)
    cvfname = os.path.join(cvpath, cvfname)
#    iv = np.genfromtxt(ivfname)
    cv = np.genfromtxt(cvfname)

#    viv = -1*iv.T[1]
#    iiv = -1*iv.T[2]

    vcv = -1*cv.T[0]
    ccv = cv.T[1]

#    Vbd = fitVbd(viv, iiv, VL0=100, VL1=250, IB0=1e-5, IB1=1e-3)
#    plt.savefig(os.path.join(ivpath, f'breakdown_pad{Npad}'))

#    Vgd, Vfd = fitVd(vcv, ccv, VL0=20, VL1=40, VD0=None, VD1=None, VF0=55, VF1=60)  #for b/w 40 and 60
    Vgd, Vfd = fitVd(vcv, ccv, VL0=10, VL1=20, VD0=None, VD1=None, VF0=30, VF1=40)  #for b/w 20 and 30 , sweep up to 40 V
#    Vgd, Vfd = fitVd(vcv, ccv, VL0=10, VL1=20, VD0=None, VD1=None, VF0=30, VF1=60)  #for b/w 20 and 30 , sweep up to 60 V
    plt.savefig(os.path.join(cvpath, f'depletion_pad{Npad}'))

    print ('-'*50)
#    print (f"Breakdown Voltage = {Vbd}")
    print ('-'*50)
    print (f"Gain layer depletion voltage = {Vgd}")
    print (f"Full depletion voltage = {Vfd}")
    print (f"\tBulk depletion voltage = {Vfd - Vgd}")
    print ('-'*50)

#    np.savetxt(os.path.join(ivpath, f'Vbd_pad{Npad}.txt'), [Vbd])
    np.savetxt(os.path.join(cvpath, f'Vd_pad{Npad}.txt'), [[Vgd, Vfd, Vfd-Vgd]], header='gainlayer, full, bulk')



def main():
    for Npad in range(4):
        doit(Npad+1)

if __name__=="__main__":
    main()