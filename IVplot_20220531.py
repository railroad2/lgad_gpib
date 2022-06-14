import os
import numpy as np
import pylab as plt

import matplotlib

import plotIV

matplotlib.rc('axes', labelsize=14)
matplotlib.rc('xtick', labelsize=12)
matplotlib.rc('ytick', labelsize=12)

def plot():
    #pathbase = r"C:\Users\summa\OneDrive\Works\2022-02-07_CMS_LGAD\I-V_test\measurement1"
    pathbase = r"C:\Users\kmlee\OneDrive\Works\2022-02-07_CMS_LGAD\I-V_test\measurement1"
    pathlist = [
        "2022-05-02_FBK_2022v1_2x2_13_T10", #9
        "2022-05-02_FBK_2022v1_2x2_14_T10", #18
        "2022-05-02_FBK_2022v1_2x2_15_T10", #8
        "2022-05-02_FBK_2022v1_2x2_16_T10", #17
        "2022-05-03_FBK_2022v1_2x2_33_T10", #9
        "2022-05-03_FBK_2022v1_2x2_34_T10", #17
        "2022-05-03_FBK_2022v1_2x2_35_T10", #7
        "2022-05-03_FBK_2022v1_2x2_36_T10", #18
        "2022-05-04_FBK_2022v1_2x2_53_T10", #7
        "2022-05-04_FBK_2022v1_2x2_54_T10", #18
        "2022-05-04_FBK_2022v1_2x2_55_T10", #9 
        "2022-05-04_FBK_2022v1_2x2_56_T10", #18
    ]
    fnames = [
        'I-V_2410_FBK_2022v1_2x2_13_T10_PAD1_2022-05-02T15.19.39_0_-400_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_14_T10_PAD1_2022-05-02T16.20.57_0_-400_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_15_T10_PAD1_2022-05-02T17.20.34_0_-400_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_16_T10_PAD1_2022-05-02T18.05.35_0_-300_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_33_T10_PAD1_2022-05-03T16.07.51_0_-100_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_34_T10_PAD1_2022-05-03T16.38.41_0_-400_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_35_T10_PAD1_2022-05-03T17.13.28_0_-400_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_36_T10_PAD1_2022-05-03T18.10.28_0_-400_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_53_T10_PAD1_2022-05-04T13.15.50_0_-400_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_54_T10_PAD1_2022-05-04T15.30.34_0_-400_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_55_T10_PAD1_2022-05-04T15.37.19_0_-400_totalCurrent_breakdown.txt',
        'I-V_2410_FBK_2022v1_2x2_56_T10_PAD1_2022-05-04T16.51.57_0_-400_totalCurrent_breakdown.txt'
    ]

    labels = [p[11:-4] for p in pathlist]
    waferN = [9, 18, 8, 17,  9, 17, 7, 18, 7, 18,  9, 18]
    idx =    [3,  8, 2,  6,  4,  7, 0,  9, 1, 10,  5, 11]
    idx =    [6,  8, 2,  0,  4, 10, 3,  5, 1,  7,  9, 11]

    flist = []
    for path, fname in zip (pathlist, fnames):
        fn = os.path.join(pathbase, path, "totalcurrent", fname)
        flist.append(fn)

    data = plotIV.readdata(flist)

    def color_by_dose():
        colors = []
        i = 2
        j = 2
        for w in waferN:
            if w > 10:
                colors.append(f'#ff{i:1x}f0f')
                i += 2
            else:
                colors.append(f'#0f{j:1x}fff')
                j += 2

        return colors


    def color_by_wafer():
        colors = []
        for w in waferN:
            if w == 7:
                colors.append(f'#ff0f0f')
            elif w == 8:
                colors.append(f'#ffaf0f')
            elif w == 9:
                colors.append(f'#ff0fff')
            elif w == 17:
                colors.append(f'#0f0fff')
            elif w == 18:
                colors.append(f'#0fafff')
            else:
                colors.append(f"#000000")

        return colors

    def color_by_sensor():
        fmts = [
            "#ff0f0f",
            "#ff7f0f",
            "#ffcf0f",
            "#ffff0f",
            "#0fff0f",
            "#0fff7f",
            "#0fffcf",
            "#0fffff",
            "#0f0fff",
            "#7f0fff",
            "#cf0fff",
            "#ff0fff",]
        #for i in range(len(fnames)):
        #    fmts.append(f"#{int(i/12*16):1x}00")
        #    print(f"#{int(i/12*16):1x}00")

        return fmts

    colors = color_by_wafer()
    #colors = color_by_sensor()
    
    for i, d in enumerate(data):
        l = len(d[1])
        ii = idx[i]
        di = data[ii]
        plt.semilogy(np.abs(di[0,:l//2]), np.abs(di[2,:l//2]), '+-', color=colors[ii], label=f"{labels[ii]} W{waferN[ii]}", linewidth=0.5, markersize=4)
        #plt.loglog(np.abs(d[1,:l//2]), np.abs(d[2,:l//2]), label=labels[i])
        
    plt.xlim(left=1)
    plt.ylim(top=1e-5)
    plt.legend()
    plt.xlabel('Bias (V)')
    plt.ylabel('Current (A)')

    plt.show()

if __name__=="__main__":
    plot()
