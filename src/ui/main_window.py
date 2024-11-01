# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainxiOpuU.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QMainWindow, QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_Main(object):
    def setupUi(self, Main):
        if not Main.objectName():
            Main.setObjectName(u"Main")
        Main.resize(800, 600)
        self.actionEspirometria = QAction(Main)
        self.actionEspirometria.setObjectName(u"actionEspirometria")
        self.actionECG = QAction(Main)
        self.actionECG.setObjectName(u"actionECG")
        self.actionEOG = QAction(Main)
        self.actionEOG.setObjectName(u"actionEOG")
        self.centralwidget = QWidget(Main)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalFrame = QFrame(self.centralwidget)
        self.horizontalFrame.setObjectName(u"horizontalFrame")
        self.horizontalFrame.setMaximumSize(QSize(16777215, 40))
        self.horizontalLayout = QHBoxLayout(self.horizontalFrame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.layout_toolbar = QHBoxLayout()
        self.layout_toolbar.setObjectName(u"layout_toolbar")
        self.btn_open = QPushButton(self.horizontalFrame)
        self.btn_open.setObjectName(u"btn_open")

        self.layout_toolbar.addWidget(self.btn_open)

        self.line = QFrame(self.horizontalFrame)
        self.line.setObjectName(u"line")
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setLineWidth(3)
        self.line.setFrameShape(QFrame.Shape.VLine)

        self.layout_toolbar.addWidget(self.line)


        self.horizontalLayout.addLayout(self.layout_toolbar)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)

        self.serial_list = QComboBox(self.horizontalFrame)
        self.serial_list.setObjectName(u"serial_list")

        self.horizontalLayout.addWidget(self.serial_list)

        self.btn_connect = QPushButton(self.horizontalFrame)
        self.btn_connect.setObjectName(u"btn_connect")
        self.btn_connect.setCheckable(True)

        self.horizontalLayout.addWidget(self.btn_connect)


        self.verticalLayout.addWidget(self.horizontalFrame)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalFrame_3 = QFrame(self.centralwidget)
        self.horizontalFrame_3.setObjectName(u"horizontalFrame_3")
        self.horizontalFrame_3.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_3 = QHBoxLayout(self.horizontalFrame_3)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(1, -1, 1, -1)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.btn_start = QPushButton(self.horizontalFrame_3)
        self.btn_start.setObjectName(u"btn_start")

        self.horizontalLayout_4.addWidget(self.btn_start)

        self.btn_clear = QPushButton(self.horizontalFrame_3)
        self.btn_clear.setObjectName(u"btn_clear")

        self.horizontalLayout_4.addWidget(self.btn_clear)

        self.btn_reset = QPushButton(self.horizontalFrame_3)
        self.btn_reset.setObjectName(u"btn_reset")

        self.horizontalLayout_4.addWidget(self.btn_reset)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.btn_save = QPushButton(self.horizontalFrame_3)
        self.btn_save.setObjectName(u"btn_save")

        self.horizontalLayout_4.addWidget(self.btn_save)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_4)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.horizontalFrame_3)

        Main.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Main)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 23))
        self.menuArchivo = QMenu(self.menubar)
        self.menuArchivo.setObjectName(u"menuArchivo")
        self.menuNuevo = QMenu(self.menuArchivo)
        self.menuNuevo.setObjectName(u"menuNuevo")
        Main.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Main)
        self.statusbar.setObjectName(u"statusbar")
        Main.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuArchivo.menuAction())
        self.menuArchivo.addAction(self.menuNuevo.menuAction())
        self.menuNuevo.addSeparator()
        self.menuNuevo.addAction(self.actionEspirometria)
        self.menuNuevo.addAction(self.actionECG)
        self.menuNuevo.addAction(self.actionEOG)

        self.retranslateUi(Main)

        QMetaObject.connectSlotsByName(Main)
    # setupUi

    def retranslateUi(self, Main):
        Main.setWindowTitle(QCoreApplication.translate("Main", u"FisioaccessPC", None))
        self.actionEspirometria.setText(QCoreApplication.translate("Main", u"Espirometria", None))
        self.actionECG.setText(QCoreApplication.translate("Main", u"ECG", None))
        self.actionEOG.setText(QCoreApplication.translate("Main", u"EMG", None))
        self.btn_open.setText(QCoreApplication.translate("Main", u"Abrir", None))
        self.btn_connect.setText(QCoreApplication.translate("Main", u"conectar", None))
        self.btn_start.setText(QCoreApplication.translate("Main", u"Iniciar", None))
        self.btn_clear.setText(QCoreApplication.translate("Main", u"Borrar", None))
        self.btn_reset.setText(QCoreApplication.translate("Main", u"Reset", None))
        self.btn_save.setText(QCoreApplication.translate("Main", u"Guardar", None))
        self.menuArchivo.setTitle(QCoreApplication.translate("Main", u"Archivo", None))
        self.menuNuevo.setTitle(QCoreApplication.translate("Main", u"Nuevo", None))
    # retranslateUi

