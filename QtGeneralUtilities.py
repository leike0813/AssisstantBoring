# -*- coding:utf-8 -*-

#本文件用于定义部分通用窗体及控件

import sys
import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
from PyQt5 import QtSvg
from qtconsole.rich_ipython_widget import RichIPythonWidget
from qtconsole.inprocess import QtInProcessKernelManager
from Ui_Console import Ui_ConsoleWidget

__all__ = ['MyCustomPushButton', 'QConsoleWidget', 'ArgumentError', 'SizeError', 'MatrixSizeError', 'str2int', 'str2float', 'str2bool']

class MyCustomPushButton(qtw.QPushButton):
    """
    自定义按钮控件。
    可指定其从属的主窗体及一个相关对象。
    """
    pressed_Mod = qtc.pyqtSignal(qtc.QObject, object)#按钮按下信号，将主窗体及相关对象作为参数发送。
    
    def __init__(self, mainWindow, _object, *args, **kwargs):
        """
        构造器。
        必要参数：
            1.mainWindow            按钮从属的主窗体，必须是PyQt5.QtWidgets.QWidget对象。
            2._object               与按钮相关的任意对象。
        可选参数：
            1.*args, **kwargs       原始的QPushButton的构造参数。
        """
        super(MyCustomPushButton, self).__init__(*args, **kwargs)
        self._mainwindow = mainWindow
        self._object = _object
        
        self.pressed.connect(self.onButtonPressed)
        
    def onButtonPressed(self):
        """
        按钮按下时调用的槽函数。
        发送pressed_Mod信号。
        """
        self.pressed_Mod.emit(self._mainwindow, self._object)
        
class QConsoleWidget(qtw.QWidget, Ui_ConsoleWidget):
    
    
    def __init__(self, mainWindow, qWidget, parent = None):
        super(QConsoleWidget, self).__init__(parent)
        self.setupUi(self)
        self.mainWindow = mainWindow
        self.qWidget = qWidget
        self.qwidgetLabel.setText(self.qWidget.__repr__())
        self.ipyConsoleWidget = QIPythonWidget(customBanner="控制台已开启。\n")
        self.consoleGroupBox.layout().addWidget(self.ipyConsoleWidget)
        self.push({"Mainwindow": self.mainWindow, "mw": self.mainWindow, "CurrentWidget": self.qWidget, "cw": self.qWidget, 'self': self})
        
        self.clearPushButton.pressed.connect(self.ipyConsoleWidget.clearTerminal)
        self.closePushButton.pressed.connect(self.close)
        
    def push(self, variableDict):
        self.ipyConsoleWidget.pushVariables(variableDict)
        
    def switchCurrentWidget(self, qWidget):
        self.qWidget = qWidget
        self.qwidgetLabel.setText(self.qWidget.__repr__())
        self.push({"CurrentWidget": self.qWidget, "cw": self.qWidget})

class QIPythonWidget(RichIPythonWidget):
    """ Convenience class for a live IPython console widget. We can replace the standard banner using the customBanner argument"""
    def __init__(self,customBanner=None,*args,**kwargs):
        super(QIPythonWidget, self).__init__(*args,**kwargs)
        if customBanner!=None: self.banner=customBanner
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            get_app_qt5().exit()            
        self.exit_requested.connect(stop)

    def pushVariables(self,variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)
    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()    
    def printText(self,text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)        
    def executeCommand(self,command):
        """ Execute a command in the frame of the console widget """
        self._execute(command,False)

def get_app_qt5(*args, **kwargs):
    """Create a new qt5 app or return an existing one."""
    app = qtw.QApplication.instance()
    if app is None:
        if not args:
            args = ([''],)
        app = qtw.QApplication(*args, **kwargs)
    return app
        
class EmittingStream(qtc.QObject):
    """
    输出流信号。
    """
    textWritten = qtc.pyqtSignal(str)
    
    def write(self, text):
        self.textWritten.emit(str(text))
        
class ArgumentError(Exception):
    def __init__(self, input):
        self.input = input

    def __str__(self):
        return '\nThe inputed argument ' + str(self.input) + ' is incorrect.'
    
class SizeError(Exception):
    """
    输入数组尺寸错误异常。
    """
    def __init__(self, input):
        self.input = input

    def __str__(self):
        return '\nThe size of inputed array (' + str(self.input) + ') does not match.'    
    
class MatrixSizeError(Exception):
    """
    输入矩阵尺寸错误异常。
    """
    def __init__(self, input):
        self.input = input

    def __str__(self):
        return '\nThe size of inputed matrix ' + str(self.input) + ' is incorrect.\nIt must be a square matrix.'
    
def str2int(str):
    """
    字符串转化为整型，附带校验。
    """
    try:
        ret = int(str)
        ok = True
    except ValueError:
        ret = str
        ok = False
    return ret, ok

def str2float(str):
    """
    字符串转化为浮点型，附带校验。
    """
    try:
        ret = float(str)
        ok = True
    except ValueError:
        ret = str
        ok = False
    return ret, ok

def str2bool(str):
    """
    字符串转化为布尔型，附带校验。
    传入字符串必须为'True'， 结果才是True；传入字符串必须为'False'， 结果才是False。这与bool()函数转化的结果不同，请注意。
    另外传入值若为整数1/0，也会返回True/False。
    其它传入值会原样返回。
    """
    if str == 'True' or str == 1:
        ret = True
        ok = True
    elif str == 'False' or str == 0:
        ret = False
        ok = True
    else:
        ret = str
        ok = False
    return ret, ok
    
