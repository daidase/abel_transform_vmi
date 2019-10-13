import sys
from pBaseQT import pBaseForm
from PySide2 import QtCore
from PySide2.QtWidgets import QMainWindow,QApplication

QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

class MainWindow(QMainWindow):
  def __init__(self, parent=None):
    QMainWindow.__init__(self,parent)
    self.ui =  pBaseForm()
    self.ui.setupUi(self)

if __name__ == "__main__":
    app=QApplication(sys.argv)
    pBase = MainWindow()
    pBase.show()
    sys.exit(app.exec_())