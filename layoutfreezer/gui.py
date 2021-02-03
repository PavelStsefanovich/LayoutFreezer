import logging
from PySide2.QtWidgets import QApplication, QMessageBox
import sys


##########  Global Properties  ####################

logger = logging.getLogger(__name__)


##########  Functions  ############################

def show_critical_error_dialog(errormessage="Critical error occured (no details provided)"):
    app = QApplication(sys.argv)
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText(errormessage)
    msgBox.show()
    app.exec_()


##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
