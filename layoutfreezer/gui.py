from .db import Database
import json
import logging
from PySide2 import QtGui
from PySide2 import QtWidgets
from os import path, makedirs
import sys


##########  Global Properties  ####################

logger = logging.getLogger(__name__)


##########  Functions  ############################

def show_critical_error_dialog(
    errormessage="Critical error occured (no details provided)"):

    app = QtWidgets.QApplication(sys.argv)
    msgBox = QtWidgets.QMessageBox()
    msgBox.setIcon(QtWidgets.QMessageBox.Critical)
    msgBox.setText(errormessage)
    msgBox.show()
    sys.exit(app.exec_())


##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
