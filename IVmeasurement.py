import time
import datetime

from PySide6.QtWidgets import *
from PySide6.QtUiTools import QUiLoader


app = QApplication()

class IVmeasurement():
    loader = QUiLoader()
    window = loader.load("IVpannel.ui")
    window.setMinimumSize(520, 640)

    Vstart = 0
    Vstop = -100
    Vstep = 1
    delay = 0.01
    compl = 1e-4  # 100 uA

    reversesweep = True
    date = datetime.date.today().isoformat() 
    sensorname = "sensor"
    npad = 0
    outpath = f"C:\\Users\\summa\\OneDrive\\Works\\2022-02-07_CMS_LGAD\\I-V_test"
    outpath += f"\\{date}_{sensorname}"
    outfilename = f"I-V_2410_{sensorname}_PAD{npad}_{time.strftime('%Y-%m-%dT%H.%M.%S')}_{Vstart}_{Vstop}"  

    def __init__(self):
        self.initialize()
        self.window.show()

    def initialize(self):
        self.window.plainTextEdit.setReadOnly(True)
        self.init_lineEdits()
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
        self.window.lineEdit_outfilename.setText(str(self.outfilename))

    def connect_actions(self):
        self.window.lineEdit_Vstart.textChanged.connect(self.set_value_Vstart)
        self.window.lineEdit_Vstop.textChanged.connect(self.set_value_Vstop)
        self.window.lineEdit_Vstep.textChanged.connect(self.set_value_Vstep)
        self.window.lineEdit_delay.textChanged.connect(self.set_value_delay)
        self.window.lineEdit_compl.textChanged.connect(self.set_value_compl)

        self.window.lineEdit_outpath.textChanged.connect(self.set_outpath)
        self.window.lineEdit_date.textChanged.connect(self.set_date)
        self.window.lineEdit_outfilename.textChanged.connect(self.set_outfilename)
        self.window.lineEdit_sensorname.textChanged.connect(self.set_sensorname)
        self.window.lineEdit_npad.textChanged.connect(self.set_npad)

        self.window.toolButton_outpath.clicked.connect(self.set_outpath)
        self.window.pushButton_start.clicked.connect(self.start_measurement)
        self.window.pushButton_stop.clicked.connect(self.stop_measurement)
        self.window.pushButton_plot.clicked.connect(self.plot_result)
    
        self.window.checkBox_reversesweep.stateChanged.connect(self.set_checkBox)

    def print_values(self):
        self.window.plainTextEdit.insertPlainText(f"{self.Vstart}\n")
        self.window.plainTextEdit.insertPlainText(f"{self.Vstop}\n")
        self.window.plainTextEdit.insertPlainText(f"{self.Vstep}\n")
        self.window.plainTextEdit.insertPlainText(f"{self.delay}\n")
        self.window.plainTextEdit.insertPlainText(f"{self.compl}\n")

    def set_value_Vstart(self):
        self.Vstart = float(self.window.lineEdit_Vstart.text())
        
    def set_value_Vstop(self):
        self.Vstop = float(self.window.lineEdit_Vstop.text())

    def set_value_Vstep(self):
        self.Vstep = float(self.window.lineEdit_Vstep.text())

    def set_value_delay(self):
        self.delay= float(self.window.lineEdit_delay.text())

    def set_value_compl(self):
        self.compl= float(self.window.lineEdit_compl.text())

    def set_filename(self):
        self.sensorname = self.window.lineEdit_sensorname.text()

    def set_npad(self):
        self.npad = self.window.lineEdit_npad.text()

    def set_outpath(self):
        self.outpath = self.window.lineEdit_outpath.text()

    def set_date(self):
        self.date = self.window.lineEdit_date.text()

    def set_outfilename(self):
        self.outfilename = self.window.lineEdit_outfilename.text()

    def update_filename(self):
        self.outpath += f"\\{self.date}_{self.sensorname}"
        self.outfilename = f"I-V_2410_{self.sensorname}_PAD{self.npad}_{time.strftime('%Y-%m-%dT%H.%M.%S')}_{self.Vstart}_{self.Vstop}"  
        #self.print_values()

    def set_outpath(self):
        self.outpath = QFileDialog.getExistingDirectory()
        self.window.lineEdit_outpath.setText(self.outpath)

    def set_checkBox(self):
        self.reversesweep = self.window.checkBox_reversesweep.isChecked()
        print (self.reversesweep)

    def start_measurement(self):
        pass

    def stop_measurement(self):
        pass

    def plot_result(self):
        pass


def main():
    iv = IVmeasurement()
    app.exec()


if __name__ == "__main__":
    main()