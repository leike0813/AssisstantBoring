#encoding: utf-8

import sys, os, random
import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import numpy as np
import pandas as pd

from QtGeneralUtilities import *
from QtDataModels import *
from QtDelegates import *

__all__ = ['QDataSheetWidget', 'QMatplotlibWidget']

class QDataSheetWidget(qtw.QWidget):
    """
    监测数据编辑窗体。
    是对采用QDataFrameModel作为数据模型的QTableView的完善。
    没有对应的界面文件。一般用于其他窗体中的一个子窗体。
    """
    dataFrameChanged = qtc.pyqtSignal()
    
    def __init__(self, parent = None):
        """
        构造器。
        可选参数：
            1. parent            父对象。
        """
        super(QDataSheetWidget, self).__init__(parent)
        self._iconSize = qtc.QSize(36, 24)
        self._newcolumncount = 1
        self._workFolder = None
        self.setupUi()
        
    def setupUi(self):
        """
        初始化窗体界面，创建必要的按钮。
        """
        self.gridLayout = qtw.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)

        self.buttonFrame = qtw.QFrame(self)#按钮区域
        self.buttonFrame.setFrameShape(qtw.QFrame.NoFrame)
        spacerItemButton = qtw.QSpacerItem(40, 20, qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Minimum)

        self.buttonFrameLayout = qtw.QGridLayout(self.buttonFrame)
        self.buttonFrameLayout.setContentsMargins(0, 0, 0, 0)
        
        self.loadDataButton = qtw.QToolButton(self.buttonFrame)#读取数据按钮
        self.loadDataButton.setObjectName('loadDataButton')
        self.loadDataButton.setText(self.tr('load'))
        self.loadDataButton.setToolTip(self.tr('load data'))
        
        self.clearDataButton = qtw.QToolButton(self.buttonFrame)#清空数据按钮
        self.clearDataButton.setObjectName('clearDataButton')
        self.clearDataButton.setText(self.tr('clear'))
        self.clearDataButton.setToolTip(self.tr('clear data'))        
        
        self.editDataButton = qtw.QToolButton(self.buttonFrame)#编辑数据按钮
        self.editDataButton.setObjectName('editDataButton')
        self.editDataButton.setText(self.tr('edit'))
        self.editDataButton.setToolTip(self.tr('edit data'))        

        self.addColumnButton = qtw.QToolButton(self.buttonFrame)#新增列按钮
        self.addColumnButton.setObjectName('addColumnButton')
        self.addColumnButton.setText(self.tr('+col'))
        self.addColumnButton.setToolTip(self.tr('add new column'))

        self.addRowButton = qtw.QToolButton(self.buttonFrame)#新增行按钮
        self.addRowButton.setObjectName('addRowButton')
        self.addRowButton.setText(self.tr('+row'))
        self.addRowButton.setToolTip(self.tr('add new row'))

        self.removeColumnButton = qtw.QToolButton(self.buttonFrame)#删除列按钮
        self.removeColumnButton.setObjectName('removeColumnButton')
        self.removeColumnButton.setText(self.tr('-col'))
        self.removeColumnButton.setToolTip(self.tr('remove a column'))

        self.removeRowButton = qtw.QToolButton(self.buttonFrame)#删除行按钮
        self.removeRowButton.setObjectName('removeRowButton')
        self.removeRowButton.setText(self.tr('-row'))
        self.removeRowButton.setToolTip(self.tr('remove selected rows'))

        self.buttons = [self.loadDataButton, self.clearDataButton, self.editDataButton, self.addColumnButton, self.addRowButton, self.removeColumnButton, self.removeRowButton]

        for index, button in enumerate(self.buttons):
            button.setMinimumSize(self._iconSize)
            button.setMaximumSize(self._iconSize)
            button.setIconSize(self._iconSize)
            button.setCheckable(True)
            self.buttonFrameLayout.addWidget(button, 0, index, 1, 1)
        self.buttonFrameLayout.addItem(spacerItemButton, 0, index+1, 1, 1)

        self.tableView = qtw.QTableView(self)#tableView窗体
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSortingEnabled(False)
        self.tableView.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.Stretch)
        self.tableView.horizontalHeader().setMinimumSectionSize(50)
        self.tableView.verticalHeader().setSectionResizeMode(qtw.QHeaderView.Fixed)
        self.tableView.verticalHeader().setDefaultSectionSize(20)
        self.tableView.verticalHeader().setSectionsMovable(False)
        
        self.gridLayout.addWidget(self.buttonFrame, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.tableView, 1, 0, 1, 1)        
        
        qtc.QMetaObject.connectSlotsByName(self)
        
    def onDataChanged(self):
        if not self.editDataButton.isChecked():
            self.dataFrameChanged.emit()
            
    def onModelChanged(self):
        self.addColumnButton.setEnabled(self.tableView.model()._editable)
        self.addRowButton.setEnabled(self.tableView.model()._editable)
        self.removeColumnButton.setEnabled(self.tableView.model()._editable)
        self.removeRowButton.setEnabled(self.tableView.model()._editable)        
        
    def setModel(self, model):
        """
        为tableView控件设定数据模型。
        等价于table.setModel()
        """
        if isinstance(model, QDataFrameModel):
            self.tableView.setModel(model)
            self.tableView.model().dataChanged.connect(self.onDataChanged)
            self.onModelChanged()
        else:
            raise TypeError("The input argument must be a QDataFrameModel object.")
        
    @qtc.pyqtSlot(bool)
    def on_loadDataButton_toggled(self, triggered):
        """
        为tableView控件的数据模型读取数据。
        """
        if triggered:
            model = self.tableView.model()
            if model is not None:
                filename, filetype = qtw.QFileDialog.getOpenFileName(self, '打开数据文件', os.getcwd() if self._workFolder == None else self._workFolder, "Microsoft Excel Spreedsheets (*.xls, *.xlsx);;Comma Separated Values (*.csv)")
                if filetype == 'Comma Separated Values (*.csv)':
                    self.tableView.model().readDataFrameFromFile(filename, 'CSV')
                elif filetype == 'Microsoft Excel Spreedsheets (*.xls, *.xlsx)':
                    self.tableView.model().readDataFrameFromFile(filename, 'XLS')
                delegate = QDoubleSpinboxDelegate(self.tableView)
                delegate.singleStep = 0.1#输入代理框的调整步长，可根据实际需要调整
                self.tableView.setItemDelegate(delegate)
                self.tableView.model().confirmEdit()#改动直接反映至DataFrameModel中的原始DataFrame中，此句可根据实际需要调整
                self.dataFrameChanged.emit()
            self.sender().setChecked(False)
            
    @qtc.pyqtSlot(bool)
    def on_clearDataButton_toggled(self, triggered):
        if triggered:
            model = self.tableView.model()
            if model is not None:
                self.tableView.model().layoutAboutToBeChanged.emit()
                QDataFrameModel.clearDataFrameAndReshape(self.tableView.model().dataFrame, (0, 0))
                self.tableView.model().layoutChanged.emit()
                #self.tableView.model().confirmEdit()#改动直接反映至DataFrameModel中的原始DataFrame中，此句可根据实际需要调整
                self.dataFrameChanged.emit()
            self.sender().setChecked(False)
            
    @qtc.pyqtSlot(bool)
    def on_editDataButton_toggled(self, triggered):
        model = self.tableView.model()
        if model is not None:
            if triggered:
                self.tableView.model()._editable = True
            else:
                self.tableView.model()._editable = False
                self.tableView.model().confirmEdit()#改动直接反映至DataFrameModel中的原始DataFrame中，此句可根据实际需要调整
                self.dataFrameChanged.emit()
            self.onModelChanged()
        else:
            if triggered:
                self.sender().setChecked(False)
        
    @qtc.pyqtSlot()
    def uncheckButton(self):
        """
        Removes the checked stated of all buttons in this widget.
        This method is also a slot.
        """
        for button in self.buttons:
            if button.isChecked():
                button.setChecked(False)
                
    @qtc.pyqtSlot(bool)
    def on_addColumnButton_toggled(self, triggered):
        """
        Adds a column with the given parameters to the underlying model
        This method is also a slot.
        If no model is set, nothing happens.

        Args:
            triggered (bool): If the corresponding button was
                activated, the row will be appended to the end.
        """
        if triggered:
            model = self.tableView.model()
            if model is not None:
                status = model.addDataFrameColumn('New Column' + str(self._newcolumncount), float, 0.0)
                if status:
                    self.tableView.setItemDelegateForColumn(model.columnCount() - 1, QMonitorDataDelegate(self.tableView))
                    self._newcolumncount += 1
                    self.onDataChanged()
            self.sender().setChecked(False)    
           
        
    @qtc.pyqtSlot(bool)
    def on_addRowButton_toggled(self, triggered):
        """
        Adds a row to the model.
        This method is also a slot.
        If no model is set, nothing happens.

        Args:
            triggered (bool): If the corresponding button was
                activated, the row will be appended to the end.
        """
        if triggered:
            model = self.tableView.model()
            if model is not None:
                status = model.addDataFrameRows()
                if status:
                    self.onDataChanged()
            self.sender().setChecked(False)    
            
    @qtc.pyqtSlot(bool)
    def on_removeRowButton_toggled(self, triggered):
        """
        Removes one or multiple rows from the model.
        This method is also a slot.

        Args:
            triggered (bool): If the corresponding button was
                activated, the selected rows will be removed
                from the model.
        """
        if triggered:
            model = self.tableView.model()
            if model is not None:
                selection = self.tableView.selectedIndexes()
    
                rows = [index.row() for index in selection]
                status = model.removeDataFrameRows(set(rows))
                if status:
                    self.onDataChanged()
            self.sender().setChecked(False)    
            
    @qtc.pyqtSlot(bool)
    def on_removeColumnButton_toggled(self, triggered):
        """
        Removes one or multiple columns from the model.
        This method is also a slot.

        Args:
            triggered (bool): If the corresponding button was
                activated, the selected columns will be removed
                from the model.
        """
        if triggered:
            model = self.tableView.model()
            if model is not None:
                selection = self.tableView.selectedIndexes()            
        
                columnNames = [(index.column(), model.headerData(index.column(), qtc.Qt.Horizontal)) for index in selection]
                status = model.removeDataFrameColumns(set(columnNames))
                if status:
                    self.onDataChanged()
            self.sender().setChecked(False)
            
