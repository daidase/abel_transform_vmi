# -*- coding: utf-8 -*-
# Created: Mon Sep 30 10:02:05 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# GUI interface for pBase program with a Qt interface
# Use some of the function build in pBaseCore 
# Use  matplotlib for displaying images

import os
from PySide2 import QtCore, QtWidgets, QtGui
import matplotlib

matplotlib.use('Qt4Agg')
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigCanvas
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import matplotlib.colors as colors
from matplotlib.ticker import NullFormatter

from pBaseCore import Datas, theta_f

waitCondition = QtCore.QWaitCondition()
mutex = QtCore.QMutex()


class PlotSettings():
    def __init__(self):
        self.palette = cm.jet.name
        self.IsSqrt = False
        self.IsFixed = False


class pBaseForm(QtWidgets.QMainWindow):
    def setupUi(self, MainWindow):
        # Define datas
        self.plotsettings = PlotSettings()
        self.workflow = Datas()
        self.file_path = ''
        self.file_name = ''
        # Create Main Window
        MainWindow.setObjectName("MainWindow")

        # Fit Main window with a Widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create the frame for the graph and add it to the main layout
        self.Wplot = QtWidgets.QWidget()
        self.LPlot = QtWidgets.QVBoxLayout()
        self.LPlot.setContentsMargins(5, 5, 5, 5)
        self.fig = Figure((6., 6.), dpi=150)
        self.canvas = FigCanvas(self.fig)
        self.canvas.setParent(self.Wplot)
        gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
        gs.update(hspace=0.05)
        self.axes = self.fig.add_subplot(gs[0])
        self.axesPES = self.fig.add_subplot(gs[1])
        gs.tight_layout(self.fig, pad=0.1)
        self.Wplot.setObjectName("Image")
        self.LPlot.addWidget(self.canvas)
        self.Wplot.setLayout(self.LPlot)
        # Bind the 'pick' event for clicking on one of the bars
        self.canvas.mpl_connect('button_press_event', self.on_press)

        # Create the Tool Box on the side
        self.VerticalWidget = QtWidgets.QWidget()
        self.VerticalBox = QtWidgets.QVBoxLayout()
        self.VerticalBox.setContentsMargins(5, 5, 5, 5)
        self.VerticalBox.setObjectName("verticalLayout")
        # Design the external Group box
        self.groupBox = QtWidgets.QGroupBox(self.VerticalWidget)
        self.groupBox.setObjectName("ToolBox")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setObjectName("verticalLayout")

        # Design the polynom group box
        self.PolyGBox = QtWidgets.QGroupBox()
        self.PolyGBox.setFlat(True)
        self.PolyGBox.setObjectName("PolynomeGBox")
        self.PolyLayout = QtWidgets.QHBoxLayout(self.PolyGBox)
        self.PolyLayout.setSpacing(5)
        self.PolyLayout.setContentsMargins(5, 5, 5, 5)
        self.PolyLayout.setObjectName("PolynomeBoxLayout")
        self.label = QtWidgets.QLabel(self.PolyGBox)
        self.label.setObjectName("label")
        self.PolyLayout.addWidget(self.label)
        self.PolyBox = QtWidgets.QSpinBox(self.PolyGBox)
        self.PolyBox.setWrapping(False)
        self.PolyBox.setFrame(True)
        self.PolyBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.PolyBox.setSpecialValueText("")
        self.PolyBox.setAccelerated(False)
        self.PolyBox.setSuffix("")
        self.PolyBox.setMinimum(0)
        self.PolyBox.setMaximum(100)
        self.PolyBox.setProperty("value", 2)
        self.PolyBox.setObjectName("PolyBox")
        self.PolyBox.valueChanged.connect(self.ChangeLmax)
        self.PolyLayout.addWidget(self.PolyBox)
        self.PolyLayout.insertSpacing(2, 15)

        self.OddBox = QtWidgets.QCheckBox(self.PolyGBox)
        self.OddBox.setObjectName("OddBox")
        self.OddBox.stateChanged.connect(self.ChangeOdd)
        self.PolyLayout.addWidget(self.OddBox)
        self.PolyGBox.setLayout(self.PolyLayout)
        self.verticalLayout.addWidget(self.PolyGBox)

        self.DataChoiceGBox = QtWidgets.QGroupBox()
        self.DataChoiceGBox.setFlat(True)
        self.DataChoiceGBox.setObjectName("DataChoiceBox")
        self.DCLayout = QtWidgets.QHBoxLayout(self.DataChoiceGBox)
        self.DCLayout.setContentsMargins(5, 5, 5, 5)
        self.DCLayout.setObjectName("DataChoiceLayout")
        self.label2 = QtWidgets.QLabel(self.DataChoiceGBox)
        self.label2.setObjectName("label2")
        self.DCLayout.addWidget(self.label2)
        self.DataChoiceBox = QtWidgets.QComboBox(self.DataChoiceGBox)
        self.DataChoiceBox.setObjectName("DataChoiceBox")
        self.DataChoiceBox.addItem("")
        self.DataChoiceBox.addItem("")
        self.DCLayout.addWidget(self.DataChoiceBox)
        self.DCLayout.insertSpacing(2, 15)
        self.DataChoiceGBox.setLayout(self.DCLayout)
        self.verticalLayout.addWidget(self.DataChoiceGBox)

        # Define the Centering Tool Box
        self.CenterBox = QtWidgets.QGroupBox(self.groupBox)
        self.CenterBox.setFlat(True)
        self.CenterBox.setObjectName("CenterBox")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setVerticalSpacing(8)
        self.gridLayout.setHorizontalSpacing(8)
        self.gridLayout.setObjectName("CenterBoxLayout")
        self.XSlider = QtWidgets.QSlider(self.CenterBox)
        self.XSlider.setOrientation(QtCore.Qt.Horizontal)
        self.XSlider.setPageStep(1)
        self.XSlider.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.XSlider.valueChanged[int].connect(self.changeXValue)
        self.XSlider.setObjectName("XSlider")
        self.gridLayout.addWidget(self.XSlider, 0, 1, 1, 1)
        self.YSlider = QtWidgets.QSlider(self.CenterBox)
        self.YSlider.setOrientation(QtCore.Qt.Horizontal)
        self.YSlider.setPageStep(1)
        self.YSlider.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.YSlider.valueChanged[int].connect(self.changeYValue)
        self.YSlider.setObjectName("YSlider")
        self.gridLayout.addWidget(self.YSlider, 1, 1, 1, 1)
        self.TransposeButton = QtWidgets.QPushButton(self.CenterBox)
        # self.TransposeButton.setStyleSheet("QPushButton {background: rgb(127,179,255);border-style:outset;border-width=2px;border-radius}")
        self.TransposeButton.setObjectName("TransposeButton")
        self.TransposeButton.clicked.connect(self.TransposeFn)
        self.gridLayout.addWidget(self.TransposeButton, 2, 0, 1, 1)

        self.FixCenterBox = QtWidgets.QCheckBox(self.CenterBox)
        self.FixCenterBox.stateChanged.connect(self.ChangeFixCenter)
        self.FixCenterBox.setObjectName("FixCenterBox")
        self.gridLayout.addWidget(self.FixCenterBox, 2, 1, 1, 1)
        self.AutoButton = QtWidgets.QPushButton(self.CenterBox)
        self.AutoButton.setFlat(False)
        self.AutoButton.clicked.connect(self.AutoCenterFn)
        self.AutoButton.setObjectName("AutoButton")
        self.gridLayout.addWidget(self.AutoButton, 0, 0, 1, 1)
        self.SymButton = QtWidgets.QPushButton(self.CenterBox)
        self.SymButton.setObjectName("SymButton")
        self.SymButton.clicked.connect(self.SymmetrizeFn)
        self.gridLayout.addWidget(self.SymButton, 1, 0, 1, 1)
        self.ImageCenterBtn = QtWidgets.QPushButton(self.CenterBox)
        self.ImageCenterBtn.setObjectName("ImageCenterBtn")
        self.ImageCenterBtn.clicked.connect(self.ICenterFn)
        self.gridLayout.addWidget(self.ImageCenterBtn, 3, 0, 1, 1)
        self.gridLayout.setColumnStretch(0, 3)
        self.gridLayout.setColumnStretch(1, 4)
        self.CenterBox.setLayout(self.gridLayout)
        self.verticalLayout.addWidget(self.CenterBox)

        # Define the plot toolbox
        self.ColorBox = QtWidgets.QGroupBox(self.groupBox)
        self.ColorBox.setFlat(True)
        self.ColorBox.setCheckable(False)
        self.ColorBox.setObjectName("ColorBox")
        self.ColorLayout = QtWidgets.QHBoxLayout()
        self.ColorLayout.setContentsMargins(5, 5, 5, 5)
        self.ColorLayout.setObjectName("ColorLayout")
        self.ColorMapBox = QtWidgets.QComboBox(self.ColorBox)
        self.ColorMapBox.setObjectName("ColorMapBox")
        self.ColorMapBox.addItem("")
        self.ColorMapBox.addItem("")
        self.ColorMapBox.addItem("")
        self.ColorMapBox.addItem("")
        self.ColorMapBox.addItem("")
        self.ColorMapBox.addItem("")
        self.ColorMapBox.addItem("")
        self.ColorMapBox.activated[str].connect(self.OnChooseCM)
        self.ColorLayout.addWidget(self.ColorMapBox)
        self.InvColorBox = QtWidgets.QCheckBox(self.ColorBox)
        self.InvColorBox.setObjectName("InvColorBox")
        self.InvColorBox.stateChanged.connect(self.InvertCM)
        self.ColorLayout.addWidget(self.InvColorBox)
        self.SqrtColorBox = QtWidgets.QCheckBox(self.ColorBox)
        self.SqrtColorBox.setObjectName("SqrtColorBox")
        self.SqrtColorBox.stateChanged.connect(self.SqrtCM)
        self.ColorLayout.addWidget(self.SqrtColorBox)
        self.ColorLayout.setStretch(0, 3)
        self.ColorLayout.setStretch(1, 2)
        self.ColorLayout.setStretch(2, 1)
        self.ColorBox.setLayout(self.ColorLayout)
        self.verticalLayout.addWidget(self.ColorBox)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1.5)
        self.verticalLayout.setStretch(3, 1)

        # Define the Main Tool Box: Invert|Save|Close buttons
        self.HBox = QtWidgets.QHBoxLayout()
        self.HBox.setContentsMargins(2, 2, 2, 2)
        self.HBox.setObjectName("HBox")
        self.InvertButton = QtWidgets.QPushButton(self.groupBox)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setStrikeOut(False)
        font.setBold(True)
        self.InvertButton.setFont(font)
        self.InvertButton.setObjectName("InvertButton")
        self.InvertButton.clicked.connect(self.InvertFn)
        self.HBox.addWidget(self.InvertButton)
        self.SaveButton = QtWidgets.QPushButton(self.groupBox)
        self.SaveButton.setObjectName("SaveButton")
        self.SaveButton.clicked.connect(self.openSave)
        self.HBox.addWidget(self.SaveButton)
        self.CloseButton = QtWidgets.QPushButton(self.groupBox)
        self.CloseButton.setObjectName("CloseButton")
        self.HBox.addWidget(self.CloseButton)

        # Add the layout to the central widget and then to the window
        self.VerticalBox.addWidget(self.groupBox)
        self.VerticalBox.addLayout(self.HBox)
        self.VerticalWidget.setLayout(self.VerticalBox)

        # Design the main Layout Frame | Control box: Horizontal
        self.MLayout = QtWidgets.QHBoxLayout()
        self.MLayout.setSpacing(5)
        self.MLayout.setContentsMargins(5, 5, 5, 5)
        self.MLayout.setObjectName("HorizontalBox")
        self.MLayout.addWidget(self.Wplot)
        self.MLayout.addWidget(self.VerticalWidget)
        self.MLayout.setAlignment(self.Wplot, QtCore.Qt.AlignCenter)

        # Define the Main window menu bar and statusbar
        self.menubar = QtWidgets.QMenuBar()
        self.menubar.setGeometry(QtCore.QRect(0, 0, 830, 22))
        self.menubar.setObjectName("menubar")
        self.menuFiles = QtWidgets.QMenu(self.menubar)
        self.menuFiles.setObjectName("menuFiles")
        MainWindow.setMenuBar(self.menubar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.setStatusTip("Open new File")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave.setStatusTip("Save current Analyse")
        self.menuFiles.addAction(self.actionOpen)
        self.menuFiles.addAction(self.actionSave)
        self.menubar.addAction(self.menuFiles.menuAction())
        # Status bar
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.statlabel = QtWidgets.QLabel()
        self.statlabel.setText("Ready !")
        self.statusbar.addWidget(self.statlabel, 1)
        self.statcoordinates = QtWidgets.QLabel()
        self.statcoordinates.setText("Center: x= , y= ")
        self.statusbar.addWidget(self.statcoordinates, 2)
        self.progressBar = QtWidgets.QProgressBar()
        self.statusbar.addWidget(self.progressBar, 2)
        self.progressBar.setValue(0)
        self.progressBar.setRange(0, 20)
        self.progressBar.setVisible(False)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.CloseButton, QtCore.SIGNAL("released()"), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave.triggered.connect(self.openSave)

        self.centralwidget.setLayout(self.MLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.display()

    def retranslateUi(self, MainWindow):
        # -1 = QtCore.QTextCodec.-1ForName("UTF-8")
        MainWindow.setWindowTitle(QtGui.QGuiApplication.translate("MainWindow", "pBaseQt", None, -1))
        self.groupBox.setTitle(QtGui.QGuiApplication.translate("MainWindow", "Treatments", None, -1))
        self.PolyGBox.setTitle(QtGui.QGuiApplication.translate("MainWindow", "Polynoms", None, -1))
        self.DataChoiceGBox.setTitle(
            QtGui.QGuiApplication.translate("MainWindow", "Choice of Data for the inversion", None, -1))
        self.label.setText(QtGui.QGuiApplication.translate("MainWindow", "Max Legendre Polynoms:", None, -1))
        self.label2.setText(QtGui.QGuiApplication.translate("MainWindow", "Datas to be inverted:", None, -1))
        self.OddBox.setText(QtGui.QGuiApplication.translate("MainWindow", "Odd", None, -1))
        self.DataChoiceBox.setItemText(0, QtGui.QGuiApplication.translate("MainWindow", "Original", None, -1))
        self.DataChoiceBox.setItemText(1, QtGui.QGuiApplication.translate("MainWindow", "Current", None, -1))
        self.CenterBox.setTitle(QtGui.QGuiApplication.translate("MainWindow", "Centering", None, -1))
        self.TransposeButton.setText(QtGui.QGuiApplication.translate("MainWindow", "Transpose", None, -1))
        self.FixCenterBox.setText(QtGui.QGuiApplication.translate("MainWindow", "Fixed Center", None, -1))
        self.AutoButton.setText(QtGui.QGuiApplication.translate("MainWindow", "Auto center", None, -1))
        self.SymButton.setText(QtGui.QGuiApplication.translate("MainWindow", "Symmetrize V", None, -1))
        self.ImageCenterBtn.setText(QtGui.QGuiApplication.translate("MainWindow", "Center of the image", None, -1))
        self.ColorBox.setTitle(QtGui.QGuiApplication.translate("MainWindow", "Colormaps", None, -1))
        self.ColorMapBox.setItemText(0, QtGui.QGuiApplication.translate("MainWindow", "Jet", None, -1))
        self.ColorMapBox.setItemText(1, QtGui.QGuiApplication.translate("MainWindow", "Gnuplot", None, -1))
        self.ColorMapBox.setItemText(2, QtGui.QGuiApplication.translate("MainWindow", "Gray", None, -1))
        self.ColorMapBox.setItemText(3, QtGui.QGuiApplication.translate("MainWindow", "Hot", None, -1))
        self.ColorMapBox.setItemText(4, QtGui.QGuiApplication.translate("MainWindow", "Rainbow", None, -1))
        self.ColorMapBox.setItemText(5, QtGui.QGuiApplication.translate("MainWindow", "Winter", None, -1))
        self.ColorMapBox.setItemText(6, QtGui.QGuiApplication.translate("MainWindow", "Terrain", None, -1))
        self.InvColorBox.setText(QtGui.QGuiApplication.translate("MainWindow", "Inverse Colors", None, -1))
        self.SqrtColorBox.setText(QtGui.QGuiApplication.translate("MainWindow", "Sqrt", None, -1))
        self.InvertButton.setText(QtGui.QGuiApplication.translate("MainWindow", "Invert !", None, -1))
        self.SaveButton.setText(QtGui.QGuiApplication.translate("MainWindow", "Save", None, -1))
        self.CloseButton.setText(QtGui.QGuiApplication.translate("MainWindow", "Close", None, -1))
        self.menuFiles.setTitle(QtGui.QGuiApplication.translate("MainWindow", "Files", None, -1))
        self.actionOpen.setText(QtGui.QGuiApplication.translate("MainWindow", "Open", None, -1))
        self.actionOpen.setShortcut(QtGui.QGuiApplication.translate("MainWindow", "Ctrl+O", None, -1))
        self.actionSave.setText(QtGui.QGuiApplication.translate("MainWindow", "Save", None, -1))
        self.actionSave.setShortcut(QtGui.QGuiApplication.translate("MainWindow", "Ctrl+S", None, -1))

    def openFile(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.tr("Open data file"), "~/", self.tr(
            "Fits Files (*.fits);;Image Files (*.tiff *.jpg *.bmp);;Txt (*.txt *.dat)"))
        if fname:
            file = QtCore.QFileInfo(fname)
            self.file_path = file.path()
            self.file_name = file.fileName()
            self.statlabel.setText("Opening File %s" % fname)
            self.workflow.OpenFile(fname)
            self.statlabel.setText("Go !")
        else:
            self.statlabel.setText("Failed to open File")
        self.display()

    def openSave(self):
        outputname = self.file_path[:-4] + '_output.fits'
        suggestedname = os.path.join(self.file_path, outputname)
        fname, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.tr("Save data file"), suggestedname,
                                                         self.tr("Fits Files (*.fits)"))
        if fname:
            self.statlabel.setText("Saving File %s" % fname)
            self.workflow.SaveFileFits(fname)

        else:
            self.statlabel.setText("Failed to save File")

    def display(self):
        """
            Deal with displaying the picture
        """
        self.axes.clear()
        self.axesPES.clear()
        # Deal with image
        xmax, ymax = self.workflow.datas.shape
        self.XSlider.setMaximum(xmax)
        self.YSlider.setMaximum(ymax)
        self.XSlider.setValue(self.workflow.center[0])
        self.YSlider.setValue(self.workflow.center[1])
        palette = cm.get_cmap(self.plotsettings.palette)
        if self.plotsettings.IsSqrt: palette = cmap_xmap(lambda x: x ** 2, palette)
        self.axes.imshow(self.workflow.datas, extent=[0, ymax, 0, xmax], origin='lower', cmap=palette,
                         vmax=0.8 * self.workflow.datas.max())

        if self.workflow.r != 0.:
            xc, yc = paint_circle(self.workflow.center, self.workflow.r)
            scalarMap = cm.ScalarMappable(norm=colors.Normalize(vmin=0, vmax=256), cmap=palette)
            self.axes.plot(xc, yc, color=scalarMap.to_rgba(256), lw=1)

        self.axes.axis([0, ymax, 0, xmax])
        # no label
        nullfmt = NullFormatter()
        self.axes.yaxis.set_major_formatter(nullfmt)
        self.axes.xaxis.set_major_formatter(nullfmt)
        self.axes.tick_params(bottom='off', top='off', left='off', right='off')
        # Deal with PES
        self.axesPES.plot(self.workflow.normed_pes, 'k')
        self.axesPES.set_yticks([0, 0.5, 1.])
        self.axesPES.set_xlim([0, self.workflow.r])
        # Deal with display
        self.canvas.draw()
        del palette
        self.statcoordinates.setText(
            u"Center: x={0[0]} , y={0[1]}.\t Radius: {1}".format(self.workflow.center, int(self.workflow.r)))

    def OnChooseCM(self, text):
        """
            Change cmap settings
        """
        if text == "Jet":
            Newpalette = cm.jet.name
        elif text == "Gnuplot":
            Newpalette = cm.gnuplot2.name
        elif text == "Gray":
            Newpalette = cm.gray.name
        elif text == "Hot":
            Newpalette = cm.hot.name
        elif text == "Terrain":
            Newpalette = cm.terrain.name
        elif text == "Rainbow":
            Newpalette = cm.rainbow.name
        elif text == "Winter":
            Newpalette = cm.winter.name
        else:
            Newpalette = cm.jet.name
        if self.plotsettings.palette.endswith("_r"): Newpalette = Newpalette + '_r'
        self.plotsettings.palette = Newpalette
        self.display()

    def InvertCM(self, state):
        """
            Inverse cmap scale
        """
        if state == QtCore.Qt.Checked:
            Newpalette = self.plotsettings.palette + '_r'
        else:
            Newpalette = self.plotsettings.palette[:-2]
        self.plotsettings.palette = Newpalette
        self.display()

    def SqrtCM(self, state):
        """
            Sqrt cmap scale
        """
        if state == QtCore.Qt.Checked:
            self.plotsettings.IsSqrt = True
        else:
            self.plotsettings.IsSqrt = False
            palette = cm.get_cmap(self.plotsettings.palette)
            palette = cmap_xmap(lambda x: np.sqrt(x), palette)
        self.display()

    def ChangeOdd(self, state):
        if state == QtCore.Qt.Checked:
            self.workflow.odd = 1
        else:
            self.workflow.odd = 0

    def ChangeLmax(self, number):
        self.workflow.lmax = number

    def ChangeFixCenter(self, state):
        """
    		If pressed, if fixes the centre of the image to the most recent value and
    		prevents the user from changing it by clicking the mouse on the image window.
    		It also forces the panel to give the distance from the centre instead of the
    		cartesian coordinates.
    	"""
        if state == QtCore.Qt.Checked:
            self.plotsettings.IsFixed = True
        else:
            self.plotsettings.IsFixed = False

    def TransposeFn(self):
        self.workflow.datas = self.workflow.datas.T
        self.workflow.center = (self.workflow.center[1], self.workflow.center[0])
        self.statlabel.setText("Transposed")
        self.display()

    def SymmetrizeFn(self):
        """
    		Symmetrise a 2_D circular selection vertically (ie about a horizontal axis).
    		Assume that the centre is mid-pixel (x0,y0) rather than at lower left corner
    		of pixel x0,y0. Note that no symmetrisation is needed
    		horizontally since the Legendre polynomials are already
    		symmetric along the vertical axis. (Vertically being the polarisation
    		axis of the ligth, or the direction of propagation in the case of cpl).
    	"""
        self.workflow.Symmetrize(self.workflow.datas)
        self.statlabel.setText("Symmetrized")
        self.display()

    def AutoCenterFn(self):
        if self.workflow.r == 0.:
            self.display()
        else:
            self.progressBar.reset()
            self.progressBar.setVisible(True)
            if not self.plotsettings.IsFixed:
                self.statlabel.setText("Centering")
                self.RunProcess()
                while not self.process.isFinished(): QtCore.QCoreApplication.processEvents()
            self.statlabel.setText("Centered")
            self.progressBar.setVisible(False)
            self.display()

    def RunProcess(self):
        self.process = CenterProcesser(self)
        QtCore.QObject.connect(self.process, QtCore.SIGNAL("progress(int)"), self.progressBar,
                               QtCore.SLOT("setValue(int)"))
        if not self.process.isRunning():
            self.process.exiting = False
            self.process.start()

    def ICenterFn(self):
        if not self.plotsettings.IsFixed: self.workflow.get_com()
        self.display()

    def InvertFn(self):
        # Path to the basis file
        dpath = QtWidgets.QFileDialog.getExistingDirectory(self, self.tr("Basis Files Directory"), dir="~/")
        self.progressBar.reset()
        self.progressBar.setVisible(True)
        self.process = InvertProcesser(self, dpath)
        QtCore.QObject.connect(self.process, QtCore.SIGNAL("progress(int)"), self.progressBar,
                               QtCore.SLOT("setValue(int)"))
        if not self.process.isRunning():
            self.process.exiting = False
            self.process.start()
        while not self.process.isFinished(): QtCore.QCoreApplication.processEvents()
        self.progressBar.setVisible(False)

        self.workflow.datas = self.workflow.output
        self.display()

    def changeXValue(self, value):
        if not self.plotsettings.IsFixed: self.workflow.center = (value, self.workflow.center[1])
        self.display()

    def changeYValue(self, value):
        if not self.plotsettings.IsFixed: self.workflow.center = (self.workflow.center[0], value)
        self.display()

    def on_press(self, event):
        if event.inaxes and not self.plotsettings.IsFixed:
            self.workflow.center = (event.xdata, event.ydata)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def on_release(self, event):
        if event.inaxes:
            x = event.xdata
            y = event.ydata
            self.workflow.r = np.sqrt((x - self.workflow.center[0]) ** 2 + (y - self.workflow.center[1]) ** 2)
            self.display()


def cmap_xmap(function, cmap):
    """ Applies function, on the indices of colormap cmap. Beware, function
    should map the [0, 1] segment to itself, or you are in for surprises.
    """
    cdict = cmap._segmentdata
    function_to_map = lambda x: (function(x[0]), x[1], x[2])
    for key in ('red', 'green', 'blue'):
        cdict[key] = map(function_to_map, cdict[key])
        cdict[key].sort()
        assert (cdict[key][0] < 0 or cdict[key][-1] > 1), "Resulting indices extend out of the [0, 1] segment."
    return colors.LinearSegmentedColormap('colormap', cdict, 1024)


def paint_circle(center, radius):
    theta = np.linspace(-np.pi, np.pi, 1001)
    return center[0] + radius * np.cos(theta), center[1] + radius * np.sin(theta)


class CenterProcesser(QtCore.QThread):
    __errorHappened = False

    def __init__(self, gui, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.workflow = gui.workflow
        self.gui = gui
        self.exiting = False

    def run(self):
        Cmax = 0
        center, Cn = self.workflow.Newcenter(10)
        for i in np.arange(20):
            if Cn > Cmax:
                self.workflow.center = center
                self.gui.display()
                self.emit(QtCore.SIGNAL("progress(int)"), i)
                Cmax = Cn
                center, Cn = self.workflow.Newcenter(10)
            else:
                self.emit(QtCore.SIGNAL("progress(int)"), 20)
                break


class InvertProcesser(QtCore.QThread):
    __errorHappened = False

    def __init__(self, gui, path, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.workflow = gui.workflow
        self.gui = gui
        self.exiting = False
        self.path = path

    def run(self):
        self.gui.statlabel.setText("Start the inversion procedure")
        base = self.workflow.LoadBasis(self.path)
        if len(base.shape) < 2:
            QtWidgets.QMessageBox.warning(self, "No Basis",
                                          "Basis file don't exist yet !!! \n Please build it first. :(")
            return 0
        self.gui.statlabel.setText("Basis Loaded")
        self.emit(QtCore.SIGNAL("progress(int)"), 5)

        if self.gui.DataChoiceBox.currentText() == "Original":
            self.gui.statlabel.setText("Original")
            polar = self.workflow.to_polar(self.workflow.raw)
        else:
            self.gui.statlabel.setText("Current")
            polar = self.workflow.to_polar(self.workflow.datas)

        self.gui.statlabel.setText("Polar Image")
        self.emit(QtCore.SIGNAL("progress(int)"), 10)

        self.workflow.Invert(polar, base)
        self.gui.statlabel.setText("Fitted")
        self.emit(QtCore.SIGNAL("progress(int)"), 15)
        del polar, base

        self.workflow.image_for_display()
        self.gui.statlabel.setText("Image inverted")
        self.emit(QtCore.SIGNAL("progress(int)"), 20)
