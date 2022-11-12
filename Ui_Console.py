# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_Console.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConsoleWidget(object):
    def setupUi(self, ConsoleWidget):
        ConsoleWidget.setObjectName("ConsoleWidget")
        ConsoleWidget.setWindowModality(QtCore.Qt.WindowModal)
        ConsoleWidget.resize(800, 600)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ConsoleWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(ConsoleWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.qwidgetLabel = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.qwidgetLabel.sizePolicy().hasHeightForWidth())
        self.qwidgetLabel.setSizePolicy(sizePolicy)
        self.qwidgetLabel.setText("")
        self.qwidgetLabel.setObjectName("qwidgetLabel")
        self.horizontalLayout_3.addWidget(self.qwidgetLabel)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.consoleGroupBox = QtWidgets.QGroupBox(ConsoleWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.consoleGroupBox.sizePolicy().hasHeightForWidth())
        self.consoleGroupBox.setSizePolicy(sizePolicy)
        self.consoleGroupBox.setObjectName("consoleGroupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.consoleGroupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_2.addWidget(self.consoleGroupBox)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout_2.setContentsMargins(10, 0, 10, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.clearPushButton = QtWidgets.QPushButton(ConsoleWidget)
        self.clearPushButton.setObjectName("clearPushButton")
        self.horizontalLayout_2.addWidget(self.clearPushButton)
        self.closePushButton = QtWidgets.QPushButton(ConsoleWidget)
        self.closePushButton.setObjectName("closePushButton")
        self.horizontalLayout_2.addWidget(self.closePushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.setStretch(0, 3)
        self.verticalLayout_2.setStretch(1, 29)
        self.verticalLayout_2.setStretch(2, 4)

        self.retranslateUi(ConsoleWidget)
        QtCore.QMetaObject.connectSlotsByName(ConsoleWidget)

    def retranslateUi(self, ConsoleWidget):
        _translate = QtCore.QCoreApplication.translate
        ConsoleWidget.setWindowTitle(_translate("ConsoleWidget", "控制台"))
        self.groupBox.setTitle(_translate("ConsoleWidget", "父窗口（可用‘CurrentWidget’或‘cw’访问；访问程序主窗口可用‘Mainwindow’或‘mw’；访问控制台自身可用‘self’）"))
        self.consoleGroupBox.setTitle(_translate("ConsoleWidget", "控制台"))
        self.clearPushButton.setText(_translate("ConsoleWidget", "清空"))
        self.closePushButton.setText(_translate("ConsoleWidget", "关闭"))

