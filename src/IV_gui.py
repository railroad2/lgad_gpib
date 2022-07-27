import time
import datetime

from PySide6.QtCore import Qt 
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader

import plotIV

app = QApplication()

class IV_gui():
    loader = QUiLoader()
    window = loader.load("IVpannel.ui")
    window.setMinimumSize(520, 640)

    Vstart = 0
    Vstop = -10
    Vstep = 1
    delay = 0.01
    compl = 1e-4  # 100 uA

    returnsweep = True
    isBreakdown = False
    isTotalcurrent = False
    date = datetime.date.today().isoformat() 
    sensorname = "sensor"
    npad = 0
    ofhead = "I-V_2410"
    outpath = f"C:\\Users\\summa\\OneDrive\\Works\\2022-02-07_CMS_LGAD\\I-V_test"
    ofname = f"{date}_{sensorname}"
    ofname += f"\\{ofhead}_{sensorname}_PAD{npad}_{time.strftime('%Y-%m-%dT%H.%M.%S')}_{Vstart}_{Vstop}"  

    def __init__(self):
        self.initialize()
        self.window.show()

    def initialize(self):
        self.window.plainTextEdit.setReadOnly(True)
        self.init_lineEdits()
        self.init_checkBoxes()
        self.connect_actions()

    def init_lineEdits(self):
        self.window.lineEdit_Vstart.setText(str(self.Vstart))
        self.window.lineEdit_Vstop.setText(str(self.Vstop))
        self.window.lineEdit_Vstep.setText(str(self.Vstep))
        self.window.lineEdit_delay.setText(str(self.delay))
        self.window.lineEdit_compl.setText(str(self.compl))

        self.window.lineEdit_sensorname.setText(str(self.sensorname))
        self.window.lineEdit_npad.setText(str(self.npad))
        self.window.lineEdit_date.setText(str(self.date))
        self.window.lineEdit_outpath.setText(str(self.outpath))
        self.window.lineEdit_ofname.setText(str(self.ofname))

    def init_checkBoxes(self):
        self.window.checkBox_returnsweep.setCheckState(Qt.Checked if self.returnsweep else Qt.Unchecked)
        self.window.checkBox_totalcurrent.setCheckState(Qt.Checked if self.isTotalcurrent else Qt.Unchecked)
        self.window.checkBox_breakdown.setCheckState(Qt.Checked if self.isBreakdown else Qt.Unchecked)

    def connect_actions(self):
        self.window.lineEdit_Vstart.textChanged.connect(self.set_Vstart)
        self.window.lineEdit_Vstop.textChanged.connect(self.set_Vstop)
        self.window.lineEdit_Vstep.textChanged.connect(self.set_Vstep)
        self.window.lineEdit_delay.textChanged.connect(self.set_delay)
        self.window.lineEdit_compl.textChanged.connect(self.set_compl)

        self.window.lineEdit_outpath.textChanged.connect(self.update_outpath)
        self.window.lineEdit_date.textChanged.connect(self.set_date)
        self.window.lineEdit_ofname.textChanged.connect(self.set_ofname)
        self.window.lineEdit_sensorname.textChanged.connect(self.set_sensorname)
        self.window.lineEdit_npad.textChanged.connect(self.set_npad)

        self.window.toolButton_outpath.clicked.connect(self.select_outpath)
        self.window.pushButton_start.clicked.connect(self.start_measurement)
        self.window.pushButton_stop.clicked.connect(self.stop_measurement)
        self.window.pushButton_plot.clicked.connect(self.plot_result)
    
        self.window.checkBox_returnsweep.stateChanged.connect(self.set_returnsweep)
        self.window.checkBox_totalcurrent.stateChanged.connect(self.set_isTotalcurrent)
        self.window.checkBox_breakdown.stateChanged.connect(self.set_isBreakdown)

    def print_values(self):
        self.window.plainTextEdit.insertPlainText(f"{self.Vstart}\n")
        self.window.plainTextEdit.insertPlainText(f"{self.Vstop}\n")
        self.window.plainTextEdit.insertPlainText(f"{self.Vstep}\n")
        self.window.plainTextEdit.insertPlainText(f"{self.delay}\n")
        self.window.plainTextEdit.insertPlainText(f"{self.compl}\n")

    ## text change events
    def set_Vstart(self):
        self.Vstart = float(self.window.lineEdit_Vstart.text())
        self.update_filename()
        
    def set_Vstop(self):
        self.Vstop = float(self.window.lineEdit_Vstop.text())
        self.update_filename()

    def set_Vstep(self):
        self.Vstep = float(self.window.lineEdit_Vstep.text())

    def set_delay(self):
        self.delay= float(self.window.lineEdit_delay.text())

    def set_compl(self):
        self.compl= float(self.window.lineEdit_compl.text())

    def set_sensorname(self):
        self.sensorname = self.window.lineEdit_sensorname.text()
        self.update_filename()

    def set_npad(self):
        self.npad = self.window.lineEdit_npad.text()
        self.update_filename()

    def update_outpath(self):
        self.outpath = self.window.lineEdit_outpath.text()

    def set_date(self):
        self.date = self.window.lineEdit_date.text()
        self.update_filename()

    def set_ofname(self):
        self.ofname = self.window.lineEdit_ofname.text()

    def update_filename(self):
        self.ofname = f"{self.date}"
        self.ofname += f"_{self.sensorname}\\"
        self.ofname += f"{self.ofhead}"
        self.ofname += f"_{self.sensorname}"
        self.ofname += f"_PAD{self.npad}"
        self.ofname += f"_{time.strftime('%Y-%m-%dT%H.%M.%S')}"
        self.ofname += f"_{self.Vstart}"
        self.ofname += f"_{self.Vstop}"  
        #self.print_values()
        self.window.lineEdit_ofname.setText(str(self.ofname))
        if self.isTotalcurrent:
            self.ofname += "_TotalCurrent"
        if self.isBreakdown:
            self.ofname += "_Breakdown"
        
        self.window.lineEdit_ofname.setText(self.ofname)

    def select_outpath(self):
        self.outpath = QFileDialog.getExistingDirectory()
        self.outpath += f"\\{self.date}_{self.sensorname}"
        self.window.lineEdit_outpath.setText(self.outpath)

    def set_returnsweep(self):
        self.returnsweep = self.window.checkBox_returnsweep.isChecked()

    def set_isTotalcurrent(self):
        self.isTotalcurrent = self.window.checkBox_returnsweep.isChecked()

    def set_isBreakdown(self):
        self.isBreakdown = self.window.checkBox_returnsweep.isChecked()

    def start_measurement(self):
        pass

    def stop_measurement(self):
        pass

    def plot_result(self):
        files, _ = QFileDialog.getOpenFileNames(dir=self.outpath, filter="*.txt")
        print (files)
        data = plotIV.readdata(files)
        fns = []
        for file in files:
            fns.append(file.split('/')[-1])
            labels = plotIV.label_from_fname(fns)

        plotIV.plot(data, labels=labels, Vreal=True, fmt='*-', logy=False)
        Vbd = plotIV.detect_breakdown(data, labels=labels)
        self.window.plainTextEdit.insertPlainText(str(Vbd)+'\n')
        self.window.plainTextEdit.moveCursor(QTextCursor.End)

def main():
    iv = IV_gui()
    app.exec()


if __name__ == "__main__":
    main()