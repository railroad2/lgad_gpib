import pylab as plt

import numpy as np


def plot(data, Vreal=False):
    if len(np.shape(data)) == 2:
        plot(np.array([data]))
    
    for i, d in enumerate(data):
        if Vreal:
            xidx = 2
        else:
            xidx = 0

        plt.plot(d[xidx], d[1], '*-', label=f'PAD #{i+1}')

    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (A)')
    plt.legend()
    plt.tight_layout()
    plt.show()
    return

def readdata(flist, pathbase=""):
    data = []

    for fn in flist:
        print (fn)
        datatmp = np.genfromtxt(pathbase + "\\" + fn)
        data.append(datatmp.T)

    data = np.array(data)
    return data


if __name__=="__main__":
    pathbase = r"C:\Users\summa\OneDrive\Works\2022-02-07_CMS LGAD\I-V test\2022-04-06_FBK_2022v1_2x2_13"
    
    """
    flist_IV = [
        "I-V_2410_FBK_2022v1_2x2_13_PAD1_2022-04-06T15.16.21_0_-250_FloatingLO.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD2_2022-04-06T15.18.48_0_-250_FloatingLO.txt",
        #"I-V_2410_FBK_2022v1_2x2_13_PAD3_2022-04-06T15.19.55_0_-250_FloatingLO.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD3_2022-04-06T15.10.31_0_-250_LOFLOAT.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD4_2022-04-06T15.24.49_0_-250_FloatingLO.txt" ]
    """
    flist_breakdown = [
        "I-V_2410_FBK_2022v1_2x2_13_PAD1_2022-04-06T15.54.52_0_-400_Breakdown.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD2_2022-04-06T15.59.50_0_-400_Breakdown.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD3_2022-04-06T16.01.43_0_-400_Breakdown.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD4_2022-04-06T16.02.51_0_-400_Breakdown.txt",
    ]

    data = readdata(flist_breakdown, pathbase)
    print(data.shape)
    plot(data, True)