class MyMplCanvas(FigureCanvas):
    """
    用于PyQt5的Matplotlib画布。
    FigureCanvas的最终的父类其实是QWidget。
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        # 配置中文显示
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        #plt.ion()  # 打开交互式绘图

        self.fig = Figure(figsize=(width, height), dpi=dpi)  # 新建一个figure
        #self.axes = self.fig.add_subplot(111)  # 建立一个子图，如果要建立复合图，可以在这里修改

        #self.axes.hold(False)  # 每次绘图的时候不保留上一次绘图的结果

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        '''定义FigureCanvas的尺寸策略，这部分的意思是设置FigureCanvas，使之尽可能的向外填充空间。'''
        FigureCanvas.setSizePolicy(self,
                                   qtw.QSizePolicy.Expanding,
                                   qtw.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class QMatplotlibWidget(qtw.QWidget):
    """
    用于PyQt5的Matplotlib窗体。
    """
    def __init__(self, parent=None, ntb_on = False):
        super(QMatplotlibWidget, self).__init__(parent)
        self.initUi(ntb_on)

    def initUi(self, ntb_on):
        self.layout = qtw.QVBoxLayout(self)
        self.matplotlibCanvas = MyMplCanvas(self, width=5, height=4, dpi=100)
        self.axesList = []
        self.fig = self.matplotlibCanvas.fig
        self.add_subplot = self.matplotlibCanvas.fig.add_subplot
        self.draw = self.matplotlibCanvas.draw
        self.navigationToolbar = NavigationToolbar(self.matplotlibCanvas, self)  # 添加完整的 toolbar
        self.layout.addWidget(self.matplotlibCanvas)
        if ntb_on:
            self.layout.addWidget(self.navigationToolbar)
            
    def clear(self):
        self.matplotlibCanvas.fig.clf()
        self.axesList.clear()
        
    def plotLine(self, axesindex, *args, **kwargs):
        obj = self.axesList[axesindex].plot(*args, **kwargs)
        return obj
        
    def plotBar(self, axesindex, *args, **kwargs):
        obj = self.axesList[axesindex].bar(*args, **kwargs)
        return obj
        
    def plotScatter(self, axesindex, *args, **kwargs):
        obj = self.axesList[axesindex].scatter(*args, **kwargs)    
        return obj
        
    def plotStack(self, axesindex, *args, **kwargs):
        obj = self.axesList[axesindex].stackplot(*args, **kwargs)
        return obj
        
    def plotBarH(self, axesindex, *args, **kwargs):
        obj = self.axesList[axesindex].barh(*args, **kwargs)
        return obj
        
    def plotFillBetweenX(self, axesindex, *args, **kwargs):
        obj = self.axesList[axesindex].fill_betweenx(*args, **kwargs)
        return obj
        
    def plotSpan(self, axesindex, orientation, *args, **kwargs):
        if orientation == 'horizontal' or orientation == 'h':
            obj = self.axesList[axesindex].axhspan(*args, **kwargs)
        elif orientation == 'vertical' or orientation == 'v':
            obj = self.axesList[axesindex].axvspan(*args, **kwargs)
        else:
            raise ArgumentError(orientation)
        return obj
        
    def plotSurface(self, axesindex, *args, **kwargs):
        obj = self.axesList[axesindex].plot_surface(*args, **kwargs)
        return obj
