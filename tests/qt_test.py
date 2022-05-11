import sys
import PySide6
from PySide6.QtWidgets import QApplication, QWidget
from __feature__ import snake_case, true_property

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    window.show()
    app.exec()
