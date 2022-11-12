# -*- coding:utf-8 -*-

import PyQt5.QtCore as qtc
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as qtg
import numpy as np
import pandas as pd

from QtGeneralUtilities import *

class QNumpyArray2Model(qtc.QAbstractTableModel):
    """
    用于PyQt5的Numpy二维array数据模型。
    """
    editConfirmed = qtc.pyqtSignal()#确认编辑的信号。
    editRefuted = qtc.pyqtSignal()#撤销编辑的信号。
    
    def __init__(self, npArray = None, parent=None):
        """
        构造器。
        可选参数：
            1. npArray            二维Numpy数组。不要采用Matrix数据类型。
            2. parent             父对象。一般留空即可。
        """
        super(QNumpyArray2Model, self).__init__(parent)
        if type(npArray) is type(None):#若指定了nparray参数，则将nparray赋予nparray_orig参数；否则将一个空数组赋予nparray_orig参数
            self.setNumpyArray(np.empty((0,0)))
        else:
            self.setNumpyArray(npArray)
        self._hasHeader_H = False#默认不含header信息
        self._hasHeader_V = False#默认不含header信息
        self._VHeader_Num = False#默认不将行号作为默认垂直header
        self._editable = True
        self._displayDecimal = None
        
        self.editConfirmed.connect(self.cacheArray)
        self.editRefuted.connect(self.cacheArray)
            
    def cacheArray(self):
        """
        生成nparray_orig的一个缓存副本nparray，用于界面编辑。
        nparray_orig为实际外部传入的数组对象。对nparray_orig的改变会直接反应在外部，而副本nparray则不会。
        """
        if self.npArray_Orig.shape[0] > 0 and self.npArray_Orig.shape[1] > 0:
            for i in range(self.npArray_Orig.shape[0]):
                for j in range(self.npArray_Orig.shape[1]):
                    self.npArray[i, j] = self.npArray_Orig[i, j]        
            self.dataChanged.emit(self.index(0, 0), self.index(self.npArray_Orig.shape[0] - 1, self.npArray_Orig.shape[1] -1))
        
    def setNumpyArray(self, npArray):
        """
        设置数据模型对应的二维Numpy数组。
        """
        if not isinstance(npArray, np.core.ndarray):
            raise TypeError("The input argument must be a numpy.ndarray object.")
        
        self.layoutAboutToBeChanged.emit()
        self.npArray_Orig = npArray
        self.npArray = np.empty((npArray.shape[0], npArray.shape[1]), dtype = npArray.dtype)
        self.cacheArray()
        self.layoutChanged.emit()
        
    @property
    def dtype(self):
        return self.npArray_Orig.dtype
        
    @property
    def rank(self):
        return min(self.npArray_Orig.shape)
        
    def confirmEdit(self):
        """
        确认编辑时调用的槽函数。
        将缓存数组nparray中的数据写入nparray_orig，确认编辑。
        """
        if self.npArray_Orig.shape[0] > 0 and self.npArray_Orig.shape[1] > 0:
            for i in range(self.npArray_Orig.shape[0]):
                for j in range(self.npArray_Orig.shape[1]):
                    self.npArray_Orig[i, j] = self.npArray[i, j]
            self.editConfirmed.emit()
        
    def refuteEdit(self):
        """
        撤销编辑时调用的槽函数。
        """
        self.editRefuted.emit()
    
    def index(self, row, column, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型索引对象(Index)。
        """
        return self.createIndex(row, column, self.npArray[row, column])
        
    def rowCount(self, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型的行数。
        """
        return self.npArray.shape[0]
    
    def columnCount(self, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型的列数。
        """
        return self.npArray.shape[1]
    
    def data(self, index, role=qtc.Qt.DisplayRole):
        """
        PyQt5数据模型必须重写的关键函数。
        返回在指定的Role下的模型数据。
        其中DisplayRole为视图(View)中显示的数据；EditRole为传给编辑器的数据；TextAlignmentRole为数据显示时的对齐方式。
        """
        if not index.isValid() or \
           not 0 <= index.row() < self.npArray.shape[0] or \
           not 0 <= index.column() < self.npArray.shape[1]:
            return qtc.QVariant()
        
        if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
            if self._displayDecimal == None:
                return str(self.npArray[index.row(), index.column()])
            else:
                return str(round(self.npArray[index.row(), index.column()], self._displayDecimal))
        elif role == qtc.Qt.TextAlignmentRole:
            return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter
        else:
            return qtc.QVariant()
        
    def flags(self, index):
        """
        PyQt5数据模型必须重写的关键函数。
        返回指定索引对应的flag。
        为使模型数据可在视图中编辑，需要额外返回ItemIsEditable这一flag。
        """
        flag = super(QNumpyArray2Model, self).flags(index)
        return flag | qtc.Qt.ItemIsEditable if self._editable else flag
    
    def setData(self, index, value, role=qtc.Qt.EditRole):
        """
        PyQt5可编辑数据模型必须重写的关键函数。
        将编辑器传入的值写入缓存数组nparray。
        """
        if self.dtype() == int:#由于编辑器传入值均为str类型，需进行相应的数据类型转换及校验。
            value_dtype, ok = str2int(value)
        elif self.dtype() == float:
            value_dtype, ok = str2float(value)
        elif self.dtype() == str:
            value_dtype, ok = value, True
        elif self.dtype() == object:
            value_dtype, ok = value, True
        if ok:
            self.npArray[index.row(), index.column()] = value_dtype
            self.dataChanged.emit(index, index)
            return True
        return False
    
    def headerData(self, section, orientation, role = qtc.Qt.DisplayRole):
        """
        PyQt5数据模型必须重写的关键函数。
        返回表头信息。
        格式类似data()函数。
        """
        hdata = super(QNumpyArray2Model, self).headerData(section, orientation, role)
        if orientation == qtc.Qt.Horizontal and self._hasHeader_H:
            if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
                return str(self.headerArray_H[section])
            elif role == qtc.Qt.TextAlignmentRole:
                return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter
            else:
                return hdata
        elif orientation == qtc.Qt.Vertical and self._hasHeader_V:
            if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
                return str(self.headerArray_V[section])
            elif role == qtc.Qt.TextAlignmentRole:
                return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter
            else:
                return hdata
        elif orientation == qtc.Qt.Vertical and self._VHeader_Num:
            if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
                return str(section)
            elif role == qtc.Qt.TextAlignmentRole:
                return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter
            else:
                return hdata        
        return qtc.QVariant()
    
    def setHeader_Batch(self, headerArray, orientation):
        """
        批量设置表头信息。
        参数：
            1. headerArray            一维Numpy数组，长度与比较矩阵阶数一致。
            2. orientation            方向，1代表水平，2代表垂直。
        """
        if type(headerArray) is np.ndarray:
            if orientation == 1:
                if headerArray.shape[0] == self.npArray.shape[1]:
                    self.headerArray_H = headerArray
                    self._hasHeader_H = True
                    self.headerDataChanged.emit(qtc.Qt.Horizontal, 0, self.npArray.shape[1] - 1)
                else:
                    raise SizeError(headerArray.shape[0])                    
            elif orientation == 2:
                if headerArray.shape[0] == self.npArray.shape[0]:
                    self.headerArray_V = headerArray
                    self._hasHeader_V = True
                    self.headerDataChanged.emit(qtc.Qt.Vertical, 0, self.npArray.shape[0] - 1)
                else:
                    raise SizeError(headerArray.shape[0])                    
            else:
                raise ArgumentError(orientation)
        else:
            raise TypeError('The input argument must be a numpy.ndarray object.')
    
class QNumpyMatrixModel(QNumpyArray2Model):
    
    
    def __init__(self, npArray=None, parent=None):
        super(QNumpyMatrixModel, self).__init__(npArray, parent)
        self.headerArray=np.empty(self.rank(), dtype = str)
    
    def setNumpyArray(self, npArray):
        """
        设置数据模型对应的二维Numpy数组。
        附带方阵校验。
        """
        if npArray.shape[0] != npArray.shape[1]:
            raise MatrixSizeError(npArray.shape)        
        else:
            super(QNumpyMatrixModel, self).setNumpyArray(npArray)
        
    @property
    def rank(self):
        return self.npArray_Orig.shape[0]
    
    def headerData(self, section, orientation, role = qtc.Qt.DisplayRole):
        """
        PyQt5数据模型必须重写的关键函数。
        返回表头信息。
        格式类似data()函数。
        """
        hdata = super(QNumpyMatrixModel, self).headerData(section, orientation, role)
        if self._hasHeader:
            if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
                if orientation == qtc.Qt.Horizontal:
                    return str(self.headerArray[section])
                elif orientation == qtc.Qt.Vertical:
                    return str(self.headerArray[section])
            elif role == qtc.Qt.TextAlignmentRole:
                return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter
            else:
                return hdata
        return qtc.QVariant()
    
    def setHeader_Batch(self, headerArray):
        """
        批量设置表头信息。
        参数：
            1. headerArray            一维Numpy数组，长度与比较矩阵阶数一致。
        """
        if type(headerArray) is np.ndarray:
            if headerArray.shape[0] == self.rank():
                self.headerArray = headerArray
                self._hasHeader = True
                self.headerDataChanged.emit(qtc.Qt.Horizontal, 0, self.rank() - 1)
                self.headerDataChanged.emit(qtc.Qt.Vertical, 0, self.rank() - 1)
            else:
                raise SizeError(headerArray.shape[0])
        else:
            raise TypeError('The input argument must be a numpy.ndarray object.')
        
class QNumpyArray1Model(qtc.QAbstractTableModel):
    """
    用于PyQt5的Numpy一维array数组模型(竖向)。
    """
    editConfirmed = qtc.pyqtSignal()#确认编辑的信号。
    editRefuted = qtc.pyqtSignal()#撤销编辑的信号。

    def __init__(self, npArray = None, parent=None):
        """
        构造器。
        可选参数：
            1. npArray            一维Numpy数组。
            2. parent             父对象。一般留空即可。
        """
        super(QNumpyArray1Model, self).__init__(parent)
        if type(npArray) is type(None):#若指定了nparray参数，则将nparray赋予nparray_orig参数；否则将一个空数组赋予nparray_orig参数
            self.setNumpyArray(np.empty(0))
        else:
            self.setNumpyArray(npArray)            
        self._hasHeader = False#默认不含header信息
        self._editable = True
        self._displayDecimal = None

        self.editConfirmed.connect(self.cacheArray)
        self.editRefuted.connect(self.cacheArray)
        
    def cacheArray(self):
        """
        生成nparray_orig的一个缓存副本nparray，用于界面编辑。
        nparray_orig为实际外部传入的数组对象。对nparray_orig的改变会直接反应在外部，而副本nparray则不会。
        """
        if self.npArray_Orig.shape[0] > 0:
            for i in range(self.npArray_Orig.shape[0]):
                self.npArray[i] = self.npArray_Orig[i]        
            self.dataChanged.emit(self.index(0, 0), self.index(self.npArray_Orig.shape[0] - 1, 0))
        
    def setNumpyArray(self, npArray):
        """
        设置数据模型对应的一维Numpy数组。
        """
        if not isinstance(npArray, np.core.ndarray):
            raise TypeError("The input argument must be a numpy.ndarray object.")
        
        self.layoutAboutToBeChanged.emit()
        self.npArray_Orig = npArray
        self.npArray = np.empty(npArray.shape[0], dtype = npArray.dtype)
        self.cacheArray()        
        self.layoutChanged.emit()
        
    def setData_Batch(self, dataArray):
        if type(dataArray) is np.ndarray:
            if dataArray.shape[0] == self.rank():
                self.npArray[:] = dataArray
                self.dataChanged.emit(self.index(0, 0), self.index(self.rank() - 1, 0))
            else:
                raise SizeError(dataArray.shape[0])
        else:
            raise TypeError('The input argument must be a numpy.ndarray object.')        
        
    def setHeader_Batch(self, headerArray):
        """
        批量设置表头信息。
        参数：
            1. headerArray            一维Numpy数组，长度与隶属度向量一致。
        """
        if type(headerArray) is np.ndarray:
            if headerArray.shape[0] == self.rank():
                self.headerArray = headerArray
                self._hasHeader = True
                self.headerDataChanged.emit(qtc.Qt.Vertical, 0, self.rank() - 1)
            else:
                raise SizeError(headerArray.shape[0])
        else:
            raise TypeError('The input argument must be a numpy.ndarray object.')
        
    def setEditable(self, editable):
        self._editable = editable    
        
    def dtype(self):
        return self.npArray_Orig.dtype
        
    def rank(self):
        return self.npArray_Orig.shape[0]

    def confirmEdit(self):
        """
        确认编辑时调用的槽函数。
        将缓存数组nparray中的数据写入nparray_orig，确认编辑。
        """
        if self.npArray_Orig.shape[0] > 0:
            for i in range(self.npArray_Orig.shape[0]):
                self.npArray_Orig[i] = self.npArray[i]
            self.editConfirmed.emit()    
        
    def refuteEdit(self):
        """
        撤销编辑时调用的槽函数。
        """
        self.editRefuted.emit()
        
    def rowCount(self, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型的行数。
        """
        return self.npArray.shape[0]    
        
    def columnCount(self, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型的列数。
        """
        return 1    
    
    def index(self, row, column, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型索引对象(Index)。
        """
        return self.createIndex(row, column, self.npArray[row])

    def data(self, index, role=qtc.Qt.DisplayRole):
        """
        PyQt5数据模型必须重写的关键函数。
        返回在指定的Role下的模型数据。
        其中DisplayRole为视图(View)中显示的数据；EditRole为传给编辑器的数据；TextAlignmentRole为数据显示时的对齐方式。
        """
        if not index.isValid() or \
               not 0 <= index.row() <= self.npArray.shape[0]:
            return qtc.QVariant()
        
        if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
            if self._displayDecimal == None:
                return str(self.npArray[index.row()])
            else:
                return str(round(self.npArray[index.row()], self._displayDecimal))
        elif role == qtc.Qt.TextAlignmentRole:
            return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter            
        else:
            return qtc.QVariant()

    def flags(self, index):
        """
        PyQt5数据模型必须重写的关键函数。
        返回指定索引对应的flag。
        为使模型数据可在视图中编辑，需要额外返回ItemIsEditable这一flag。
        """
        flag = super(QNumpyArray1Model, self).flags(index)
        return flag | qtc.Qt.ItemIsEditable if self._editable else flag
        
    def headerData(self, section, orientation, role = qtc.Qt.DisplayRole):
        """
        PyQt5数据模型必须重写的关键函数。
        返回表头信息。
        格式类似data()函数。
        """
        hdata = super(QNumpyArray1Model, self).headerData(section, orientation, role)
        if self._hasHeader:
            if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
                if orientation == qtc.Qt.Horizontal:
                    return ''
                elif orientation == qtc.Qt.Vertical:
                    return str(self.headerArray[section])
            elif role == qtc.Qt.TextAlignmentRole:
                return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter
            else:
                return hdata
        return qtc.QVariant()
        
    def setData(self, index, value, role=qtc.Qt.EditRole):
        """
        PyQt5可编辑数据模型必须重写的关键函数。
        将编辑器传入的值写入缓存数组nparray。
        """
        if self.dtype() == int:#由于编辑器传入值均为str类型，需进行相应的数据类型转换及校验。
            value_dtype, ok = str2int(value)
        elif self.dtype() == float:
            value_dtype, ok = str2float(value)
        elif self.dtype() == str:
            value_dtype, ok = value, True
        elif self.dtype() == object:
            value_dtype, ok = value, True
        if ok:
            self.npArray[index.row()] = value_dtype
            self.dataChanged.emit(index, index)
            return True
        return False

class QNumpyArray1Model_Transpose(QNumpyArray1Model):
    """
    用于PyQt5的Numpy一维array数组模型(横向)。
    """
    def setData_Batch(self, dataArray):
        if type(dataArray) is np.ndarray:
            if dataArray.shape[0] == self.rank():
                self.npArray[:] = dataArray
                self.dataChanged.emit(self.index(0, 0), self.index(0, self.rank() - 1))
            else:
                raise SizeError(dataArray.shape[0])
        else:
            raise TypeError('The input argument must be a numpy.ndarray object.')

    def setHeader_Batch(self, headerArray):
        """
        批量设置表头信息。
        参数：
            1. headerArray            一维Numpy数组，长度与隶属度向量一致。
        """
        if type(headerArray) is np.ndarray:
            if headerArray.shape[0] == self.rank():
                self.headerArray = headerArray
                self._hasHeader = True
                self.headerDataChanged.emit(qtc.Qt.Horizontal, 0, self.rank() - 1)
            else:
                raise SizeError(headerArray.shape[0])
        else:
            raise TypeError('The input argument must be a numpy.ndarray object.')

    def rowCount(self, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型的行数。
        """
        return 1

    def columnCount(self, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型的列数。
        """
        return self.npArray.shape[0]    

    def index(self, row, column, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型索引对象(Index)。
        """
        return self.createIndex(row, column, self.npArray[column])

    def data(self, index, role=qtc.Qt.DisplayRole):
        """
        PyQt5数据模型必须重写的关键函数。
        返回在指定的Role下的模型数据。
        其中DisplayRole为视图(View)中显示的数据；EditRole为传给编辑器的数据；TextAlignmentRole为数据显示时的对齐方式。
        """
        if not index.isValid() or \
           not 0 <= index.column() <= self.npArray.shape[0]:
            return qtc.QVariant()

        if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
            return str(self.npArray[index.column()])
        elif role == qtc.Qt.TextAlignmentRole:
            return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter            
        else:
            return qtc.QVariant()

    def headerData(self, section, orientation, role = qtc.Qt.DisplayRole):
        """
        PyQt5数据模型必须重写的关键函数。
        返回表头信息。
        格式类似data()函数。
        """
        hdata = super(QNumpyArray1Model_Transpose, self).headerData(section, orientation, role)
        if self._hasHeader:
            if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
                if orientation == qtc.Qt.Vertical:
                    return ''
                elif orientation == qtc.Qt.Horizontal:
                    return str(self.headerArray[section])
            elif role == qtc.Qt.TextAlignmentRole:
                return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter
            else:
                return hdata
        return qtc.QVariant()

    def setData(self, index, value, role=qtc.Qt.EditRole):
        """
        PyQt5可编辑数据模型必须重写的关键函数。
        将编辑器传入的值写入缓存数组nparray。
        """
        if self.dtype() == int:#由于编辑器传入值均为str类型，需进行相应的数据类型转换及校验。
            value_dtype, ok = str2int(value)
        elif self.dtype() == float:
            value_dtype, ok = str2float(value)
        elif self.dtype() == str:
            value_dtype, ok = value, True
        elif self.dtype() == object:
            value_dtype, ok = value, True
        if ok:
            self.npArray[index.column()] = value_dtype
            self.dataChanged.emit(index, index)
            return True
        return False
    
class QDataFrameModel(qtc.QAbstractTableModel):
    """
    用于PyQt5的Pandas.DataFrame数据模型。
    """
    editConfirmed = qtc.pyqtSignal()#确认编辑的信号。
    editRefuted = qtc.pyqtSignal()#撤销编辑的信号。

    def __init__(self, dataFrame = None, parent=None):
        """
        构造器。
        可选参数：
            1. dataFrame            Pandas.DataFrame对象。
            2. parent               父对象。一般留空即可。
        """
        super(QDataFrameModel, self).__init__(parent)
        if type(dataFrame) is type(None):#若指定了dataframe参数，则将dataframe赋予dataframe_orig参数；否则将一个空DataFrame赋予dataframe_orig参数
            self.setDataFrame(pd.DataFrame())
        else:
            self.setDataFrame(dataFrame)
        self._displayDecimal = 2
        self._editable = True

        self.editConfirmed.connect(self.cacheDataFrame)
        self.editRefuted.connect(self.cacheDataFrame)

    def cacheDataFrame(self):
        """
        生成dataframe_orig的一个缓存副本dataframe，用于界面编辑。
        dataframe_orig为实际外部传入的DataFrame对象。对dataframe_orig的改变会直接反应在外部，而副本dataframe则不会。
        """
        if self.dataFrame_Orig.shape[0] > 0 and self.dataFrame_Orig.shape[1] > 0:
            for j in range(self.dataFrame_Orig.shape[1]):
                self.dataFrame.rename(columns = {self.dataFrame.columns[j]: self.dataFrame_Orig.columns[j]}, inplace = True)
                for i in range(self.dataFrame_Orig.shape[0]):
                    self.dataFrame.iat[i, j] = self.dataFrame_Orig.iat[i, j]        
            self.dataFrame.infer_objects()
            self.dataChanged.emit(self.index(0, 0), self.index(self.dataFrame_Orig.shape[0] - 1, self.dataFrame_Orig.shape[1] -1))

    def setDataFrame(self, dataFrame):
        """
        设置数据模型对应的DataFrame对象。
        """
        if not isinstance(dataFrame, pd.DataFrame):
            raise TypeError("The input argument must be a pandas.DataFrame object.")

        self.layoutAboutToBeChanged.emit()
        self.dataFrame_Orig = dataFrame
        self.dataFrame = pd.DataFrame(np.empty((dataFrame.shape[0], dataFrame.shape[1])), index = dataFrame.index, dtype = object)
        self.cacheDataFrame()
        self.layoutChanged.emit()
        
    def setDataFrameFromFile(self, filename, filetype):
        """
        从文件中读取数据，存入模型的DataFrame对象。
        这一操作会改变模型内外的连接关系，请注意。
        """
        self.layoutAboutToBeChanged.emit()
        if filetype == 'CSV':
            self.dataFrame_Orig = pd.read_csv(filename, header = None, prefix = 'P')
        elif filetype == 'XLS':
            self.dataFrame_Orig = pd.read_excel(filename, header = None, prefix = 'P')
        self.dataFrame = pd.DataFrame(np.empty((self.dataFrame_Orig.shape[0], self.dataFrame_Orig.shape[1])))
        self.cacheDataFrame()
        self.layoutChanged.emit()
        
    def readDataFrameFromFile(self, filename, filetype):
        """
        从文件中读取数据，存入模型的缓存DataFrame对象。
        """
        self.layoutAboutToBeChanged.emit()
        if filetype == 'CSV':
            self.dataFrame = pd.read_csv(filename, header = 'infer')
        elif filetype == 'XLS':
            self.dataFrame = pd.read_excel(filename, header = 'infer')
        QDataFrameModel.clearDataFrameAndReshape(self.dataFrame_Orig, (self.dataFrame.shape[0], self.dataFrame.shape[1]))
        self.layoutChanged.emit()
        
    @staticmethod
    def clearDataFrameAndReshape(dataFrame, shape):
        dataFrame.drop(range(dataFrame.shape[0]), inplace = True)
        dataFrame.drop(dataFrame.columns, axis = 1, inplace = True)
        for i in range(shape[1]):
            dataFrame.insert(i, i, [])
        for j in range(shape[0]):
            dataFrame.loc[j] = [np.nan for i in range(shape[1])]
        
    def dtype(self, column):
        return self.dataFrame.dtypes.iat[column]

    def rank(self):
        return min(self.dataFrame_Orig.shape)

    def confirmEdit(self):
        """
        确认编辑时调用的槽函数。
        将缓存对象dataframe中的数据写入dataframe_orig，确认编辑。
        """
        if self.dataFrame_Orig.shape[0] > 0 and self.dataFrame_Orig.shape[1] > 0:
            for j in range(self.dataFrame_Orig.shape[1]):
                self.dataFrame_Orig.rename(columns = {self.dataFrame_Orig.columns[j]: self.dataFrame.columns[j]}, inplace = True)
                for i in range(self.dataFrame_Orig.shape[0]):
                    self.dataFrame_Orig.iat[i, j] = self.dataFrame.iat[i, j]
            self.editConfirmed.emit()

    def refuteEdit(self):
        """
        撤销编辑时调用的槽函数。
        """
        self.editRefuted.emit()

    def index(self, row, column, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型索引对象(Index)。
        """
        return self.createIndex(row, column, self.dataFrame.iat[row, column])

    def rowCount(self, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型的行数。
        """
        return self.dataFrame.shape[0]

    def columnCount(self, parent=qtc.QModelIndex()):
        """
        PyQt5数据模型必须重写的关键函数。
        返回模型的列数。
        """
        return self.dataFrame.shape[1]

    def data(self, index, role=qtc.Qt.DisplayRole):
        """
        PyQt5数据模型必须重写的关键函数。
        返回在指定的Role下的模型数据。
        其中DisplayRole为视图(View)中显示的数据；EditRole为传给编辑器的数据；TextAlignmentRole为数据显示时的对齐方式。
        """
        if not index.isValid() or \
           not 0 <= index.row() < self.dataFrame.shape[0] or \
           not 0 <= index.column() < self.dataFrame.shape[1]:
            return qtc.QVariant()

        if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
            try:
                return str(round(self.dataFrame.iat[index.row(), index.column()], self._displayDecimal))
            except TypeError:
                return str(self.dataFrame.iat[index.row(), index.column()])
        elif role == qtc.Qt.TextAlignmentRole:
            return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter
        else:
            return qtc.QVariant()

    def flags(self, index):
        """
        PyQt5数据模型必须重写的关键函数。
        返回指定索引对应的flag。
        为使模型数据可在视图中编辑，需要额外返回ItemIsEditable这一flag。
        """
        flag = super(QDataFrameModel, self).flags(index)
        return flag | qtc.Qt.ItemIsEditable if self._editable else flag

    def setData(self, index, value, role=qtc.Qt.EditRole):
        """
        PyQt5可编辑数据模型必须重写的关键函数。
        将编辑器传入的值写入缓存对象dataframe。
        """
        if self.dtype(index.column()) == int:
            value_dtype, ok = str2int(value)
        elif self.dtype(index.column()) == float:
            value_dtype, ok = str2float(value)
        elif selt.dtype(index.column()) == bool:
            value_dtype, ok = str2bool(value)
        elif self.dtype(index.column()) == str:
            value_dtype, ok = value, True
        elif self.dtype(index.column()) == object:
            value_dtype, ok = value, False
        else:
            value_dtype, ok = value, False
        if ok:
            self.dataFrame.iat[index.row(), index.column()] = value_dtype
            self.dataChanged.emit(index, index)
            return True
        return False

    def headerData(self, section, orientation, role = qtc.Qt.DisplayRole):
        """
        PyQt5数据模型必须重写的关键函数。
        返回表头信息。
        格式类似data()函数。
        """
        hdata = super(QDataFrameModel, self).headerData(section, orientation, role)
        if role == qtc.Qt.DisplayRole or role == qtc.Qt.EditRole:
            if orientation == qtc.Qt.Horizontal:
                return str(self.dataFrame.columns[section])
            elif orientation == qtc.Qt.Vertical:
                return str(self.dataFrame.index[section])
        elif role == qtc.Qt.TextAlignmentRole:
            return qtc.Qt.AlignHCenter | qtc.Qt.AlignVCenter        
        else:
            return hdata
        
    def setHeaderData(self, section, orientation, value, role = qtc.Qt.EditRole):
        """
        PyQt5可编辑数据模型必须重写的关键函数。
        将编辑器传入的值写入dataframe的columns列表中。
        格式类似setData()函数。
        未完工。
        """
        if orientation == qtc.Qt.Horizontal:
            self.dataFrame.columns[section] = str(value)
            self.headerDataChanged.emit(orientation, section, section)
            return True
        return False
        
    def addDataFrameRows(self, count = 1):
        """
        向dataframe中增加数行。
        可选参数：
            1. count            增加的行数，默认为1。
        """
        position = self.rowCount()
        if count < 1:
            return False
    
        if len(self.dataFrame.columns) == 0:
            # log an error message or warning
            return False        
        
        self.beginInsertRows(qtc.QModelIndex(), position, position + count - 1)
        defaultValues = []
        for dtype in self.dataFrame.dtypes:
            if dtype == int:
                val = 0
            elif dtype == float:
                val = 0.0
            elif dtype == bool:
                val = True
            elif dtype == str:
                val = ''
            else:
                val = dtype.type()
            defaultValues.append(val)#根据每列不同的数据类型设置不同的初始值。
        for i in range(count):
            self.dataFrame.loc[position + i] = defaultValues
        self.dataFrame.reset_index()#DataFrame中插入数据后必须执行的函数
        self.endInsertRows()
        return True
    
    def addDataFrameColumn(self, columnName, dtype = float, defaultValue = None):
        """
        向dataframe中插入一列。
        必要参数：
            1. columnName            列名称。
        可选参数：
            1. dtype                 该列的数据类型，默认为浮点型。
            2. defaultValue          该列数据的初始值，默认为None。
        """
        elements = self.rowCount()
        columnPosition = self.columnCount()#默认插入在最右侧
        newColumn = pd.Series([defaultValue]*elements, index=self.dataFrame.index, dtype=dtype)#生成一个Series，随后插入

        self.beginInsertColumns(qtc.QModelIndex(), columnPosition - 1, columnPosition - 1)        
        try:
            self.dataFrame.insert(columnPosition, columnName, newColumn, allow_duplicates=False)
        except ValueError as e:
            # columnName does already exist
            return False        
        self.endInsertColumns()
        return True
    
    def removeDataFrameRows(self, rows):
        """
        从dataframe中移除数行。
        必要参数：
            1. rows            由需要移除的行索引号组成的列表
        """
        if rows:
            position = min(rows)
            count = len(rows)
            self.beginRemoveRows(qtc.QModelIndex(), position, position + count - 1)        
            removedAny = False
            for idx, line in self.dataFrame.iterrows():
                if idx in rows:
                    removedAny = True
                    self.dataFrame.drop(idx, inplace=True)
        
            if not removedAny:
                return False

            self.dataFrame.reset_index(inplace=True, drop=True)
            self.endRemoveRows()
            return True
        return False            
    
    def removeDataFrameColumns(self, columns):
        """
        从dataframe中移除数列。
        必要参数：
            1. columns            由需要移除的列的(索引号, 列名称)元组组成的列表。
        """
        if columns:
            deleted = 0
            errored = False
            for (position, name) in columns:
                position = position - deleted
                if position < 0:
                    position = 0
                self.beginRemoveColumns(qtc.QModelIndex(), position, position)
                try:
                    self.dataFrame.drop(name, axis=1, inplace=True)
                except ValueError as e:
                    errored = True
                    continue
                self.endRemoveColumns()
                deleted += 1
            if self.columnCount() > 0:
                self.dataChanged.emit(self.index(0, position - 1 if position == self.columnCount() else position),
                                      self.index(self.rowCount() - 1, self.columnCount() - 1 if position + deleted > self.columnCount() else position + deleted - 1))
            else:
                self.removeDataFrameRows(range(self.rowCount()))
                self.dataChanged.emit(qtc.QModelIndex(), qtc.QModelIndex())
                
            if errored:
                return False
            else:
                return True
        return False