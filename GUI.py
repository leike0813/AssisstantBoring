#encoding: utf-8

import sys, os
import numpy as np
import pandas as pd
import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg

from UI_Design import Ui_MainWindow

class AssistantBoring_GUI(qtw.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(AssistantBoring_GUI, self).__init__(parent)
        self.setupUi(self)
        

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    win = AssistantBoring_GUI()
    win.show()
    sys.exit(app.exec_())