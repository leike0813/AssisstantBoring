# -*- coding:utf-8 -*-

import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg

__all__ = ['QDoubleSpinboxDelegate', 'QSpinboxDelegate']

class QDoubleSpinboxDelegate(qtw.QStyledItemDelegate):
    """
    用于PyQt5的浮点数输入框代理。
    """


    def __init__(self, parent=None):
        super(QDoubleSpinboxDelegate, self).__init__(parent)
        self.maximum = 65535
        self.minimum = -65535
        self.singleStep = 0.01        
        self.decimalPlace = 2

    def createEditor(self, parent, option, index):
        """
        PyQt5的代理必须重写的关键函数。
        创建编辑器。
        默认数据范围为(-65535.0 ~ 65535.0)。
        默认步长为0.01。
        """
        editor = qtw.QDoubleSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(self.minimum)
        editor.setMaximum(self.maximum)
        editor.setSingleStep(self.singleStep)
        editor.setDecimals(self.decimalPlace)
        return editor

    def setEditorData(self, editor, index):
        """
        PyQt5的代理必须重写的关键函数。
        从模型中读取数据传给编辑器。
        """
        editor.setValue(float(index.data(qtc.Qt.EditRole)))

    def setModelData(self, editor, model, index):
        """
        PyQt5的代理必须重写的关键函数。
        将编辑器的数值写入模型。
        """
        model.setData(index, editor.value())
        
    def setMaximum(self, value):
        self.maximum = value
        
    def setMinimum(self, value):
        self.minimum = value
        
    def setSingleStep(self, value):
        self.singleStep = value
        
    def setDecimalPlace(self, value):
        self.decimalPlace = value
        
class QSpinboxDelegate(qtw.QStyledItemDelegate):
    """
    用于PyQt5的整数输入框代理。
    """


    def __init__(self, parent=None):
        super(QSpinboxDelegate, self).__init__(parent)
        self.maximum = 65535
        self.minimum = -65535
        self.singleStep = 1

    def createEditor(self, parent, option, index):
        """
        PyQt5的代理必须重写的关键函数。
        创建编辑器。
        默认数据范围为(-65535 ~ 65535)。
        默认步长为1。
        """
        editor = qtw.QSpinBox(parent)
        editor.setFrame(False)
        editor.setMinimum(self.minimum)
        editor.setMaximum(self.maximum)
        editor.setSingleStep(self.singleStep)
        return editor

    def setEditorData(self, editor, index):
        """
        PyQt5的代理必须重写的关键函数。
        从模型中读取数据传给编辑器。
        """
        editor.setValue(int(index.data(qtc.Qt.EditRole)))

    def setModelData(self, editor, model, index):
        """
        PyQt5的代理必须重写的关键函数。
        将编辑器的数值写入模型。
        """
        model.setData(index, editor.value())
        
    def setMaximum(self, value):
        self.maximum = value
        
    def setMinimum(self, value):
        self.minimum = value
        
    def setSingleStep(self, value):
        self.singleStep = value