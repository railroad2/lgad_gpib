import os
import numpy as np
import pylab as plt


def label_from_fname(labels):
    labels_new = []
    for l in labels:
        tmp = l.split('_')
        l_new= '_'.join(tmp[2:8])
        labels_new.append(l_new)

    return labels_new 


def plot(data, Vreal=False, labels=[], fmt="*", logx=False, logy=False):
    try:
        if len(np.shape(data)) == 2:
            plot(np.array([data]), labels=labels)
    except ValueError:
        pass
    
    plt.figure(figsize=(16,12))
    
    for i, d in enumerate(data):
        if Vreal:
            xidx = 1
        else:
            xidx = 0

        if logx:
            x = -1*np.log10(-1*d[xidx])
        else:
            x = d[xidx]

        if logy:
            y = -1*np.log10(-1*d[2])
        else:
            y = d[2]

        if len(d) == 5:
            plt.errorbar(x, y, yerr=d[3], fmt=fmt, label=labels[i])
        else:
            if labels is []:
                plt.plot(x, y, fmt=fmt, label=f'PAD #{i+1}')
            else:
                plt.plot(x, y, fmt=fmt, label=labels[i])


    plt.xlabel('Voltage (V)')
    plt.ylabel('Current (A)')
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.tight_layout()
    return

def detect_breakdown(data, labels=None, threshold=-1e-5):
    Vbd = []
    for d in data:
        xs = d[1]
        ys = d[2]
        Vbdtmp = 0
        for x, y in zip(xs, ys):
            if y < threshold:
                Vbdtmp = x
                break
                
        Vbd.append(Vbdtmp)

    print (Vbd)
    return Vbd 


def readdata(flist, pathbase=None):
    data = []

    for fn in flist:
        print (fn)
        if pathbase:
            fn1 = os.path.join(pathbase, fn)
        else:
            fn1 = fn
        datatmp = np.genfromtxt(fn1)
        data.append(datatmp.T)

    #data = np.array(data)
    return data


if __name__=="__main__":
    pathbase = r"C:\Users\summa\OneDrive\Works\2022-02-07_CMS LGAD\I-V test\2022-04-06_FBK_2022v1_2x2_13"

    flist_IV = [
        "I-V_2410_FBK_2022v1_2x2_13_PAD1_2022-04-06T15.16.21_0_-250_FloatingLO.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD2_2022-04-06T15.18.48_0_-250_FloatingLO.txt",
        #"I-V_2410_FBK_2022v1_2x2_13_PAD3_2022-04-06T15.19.55_0_-250_FloatingLO.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD3_2022-04-06T15.10.31_0_-250_LOFLOAT.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD4_2022-04-06T15.24.49_0_-250_FloatingLO.txt" ]

    flist_breakdown = [
        "I-V_2410_FBK_2022v1_2x2_13_PAD1_2022-04-06T15.54.52_0_-400_Breakdown.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD2_2022-04-06T15.59.50_0_-400_Breakdown.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD3_2022-04-06T16.01.43_0_-400_Breakdown.txt",
        "I-V_2410_FBK_2022v1_2x2_13_PAD4_2022-04-06T16.02.51_0_-400_Breakdown.txt",
    ]

    pathbase_T9 = r"C:\Users\summa\OneDrive\Works\2022-02-07_CMS LGAD\I-V test\2022-04-07_FBK_2022v1_2x2_13_T9"
    flist_T9 = [
        "I-V_2410_FBK_2022v1_2x2_13_T9_PAD1_2022-04-07T14.08.55_0_-250.txt",
        "I-V_2410_FBK_2022v1_2x2_13_T9_PAD2_2022-04-07T13.50.06_0_-250.txt",
        "I-V_2410_FBK_2022v1_2x2_13_T9_PAD3_2022-04-07T13.52.16_0_-250.txt",
        "I-V_2410_FBK_2022v1_2x2_13_T9_PAD4_2022-04-07T13.53.09_0_-250.txt",
    ]
    flist_avg = [
        "I-V_2410_FBK_2022v1_2x2_13_T9_PAD1_2022-04-07T14.18.08_0_-250_navg10.txt",
        "I-V_2410_FBK_2022v1_2x2_13_T9_PAD1_2022-04-07T14.26.03_0_-250_navg100.txt",
        "I-V_2410_FBK_2022v1_2x2_13_T9_PAD1_2022-04-07T16.15.28_0_-250_navg100.txt",
    ]
    labels = [
        'avg 10', 
        'avg 100',
        'avg 100 with standard deviation',
    ]

    pathbase_33T10 = r"C:\Users\summa\OneDrive\Works\2022-02-07_CMS LGAD\I-V test\2022-04-11_FBK_2022v1_2x2_33_T10"
    flist_33T10 = [
        "I-V_2410_FBK_2022v1_2x2_33_T10_PAD1_2022-04-11T17.37.59_0_-300.txt",
        "I-V_2410_FBK_2022v1_2x2_33_T10_PAD2_2022-04-11T17.40.10_0_-300.txt",
        "I-V_2410_FBK_2022v1_2x2_33_T10_PAD3_2022-04-11T17.49.43_0_-300.txt",
        "I-V_2410_FBK_2022v1_2x2_33_T10_PAD4_2022-04-11T18.08.53_0_-300.txt"
    ]
    
    pathbase_53T10 = r"C:\Users\summa\OneDrive\Works\2022-02-07_CMS LGAD\I-V test\2022-04-11_FBK_2022v1_2x2_53_T10"
    flist_53T10 = [
        "I-V_2410_FBK_2022v1_2x2_53_T10_PAD1_2022-04-11T18.26.54_0_-300.txt",
        "I-V_2410_FBK_2022v1_2x2_53_T10_PAD2_2022-04-11T18.42.48_0_-300.txt",
        "I-V_2410_FBK_2022v1_2x2_53_T10_PAD3_2022-04-11T18.49.08_0_-300.txt",
        "I-V_2410_FBK_2022v1_2x2_53_T10_PAD4_2022-04-11T18.58.06_0_-300.txt",
    ]

    labels = [
        'PAD #1',
        'PAD #2',
        'PAD #3',
        'PAD #4'
    ]
    data = readdata(flist_53T10, pathbase_53T10)
    print(data.shape)
    plot(data, True, labels=labels)
