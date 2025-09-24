# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fisioaccessrsScNA.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QSpinBox, QStatusBar,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_Main(object):
    def setupUi(self, Main):
        if not Main.objectName():
            Main.setObjectName(u"Main")
        Main.resize(1301, 755)
        Main.setStyleSheet(u"/* Estilo general */\n"
"QWidget {\n"
"    background-color: #f5f5f5;\n"
"    color: #000000;\n"
"    font-family: Arial, sans-serif;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"/* Ventana principal */\n"
"QMainWindow {\n"
"    background-color: #f5f5f5;\n"
"}\n"
"\n"
"/* Men\u00fas y barras de herramientas */\n"
"QMenuBar {\n"
"    background-color: #f0f0f0;\n"
"    border-bottom: 1px solid #cccccc;\n"
"}\n"
"\n"
"QMenuBar::item {\n"
"    spacing: 5px;\n"
"    padding: 3px 8px;\n"
"    background: transparent;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"QMenuBar::item:selected {\n"
"    background: #e6e6e6;\n"
"}\n"
"\n"
"QMenuBar::item:pressed {\n"
"    background: #d9d9d9;\n"
"}\n"
"\n"
"QMenu {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #cccccc;\n"
"}\n"
"\n"
"QMenu::item {\n"
"    padding: 5px 30px 5px 20px;\n"
"    border: 1px solid transparent;\n"
"}\n"
"\n"
"QMenu::item:selected {\n"
"    background-color: #e6f2ff;\n"
"    border-color: #3399ff;\n"
"}\n"
"\n"
"QMenu::separator {\n"
"    he"
                        "ight: 1px;\n"
"    background: #e0e0e0;\n"
"    margin: 4px 10px;\n"
"}\n"
"\n"
"/* Barras de herramientas */\n"
"QToolBar {\n"
"    background-color: #f0f0f0;\n"
"    border-bottom: 1px solid #cccccc;\n"
"    padding: 2px;\n"
"    spacing: 1px;\n"
"}\n"
"\n"
"QToolBar::separator {\n"
"    width: 1px;\n"
"    background-color: #cccccc;\n"
"    margin: 3px 6px;\n"
"}\n"
"\n"
"QToolBar QToolButton {\n"
"    background-color: transparent;\n"
"    border: 1px solid transparent;\n"
"    border-radius: 3px;\n"
"    padding: 3px;\n"
"    margin: 1px;\n"
"}\n"
"\n"
"QToolBar QToolButton:hover {\n"
"    background-color: #e6e6e6;\n"
"    border: 1px solid #cccccc;\n"
"}\n"
"\n"
"QToolBar QToolButton:pressed,\n"
"QToolBar QToolButton:checked {\n"
"    background-color: #d0d0d0;\n"
"    border: 1px solid #999999;\n"
"}\n"
"\n"
"/* Botones est\u00e1ndar */\n"
"QPushButton {\n"
"    background-color: #e6e6e6;\n"
"    border: 1px solid #cccccc;\n"
"    border-radius: 3px;\n"
"    padding: 6px 12px;\n"
"    min-width: 80px;\n"
""
                        "}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #d9d9d9;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #d0d0d0;\n"
"    border: 1px solid #999999;\n"
"}\n"
"\n"
"QPushButton:disabled {\n"
"    background-color: #f5f5f5;\n"
"    color: #9E9E9E;\n"
"    border: 1px solid #e0e0e0;\n"
"}\n"
"\n"
"/* Botones especiales */\n"
"QPushButton#primaryButton {\n"
"    background-color: #3399ff;\n"
"    color: white;\n"
"    border: 1px solid #0066cc;\n"
"}\n"
"\n"
"QPushButton#primaryButton:hover {\n"
"    background-color: #0066cc;\n"
"}\n"
"\n"
"QPushButton#successButton {\n"
"    background-color: #4CAF50;\n"
"    color: white;\n"
"    border: 1px solid #2E7D32;\n"
"}\n"
"\n"
"QPushButton#dangerButton {\n"
"    background-color: #F44336;\n"
"    color: white;\n"
"    border: 1px solid #C62828;\n"
"}\n"
"\n"
"/* Paneles, Frames y GroupBox */\n"
"QFrame {\n"
"    border: 1px solid #cccccc;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QGroupBox {\n"
"    background-color: #ffffff;\n"
"    border: 1"
                        "px solid #cccccc;\n"
"    border-radius: 5px;\n"
"    margin-top: 15px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position: top left;\n"
"    background-color: transparent;\n"
"    padding: 5px;\n"
"    color: #333333;\n"
"}\n"
"\n"
"/* Tabs */\n"
"QTabWidget::pane {\n"
"    border: 1px solid #cccccc;\n"
"    border-radius: 3px;\n"
"    top: -1px;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    background-color: #e6e6e6;\n"
"    border: 1px solid #cccccc;\n"
"    padding: 5px 10px;\n"
"    margin-right: 2px;\n"
"    border-top-left-radius: 4px;\n"
"    border-top-right-radius: 4px;\n"
"}\n"
"\n"
"QTabBar::tab:selected {\n"
"    background-color: #ffffff;\n"
"    border-bottom-color: #ffffff;\n"
"}\n"
"\n"
"QTabBar::tab:hover:!selected {\n"
"    background-color: #f0f0f0;\n"
"}\n"
"\n"
"/* Listas, tablas y vistas */\n"
"QListView, QTreeView, QTableView {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #cccccc;\n"
"    selection-backgrou"
                        "nd-color: #e6f2ff;\n"
"    selection-color: #000000;\n"
"    alternate-background-color: #f9f9f9;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    background-color: #e6e6e6;\n"
"    border: 1px solid #cccccc;\n"
"    padding: 4px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"/* ComboBox (desplegables) */\n"
"QComboBox {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #cccccc;\n"
"    border-radius: 3px;\n"
"    padding: 3px 18px 3px 5px;\n"
"    min-width: 6em;\n"
"}\n"
"\n"
"QComboBox:hover {\n"
"    border: 1px solid #3399ff;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 15px;\n"
"    border-left: 1px solid #cccccc;\n"
"}\n"
"\n"
"/* SpinBox (selectores num\u00e9ricos) */\n"
"QSpinBox, QDoubleSpinBox {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #cccccc;\n"
"    border-radius: 3px;\n"
"    padding: 3px 5px;\n"
"}\n"
"\n"
"/* Checkbox */\n"
"QCheckBox::indicator {\n"
"    width: 13px;\n"
"    height: 13p"
                        "x;\n"
"    border: 1px solid #cccccc;\n"
"    border-radius: 2px;\n"
"    background-color: #ffffff;\n"
"}\n"
"\n"
"QCheckBox::indicator:checked {\n"
"    background-color: #3399ff;\n"
"    border-color: #0066cc;\n"
"}\n"
"\n"
"/* Radio Button */\n"
"QRadioButton::indicator {\n"
"    width: 13px;\n"
"    height: 13px;\n"
"    border: 1px solid #cccccc;\n"
"    border-radius: 7px;\n"
"    background-color: #ffffff;\n"
"}\n"
"\n"
"QRadioButton::indicator:checked {\n"
"    background-color: qradialgradient(cx:0.5, cy:0.5, radius:0.4, fx:0.5, fy:0.5, stop:0 #3399ff, stop:1 #ffffff);\n"
"    border-color: #0066cc;\n"
"}\n"
"\n"
"/* Campos de texto */\n"
"QLineEdit, QTextEdit, QPlainTextEdit {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #cccccc;\n"
"    border-radius: 3px;\n"
"    padding: 3px;\n"
"}\n"
"\n"
"QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {\n"
"    border: 1px solid #3399ff;\n"
"}\n"
"\n"
"/* Sliders (deslizadores) */\n"
"QSlider::groove:horizontal {\n"
"    border: 1px soli"
                        "d #cccccc;\n"
"    height: 6px;\n"
"    background: #e6e6e6;\n"
"    border-radius: 3px;\n"
"    margin: 2px 0;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"    background: #3399ff;\n"
"    border: 1px solid #0066cc;\n"
"    width: 14px;\n"
"    height: 14px;\n"
"    margin: -5px 0;\n"
"    border-radius: 7px;\n"
"}\n"
"\n"
"/* ProgressBar (barras de progreso) */\n"
"QProgressBar {\n"
"    border: 1px solid #cccccc;\n"
"    border-radius: 3px;\n"
"    background-color: #e6e6e6;\n"
"    text-align: center;\n"
"    padding: 1px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #3399ff;\n"
"    width: 10px;\n"
"    margin: 0.5px;\n"
"}\n"
"\n"
"/* Barras de desplazamiento */\n"
"QScrollBar:horizontal {\n"
"    border: 1px solid #cccccc;\n"
"    background: #f5f5f5;\n"
"    height: 15px;\n"
"    margin: 0px 15px 0 15px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background: #d0d0d0;\n"
"    min-width: 30px;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"    border"
                        ": 1px solid #cccccc;\n"
"    background: #f5f5f5;\n"
"    width: 15px;\n"
"    margin: 15px 0 15px 0;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: #d0d0d0;\n"
"    min-height: 30px;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"/* ToolTips */\n"
"QToolTip {\n"
"    background-color: #ffffd0;\n"
"    border: 1px solid #ccccaa;\n"
"    border-radius: 3px;\n"
"    padding: 5px;\n"
"    color: #333333;\n"
"    font-size: 11px;\n"
"}\n"
"\n"
"/* Barra de estado */\n"
"QStatusBar {\n"
"    background-color: #f0f0f0;\n"
"    color: #333333;\n"
"    border-top: 1px solid #cccccc;\n"
"}\n"
"\n"
"/* Estilos para se\u00f1ales */\n"
"QLabel[class=\"ECGSignal\"] {\n"
"    color: #ff6666;\n"
"}\n"
"\n"
"QLabel[class=\"EEGSignal\"] {\n"
"    color: #6666ff;\n"
"}\n"
"\n"
"QLabel[class=\"EMGSignal\"] {\n"
"    color: #66cc66;\n"
"}\n"
"\n"
"QLabel[class=\"SpiroSignal\"] {\n"
"    color: #ff9933;\n"
"}\n"
"\n"
"/* Estilos para toolbars agrupados */\n"
"QFrame[frameShape=\"5\"] {  /* 5 es VLine */\n"
"    color"
                        ": #cccccc;\n"
"    width: 1px;\n"
"    height: 20px;\n"
"    margin: 2px 8px;\n"
"}\n"
"\n"
"/* T\u00edtulos de grupos en toolbars */\n"
"QToolBar QLabel.group-title {\n"
"    font-size: 10px;\n"
"    color: #666666;\n"
"    background: transparent;\n"
"    padding: 0px 4px;\n"
"    margin-bottom: -2px;\n"
"}")
        self.centralwidget = QWidget(Main)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setMaximumSize(QSize(16777215, 35))
        self.frame.setStyleSheet(u"QPushButton {\n"
"    min-width: 0px;\n"
"    padding: 3px;\n"
"}\n"
"QComboBox {\n"
"    background-color: #ffffff;\n"
"    border: 1px solid #cccccc;\n"
"    border-radius: 3px;\n"
"    padding: 3px 18px 3px 5px;\n"
"    min-width: 0px; /* Reducir o quitar el ancho m\u00ednimo predeterminado */\n"
"}")
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(10, 0, 10, 0)
        self.pushButton = QPushButton(self.frame)
        self.pushButton.setObjectName(u"pushButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMinimumSize(QSize(8, 0))
        self.pushButton.setMaximumSize(QSize(35, 16777215))
        self.pushButton.setStyleSheet(u"")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.FolderOpen))
        self.pushButton.setIcon(icon)

        self.horizontalLayout.addWidget(self.pushButton)

        self.pushButton_2 = QPushButton(self.frame)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMinimumSize(QSize(8, 0))
        self.pushButton_2.setMaximumSize(QSize(35, 16777215))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.MediaFlash))
        self.pushButton_2.setIcon(icon1)

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(self.frame)
        self.pushButton_3.setObjectName(u"pushButton_3")
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setMinimumSize(QSize(8, 0))
        self.pushButton_3.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_3)

        self.line_2 = QFrame(self.frame)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.VLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line_2)

        self.line_3 = QFrame(self.frame)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.VLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line_3)

        self.pushButton_9 = QPushButton(self.frame)
        self.pushButton_9.setObjectName(u"pushButton_9")
        self.pushButton_9.setMinimumSize(QSize(8, 0))
        self.pushButton_9.setMaximumSize(QSize(35, 16777215))
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ZoomIn))
        self.pushButton_9.setIcon(icon2)

        self.horizontalLayout.addWidget(self.pushButton_9)

        self.pushButton_7 = QPushButton(self.frame)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setMinimumSize(QSize(8, 0))
        self.pushButton_7.setMaximumSize(QSize(35, 16777215))
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ZoomOut))
        self.pushButton_7.setIcon(icon3)

        self.horizontalLayout.addWidget(self.pushButton_7)

        self.comboBox_3 = QComboBox(self.frame)
        self.comboBox_3.setObjectName(u"comboBox_3")
        self.comboBox_3.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.comboBox_3)

        self.pushButton_8 = QPushButton(self.frame)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setMinimumSize(QSize(8, 0))
        self.pushButton_8.setMaximumSize(QSize(35, 16777215))
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ZoomFitBest))
        self.pushButton_8.setIcon(icon4)

        self.horizontalLayout.addWidget(self.pushButton_8)

        self.line_4 = QFrame(self.frame)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.VLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line_4)

        self.pushButton_13 = QPushButton(self.frame)
        self.pushButton_13.setObjectName(u"pushButton_13")
        self.pushButton_13.setMinimumSize(QSize(8, 0))
        self.pushButton_13.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_13)

        self.pushButton_10 = QPushButton(self.frame)
        self.pushButton_10.setObjectName(u"pushButton_10")
        self.pushButton_10.setMinimumSize(QSize(8, 0))
        self.pushButton_10.setMaximumSize(QSize(35, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_10)

        self.pushButton_11 = QPushButton(self.frame)
        self.pushButton_11.setObjectName(u"pushButton_11")
        self.pushButton_11.setMinimumSize(QSize(8, 0))
        self.pushButton_11.setMaximumSize(QSize(55, 16777215))
        self.pushButton_11.setStyleSheet(u"")

        self.horizontalLayout.addWidget(self.pushButton_11)

        self.pushButton_12 = QPushButton(self.frame)
        self.pushButton_12.setObjectName(u"pushButton_12")
        self.pushButton_12.setMinimumSize(QSize(8, 0))
        self.pushButton_12.setMaximumSize(QSize(55, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_12)

        self.comboBox_2 = QComboBox(self.frame)
        self.comboBox_2.setObjectName(u"comboBox_2")
        sizePolicy.setHeightForWidth(self.comboBox_2.sizePolicy().hasHeightForWidth())
        self.comboBox_2.setSizePolicy(sizePolicy)
        self.comboBox_2.setMaximumSize(QSize(50, 16777215))

        self.horizontalLayout.addWidget(self.comboBox_2)

        self.line_5 = QFrame(self.frame)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.VLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line_5)

        self.pushButton_14 = QPushButton(self.frame)
        self.pushButton_14.setObjectName(u"pushButton_14")
        self.pushButton_14.setMinimumSize(QSize(8, 0))
        self.pushButton_14.setMaximumSize(QSize(55, 16777215))
        icon5 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentPrint))
        self.pushButton_14.setIcon(icon5)

        self.horizontalLayout.addWidget(self.pushButton_14)

        self.pushButton_15 = QPushButton(self.frame)
        self.pushButton_15.setObjectName(u"pushButton_15")
        self.pushButton_15.setMinimumSize(QSize(8, 0))
        self.pushButton_15.setMaximumSize(QSize(55, 16777215))
        icon6 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentPrintPreview))
        self.pushButton_15.setIcon(icon6)

        self.horizontalLayout.addWidget(self.pushButton_15)

        self.pushButton_16 = QPushButton(self.frame)
        self.pushButton_16.setObjectName(u"pushButton_16")
        self.pushButton_16.setMinimumSize(QSize(8, 0))
        self.pushButton_16.setMaximumSize(QSize(55, 16777215))
        icon7 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        self.pushButton_16.setIcon(icon7)

        self.horizontalLayout.addWidget(self.pushButton_16)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout.addWidget(self.line)


        self.verticalLayout_3.addWidget(self.frame)

        self.horizontalFrame_3 = QFrame(self.centralwidget)
        self.horizontalFrame_3.setObjectName(u"horizontalFrame_3")
        self.horizontalFrame_3.setMaximumSize(QSize(16777215, 70))
        self.horizontalLayout_3 = QHBoxLayout(self.horizontalFrame_3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.groupBox_7 = QGroupBox(self.horizontalFrame_3)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.groupBox_7.setMaximumSize(QSize(16777215, 70))
        self.horizontalLayout_9 = QHBoxLayout(self.groupBox_7)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(9, 3, -1, 3)
        self.btn_test_ecg = QPushButton(self.groupBox_7)
        self.btn_test_ecg.setObjectName(u"btn_test_ecg")

        self.horizontalLayout_9.addWidget(self.btn_test_ecg)

        self.btn_test_eeg = QPushButton(self.groupBox_7)
        self.btn_test_eeg.setObjectName(u"btn_test_eeg")

        self.horizontalLayout_9.addWidget(self.btn_test_eeg)

        self.btn_test_emg = QPushButton(self.groupBox_7)
        self.btn_test_emg.setObjectName(u"btn_test_emg")

        self.horizontalLayout_9.addWidget(self.btn_test_emg)

        self.btn_test_spiro = QPushButton(self.groupBox_7)
        self.btn_test_spiro.setObjectName(u"btn_test_spiro")

        self.horizontalLayout_9.addWidget(self.btn_test_spiro)


        self.horizontalLayout_3.addWidget(self.groupBox_7)

        self.groupBox_6 = QGroupBox(self.horizontalFrame_3)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.groupBox_6.setMaximumSize(QSize(16777215, 70))

        self.horizontalLayout_3.addWidget(self.groupBox_6)


        self.verticalLayout_3.addWidget(self.horizontalFrame_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, 6, -1)
        self.frame1 = QFrame(self.centralwidget)
        self.frame1.setObjectName(u"frame1")
        self.frame1.setMinimumSize(QSize(500, 0))
        self.graph_layout = QVBoxLayout(self.frame1)
        self.graph_layout.setObjectName(u"graph_layout")

        self.horizontalLayout_2.addWidget(self.frame1)

        self.control_panel = QFrame(self.centralwidget)
        self.control_panel.setObjectName(u"control_panel")
        self.control_panel.setMinimumSize(QSize(300, 0))
        self.control_panel.setMaximumSize(QSize(450, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.control_panel)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_7 = QLabel(self.control_panel)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMaximumSize(QSize(16777215, 30))
        self.label_7.setLineWidth(0)
        self.label_7.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_7)

        self.tabWidget = QTabWidget(self.control_panel)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy1)
        self.tab_1 = QWidget()
        self.tab_1.setObjectName(u"tab_1")
        self.verticalLayout_9 = QVBoxLayout(self.tab_1)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.gridFrame = QFrame(self.tab_1)
        self.gridFrame.setObjectName(u"gridFrame")
        self.gridLayout = QGridLayout(self.gridFrame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.btn_connect = QPushButton(self.gridFrame)
        self.btn_connect.setObjectName(u"btn_connect")

        self.gridLayout.addWidget(self.btn_connect, 1, 1, 1, 1)

        self.label = QLabel(self.gridFrame)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setBold(True)
        self.label.setFont(font)
        self.label.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label.setScaledContents(False)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.serial_list = QComboBox(self.gridFrame)
        self.serial_list.setObjectName(u"serial_list")

        self.gridLayout.addWidget(self.serial_list, 1, 0, 1, 1)

        self.pushButton_23 = QPushButton(self.gridFrame)
        self.pushButton_23.setObjectName(u"pushButton_23")
        self.pushButton_23.setStyleSheet(u"background-color: rgb(51, 153, 255);")

        self.gridLayout.addWidget(self.pushButton_23, 2, 1, 1, 1)


        self.verticalLayout_9.addWidget(self.gridFrame)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_5 = QLabel(self.tab_1)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 2, 0, 1, 1)

        self.label_3 = QLabel(self.tab_1)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)

        self.label_4 = QLabel(self.tab_1)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 5, 0, 1, 1)

        self.label_6 = QLabel(self.tab_1)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)

        self.btn_reset = QPushButton(self.tab_1)
        self.btn_reset.setObjectName(u"btn_reset")
        self.btn_reset.setStyleSheet(u"background-color: rgb(255, 204, 0);")

        self.gridLayout_2.addWidget(self.btn_reset, 5, 3, 1, 1)

        self.pushButton_25 = QPushButton(self.tab_1)
        self.pushButton_25.setObjectName(u"pushButton_25")

        self.gridLayout_2.addWidget(self.pushButton_25, 5, 1, 1, 1)

        self.pushButton_26 = QPushButton(self.tab_1)
        self.pushButton_26.setObjectName(u"pushButton_26")

        self.gridLayout_2.addWidget(self.pushButton_26, 5, 2, 1, 1)

        self.checkBox = QCheckBox(self.tab_1)
        self.checkBox.setObjectName(u"checkBox")

        self.gridLayout_2.addWidget(self.checkBox, 2, 3, 1, 1)

        self.spinBox = QSpinBox(self.tab_1)
        self.spinBox.setObjectName(u"spinBox")

        self.gridLayout_2.addWidget(self.spinBox, 2, 1, 1, 2)

        self.spinBox_2 = QSpinBox(self.tab_1)
        self.spinBox_2.setObjectName(u"spinBox_2")

        self.gridLayout_2.addWidget(self.spinBox_2, 1, 1, 1, 2)

        self.horizontalSlider = QSlider(self.tab_1)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout_2.addWidget(self.horizontalSlider, 3, 1, 1, 2)

        self.label_2 = QLabel(self.tab_1)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 4)


        self.verticalLayout_9.addLayout(self.gridLayout_2)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.pushButton_29 = QPushButton(self.tab_1)
        self.pushButton_29.setObjectName(u"pushButton_29")
        self.pushButton_29.setStyleSheet(u"background-color: rgb(255, 204, 0);")

        self.gridLayout_4.addWidget(self.pushButton_29, 1, 1, 1, 1)

        self.btn_start = QPushButton(self.tab_1)
        self.btn_start.setObjectName(u"btn_start")
        self.btn_start.setStyleSheet(u"background-color: #66cc66;")

        self.gridLayout_4.addWidget(self.btn_start, 1, 0, 1, 1)

        #self.btn_clear = QPushButton(self.tab_1)
        #self.btn_clear.setObjectName(u"btn_clear")
        #self.btn_clear.setStyleSheet(u"background-color: rgb(244, 67, 54);")

        #self.gridLayout_4.addWidget(self.btn_clear, 1, 2, 1, 1)

        self.label_9 = QLabel(self.tab_1)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_4.addWidget(self.label_9, 2, 0, 1, 1)

        self.label_10 = QLabel(self.tab_1)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_4.addWidget(self.label_10, 2, 1, 1, 1)

        self.label_11 = QLabel(self.tab_1)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_4.addWidget(self.label_11, 2, 2, 1, 1)

        self.label_8 = QLabel(self.tab_1)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_4.addWidget(self.label_8, 0, 0, 1, 3)


        self.verticalLayout_9.addLayout(self.gridLayout_4)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.pushButton_32 = QPushButton(self.tab_1)
        self.pushButton_32.setObjectName(u"pushButton_32")

        self.gridLayout_3.addWidget(self.pushButton_32, 3, 2, 1, 1)

        self.label_13 = QLabel(self.tab_1)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_3.addWidget(self.label_13, 1, 0, 1, 1)

        self.btn_save = QPushButton(self.tab_1)
        self.btn_save.setObjectName(u"btn_save")

        self.gridLayout_3.addWidget(self.btn_save, 3, 0, 1, 1)

        self.pushButton_33 = QPushButton(self.tab_1)
        self.pushButton_33.setObjectName(u"pushButton_33")

        self.gridLayout_3.addWidget(self.pushButton_33, 3, 3, 1, 1)

        self.btn_open = QPushButton(self.tab_1)
        self.btn_open.setObjectName(u"btn_open")

        self.gridLayout_3.addWidget(self.btn_open, 3, 1, 1, 1)

        self.label_14 = QLabel(self.tab_1)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_3.addWidget(self.label_14, 1, 2, 1, 1)

        self.label_15 = QLabel(self.tab_1)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_3.addWidget(self.label_15, 2, 0, 1, 1)

        self.label_16 = QLabel(self.tab_1)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_3.addWidget(self.label_16, 2, 2, 1, 1)

        self.label_12 = QLabel(self.tab_1)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_3.addWidget(self.label_12, 0, 0, 1, 4)


        self.verticalLayout_9.addLayout(self.gridLayout_3)

        self.tabWidget.addTab(self.tab_1, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_12 = QVBoxLayout(self.tab_3)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.pushButton_38 = QPushButton(self.tab_3)
        self.pushButton_38.setObjectName(u"pushButton_38")

        self.gridLayout_5.addWidget(self.pushButton_38, 4, 5, 1, 1)

        self.pushButton_34 = QPushButton(self.tab_3)
        self.pushButton_34.setObjectName(u"pushButton_34")

        self.gridLayout_5.addWidget(self.pushButton_34, 4, 0, 1, 1)

        self.pushButton_37 = QPushButton(self.tab_3)
        self.pushButton_37.setObjectName(u"pushButton_37")

        self.gridLayout_5.addWidget(self.pushButton_37, 4, 3, 1, 1)

        self.pushButton_35 = QPushButton(self.tab_3)
        self.pushButton_35.setObjectName(u"pushButton_35")

        self.gridLayout_5.addWidget(self.pushButton_35, 4, 1, 1, 1)

        self.pushButton_36 = QPushButton(self.tab_3)
        self.pushButton_36.setObjectName(u"pushButton_36")

        self.gridLayout_5.addWidget(self.pushButton_36, 4, 2, 1, 1)

        self.pushButton_39 = QPushButton(self.tab_3)
        self.pushButton_39.setObjectName(u"pushButton_39")

        self.gridLayout_5.addWidget(self.pushButton_39, 4, 4, 1, 1)

        self.label_17 = QLabel(self.tab_3)
        self.label_17.setObjectName(u"label_17")
        self.label_17.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_5.addWidget(self.label_17, 0, 0, 1, 6)

        self.label_19 = QLabel(self.tab_3)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout_5.addWidget(self.label_19, 6, 0, 1, 1)

        self.spinBox_3 = QSpinBox(self.tab_3)
        self.spinBox_3.setObjectName(u"spinBox_3")

        self.gridLayout_5.addWidget(self.spinBox_3, 6, 1, 1, 1)

        self.label_20 = QLabel(self.tab_3)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_5.addWidget(self.label_20, 6, 2, 1, 1)

        self.label_21 = QLabel(self.tab_3)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout_5.addWidget(self.label_21, 6, 4, 1, 1)

        self.comboBox_5 = QComboBox(self.tab_3)
        self.comboBox_5.setObjectName(u"comboBox_5")

        self.gridLayout_5.addWidget(self.comboBox_5, 6, 3, 1, 1)

        self.comboBox_6 = QComboBox(self.tab_3)
        self.comboBox_6.setObjectName(u"comboBox_6")

        self.gridLayout_5.addWidget(self.comboBox_6, 6, 5, 1, 1)

        self.label_18 = QLabel(self.tab_3)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_5.addWidget(self.label_18, 5, 0, 1, 6)


        self.verticalLayout_12.addLayout(self.gridLayout_5)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_22 = QLabel(self.tab_3)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setTextFormat(Qt.TextFormat.MarkdownText)

        self.verticalLayout_13.addWidget(self.label_22)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.pushButton_42 = QPushButton(self.tab_3)
        self.pushButton_42.setObjectName(u"pushButton_42")

        self.horizontalLayout_4.addWidget(self.pushButton_42)

        self.pushButton_43 = QPushButton(self.tab_3)
        self.pushButton_43.setObjectName(u"pushButton_43")

        self.horizontalLayout_4.addWidget(self.pushButton_43)

        self.pushButton_44 = QPushButton(self.tab_3)
        self.pushButton_44.setObjectName(u"pushButton_44")

        self.horizontalLayout_4.addWidget(self.pushButton_44)

        self.pushButton_41 = QPushButton(self.tab_3)
        self.pushButton_41.setObjectName(u"pushButton_41")

        self.horizontalLayout_4.addWidget(self.pushButton_41)

        self.pushButton_40 = QPushButton(self.tab_3)
        self.pushButton_40.setObjectName(u"pushButton_40")

        self.horizontalLayout_4.addWidget(self.pushButton_40)


        self.verticalLayout_13.addLayout(self.horizontalLayout_4)


        self.verticalLayout_12.addLayout(self.verticalLayout_13)

        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_23 = QLabel(self.tab_3)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setTextFormat(Qt.TextFormat.MarkdownText)

        self.gridLayout_6.addWidget(self.label_23, 0, 0, 1, 1)


        self.verticalLayout_12.addLayout(self.gridLayout_6)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.label_24 = QLabel(self.tab_3)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setTextFormat(Qt.TextFormat.MarkdownText)

        self.verticalLayout_11.addWidget(self.label_24)


        self.verticalLayout_12.addLayout(self.verticalLayout_11)

        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.tabWidget.addTab(self.tab_5, "")

        self.verticalLayout_2.addWidget(self.tabWidget)


        self.horizontalLayout_2.addWidget(self.control_panel)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        Main.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(Main)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1301, 23))
        Main.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(Main)
        self.statusbar.setObjectName(u"statusbar")
        Main.setStatusBar(self.statusbar)

        self.retranslateUi(Main)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Main)
    # setupUi

    def retranslateUi(self, Main):
        Main.setWindowTitle(QCoreApplication.translate("Main", u"FisioAccess v2015", None))
        self.pushButton.setText("")
        self.pushButton_2.setText("")
        self.pushButton_3.setText(QCoreApplication.translate("Main", u"O", None))
        self.pushButton_9.setText("")
        self.pushButton_7.setText("")
        self.pushButton_8.setText("")
        self.pushButton_13.setText(QCoreApplication.translate("Main", u".", None))
        self.pushButton_10.setText(QCoreApplication.translate("Main", u".-", None))
        self.pushButton_11.setText(QCoreApplication.translate("Main", u"dots", None))
        self.pushButton_12.setText(QCoreApplication.translate("Main", u"filter", None))
        self.pushButton_14.setText("")
        self.pushButton_15.setText("")
        self.pushButton_16.setText("")
        self.groupBox_7.setTitle(QCoreApplication.translate("Main", u"Puebas", None))
        self.btn_test_ecg.setText(QCoreApplication.translate("Main", u"ECG", None))
        self.btn_test_eeg.setText(QCoreApplication.translate("Main", u"EEG", None))
        self.btn_test_emg.setText(QCoreApplication.translate("Main", u"EMG", None))
        self.btn_test_spiro.setText(QCoreApplication.translate("Main", u"Espirometr\u00eda", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("Main", u"Herramientas", None))
        self.label_7.setText(QCoreApplication.translate("Main", u"## Panel de Control", None))
        self.btn_connect.setText(QCoreApplication.translate("Main", u"Configurar", None))
        self.label.setText(QCoreApplication.translate("Main", u"### Dispositivos Seriales", None))
        self.pushButton_23.setText(QCoreApplication.translate("Main", u"Buscar Dispositivos", None))
        self.label_5.setText(QCoreApplication.translate("Main", u"Duraci\u00f3n (seg):", None))
        self.label_3.setText(QCoreApplication.translate("Main", u"Amplitud (mV):", None))
        self.label_4.setText(QCoreApplication.translate("Main", u"Calibraci\u00f3n:", None))
        self.label_6.setText(QCoreApplication.translate("Main", u"Fmuestreo (Hz):", None))
        self.btn_reset.setText(QCoreApplication.translate("Main", u"Reset", None))
        self.pushButton_25.setText(QCoreApplication.translate("Main", u"Auto", None))
        self.pushButton_26.setText(QCoreApplication.translate("Main", u"Manual", None))
        self.checkBox.setText(QCoreApplication.translate("Main", u"Continua", None))
        self.label_2.setText(QCoreApplication.translate("Main", u"### Configuraci\u00f3n de Adquisici\u00f3n", None))
        self.pushButton_29.setText(QCoreApplication.translate("Main", u"Pausar", None))
        self.btn_start.setText(QCoreApplication.translate("Main", u"Iniciar", None))
        #self.btn_clear.setText(QCoreApplication.translate("Main", u"Detener", None))
        self.label_9.setText(QCoreApplication.translate("Main", u"Tiempo :", None))
        self.label_10.setText(QCoreApplication.translate("Main", u"00:00:00", None))
        self.label_11.setText(QCoreApplication.translate("Main", u"Estado: Detenicdo", None))
        self.label_8.setText(QCoreApplication.translate("Main", u"### control de Adquisici\u00f3n", None))
        self.pushButton_32.setText(QCoreApplication.translate("Main", u"Exportar", None))
        self.label_13.setText(QCoreApplication.translate("Main", u"ID Usuario :", None))
        self.btn_save.setText(QCoreApplication.translate("Main", u"Guardar", None))
        self.pushButton_33.setText(QCoreApplication.translate("Main", u"Imprimir", None))
        self.btn_open.setText(QCoreApplication.translate("Main", u"Cargar", None))
        self.label_14.setText(QCoreApplication.translate("Main", u"Sesi\u00f3n :", None))
        self.label_15.setText(QCoreApplication.translate("Main", u"Formato :", None))
        self.label_16.setText(QCoreApplication.translate("Main", u"Compresi\u00f3n :", None))
        self.label_12.setText(QCoreApplication.translate("Main", u"### Gesti\u00f3n de Datos", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), QCoreApplication.translate("Main", u"Adquisici\u00f3n", None))
        self.pushButton_38.setText(QCoreApplication.translate("Main", u"Anotaci\u00f3n", None))
        self.pushButton_34.setText(QCoreApplication.translate("Main", u"Cursor", None))
        self.pushButton_37.setText(QCoreApplication.translate("Main", u"Zoom", None))
        self.pushButton_35.setText(QCoreApplication.translate("Main", u"Marcador", None))
        self.pushButton_36.setText(QCoreApplication.translate("Main", u"Medici\u00f3n", None))
        self.pushButton_39.setText(QCoreApplication.translate("Main", u"Regi\u00f3n", None))
        self.label_17.setText(QCoreApplication.translate("Main", u"### Herramientas de An\u00e1lisis", None))
        self.label_19.setText(QCoreApplication.translate("Main", u"Grosor:", None))
        self.label_20.setText(QCoreApplication.translate("Main", u"Color:", None))
        self.label_21.setText(QCoreApplication.translate("Main", u"Modo:", None))
        self.label_18.setText(QCoreApplication.translate("Main", u"Propiedades:", None))
        self.label_22.setText(QCoreApplication.translate("Main", u"### Marcadores y Eventos", None))
        self.pushButton_42.setText(QCoreApplication.translate("Main", u"Nuevo", None))
        self.pushButton_43.setText(QCoreApplication.translate("Main", u"Editar", None))
        self.pushButton_44.setText(QCoreApplication.translate("Main", u"Eliminar", None))
        self.pushButton_41.setText(QCoreApplication.translate("Main", u"Ir a", None))
        self.pushButton_40.setText(QCoreApplication.translate("Main", u"Exportar", None))
        self.label_23.setText(QCoreApplication.translate("Main", u"### An\u00e1lisis Autom\u00e1tico", None))
        self.label_24.setText(QCoreApplication.translate("Main", u"### Estad\u00edsticas y Resultados", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("Main", u"An\u00e1lisis", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), QCoreApplication.translate("Main", u"Filtros", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), QCoreApplication.translate("Main", u"Informes", None))
    # retranslateUi

