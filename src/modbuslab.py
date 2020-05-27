# -*- coding: utf-8 -*-
from PyQt4 import QtGui
from Intefaz import ApplicationWindow
 
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = ApplicationWindow()
    ui.show()
    sys.exit(app.exec_())
