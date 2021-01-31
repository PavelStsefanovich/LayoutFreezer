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

# def scr_get_display_index(screens, win_rectangle):

#     for scr_index in range(0, len(screens)):
#         scr_rectangle = screens[scr_index]['rectangle']

#         if win_rectangle[0] < scr_rectangle[0] or win_rectangle[0] > scr_rectangle[2]:
#             continue

#         if win_rectangle[1] < scr_rectangle[1] or win_rectangle[1] > scr_rectangle[3]:
#             continue

#         return scr_index

#     return -1


# def scr_get_num_of_windows_for_proc(app_configs, proc_name):
#     occurencies = 0

#     if isinstance(app_configs, list):
#         for i in range(0, len(app_configs)):
#             if app_configs[i][2] == proc_name:
#                 occurencies += 1

#     if isinstance(app_configs, dict):
#         for key in app_configs:
#             if app_configs[key]['process_name'] == proc_name:
#                 occurencies += 1

#     logger.debug(f'Found {occurencies} configuration(s) for process "{proc_name}" in the following data set:')
#     logger.debug(app_configs)
#     return occurencies

# def load_preferences_from_file(preferences_path):
#     prefs = {}

#     if path.exists(preferences_path):
#         with open(preferences_path, 'r') as file:
#             prefs = json.load(file)


#     return prefs


# def db_update_app_config(db, display_layout, window_config):
#     layout_app_configs = db.search(name=window_config['process_name'])

#     for conf in layout_app_configs:
#         logger.info(f'Found config for process \'{window_config["process_name"]}\': {conf}')


##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
