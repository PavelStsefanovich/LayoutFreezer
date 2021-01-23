import json
import logging
import sys

from .db import Database
from PySide2 import QtGui
from PySide2 import QtWidgets
from os import path, makedirs


##########  Module Properties  ####################

logger = logging.getLogger(__name__)

# Determine Operating System
#(ps) currently windows only
#current_os = get_os()
current_os = 'windows'

# load os-specific module for screen/windows operations
if current_os == 'windows':
    from .os_screen import windows as osscreen


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


def db_enum_apps_for_curr_layout(db, dl_hash, simplify=True):
    layout_app_configs = db.search(dl_hash=dl_hash, order_by='process_name')

    if simplify:
        results = []
        for item in layout_app_configs:
            results.append(item[2:-1])

    else:
        results = layout_app_configs

    if results:
        logger.debug(f'Found app configurations in database for layout {dl_hash}')
        logger.debug(f'app_configs: {results}')

    else:
        logger.debug(f'No app configurations found in database for layout {dl_hash}')

    return results


def db_add_app_config(db, display_layout_hash, window_config):
    process_name = window_config[0]
    title = window_config[1]
    rect = str(window_config[2])
    display_index = window_config[3]
    display_orientation = window_config[4]

    logger.debug(f'Adding:')
    logger.debug(f' - process_name: {process_name}')
    logger.debug(f' - window_title: {title}')
    logger.debug(f' - window_rectangle: {rect}')
    logger.debug(f' - display_index: {display_index}')
    logger.debug(f' - display_orientation: {display_orientation}')

    db.add( display_layout_hash,
            process_name,
            title,
            rect,
            display_index,
            display_orientation)


def simplify_app_config(app_config):
    result = (app_config['process_name'],
              app_config['window_title'],
              str(app_config['window_rectangle']),
              app_config['display_index'],
              app_config['display_orientation'])

    return result
    

def extract_process_names(layout_app_configs):
    apps = []

    for app_config in layout_app_configs:
        apps.append(app_config[0])

    return apps


def load_preferences_from_file(preferences_path):
    prefs = {}
    
    if path.exists(preferences_path):
        with open(preferences_path, 'r') as file:
            prefs = json.load(file)

    
    return prefs


# def db_update_app_config(db, display_layout, window_config):
#     layout_app_configs = db.search(name=window_config['process_name'])

#     for conf in layout_app_configs:
#         logger.info(f'Found config for process \'{window_config["process_name"]}\': {conf}')



##########  Classes  ##############################

class SystemTrayApp():

    def __init__(self, iconpath, tooltip='SystemTrayApp', database_path='database', preferences_path='preferences.json'):
        # Initiate database connection
        database_path = database_path.replace('~',path.expanduser('~'))
        database_path = path.abspath(database_path)
        logger.debug(f'Database path: {database_path}')
        makedirs(path.split(database_path)[0], exist_ok=True)
        self.db = Database(database_path)

        # Set preferences file path
        self.preferences_path = path.abspath(preferences_path)

        # Init QApplication, QWidet and QMenu
        self.app = QtWidgets.QApplication([])
        self.widget = QtWidgets.QWidget()
        self.menu = QtWidgets.QMenu(self.widget)

        # Add items to menu
        self.menu_action_raise = self.menu.addAction("Restore Layout")
        self.menu_action_raise.triggered.connect(self.restore_layout)

        self.menu_action_raise = self.menu.addAction("Freeze Layout")
        self.menu_action_raise.triggered.connect(self.freeze_layout)

        self.menu_action_raise = self.menu.addSeparator()

        self.menu_action_raise = self.menu.addAction("Preferences")
        self.menu_action_raise.triggered.connect(self.open_preferences)

        self.menu_action_raise = self.menu.addSeparator()

        self.menu_action_exit = self.menu.addAction("Exit")
        self.menu_action_exit.triggered.connect(self.app.exit)

        # Create app icon
        iconpath = path.abspath(iconpath)
        logger.debug(f'SystemTray icon path: {iconpath}')
        self.icon = QtGui.QIcon(iconpath)

        # Create the tray app
        self.tray = QtWidgets.QSystemTrayIcon(self.icon, self.widget)
        self.tray.setContextMenu(self.menu)
        self.tray.setToolTip(tooltip)
        self.tray.showMessage('one', 'two', QtGui.QIcon(iconpath))

        # Show app
        self.tray.show()

    def restore_layout(self):
        raise Exception('Not implemented')

    def freeze_layout(self):
        logger.info('Freezing layout')

        # get current displays layout
        display_layout = osscreen.enum_displays(self.app)

        # find opened apps windows
        opened_windows = osscreen.enum_opened_windows(display_layout['screens'])

        # (ps)(debug)
        #self.db.clear()

        # search database for saved app configurations for current display layout
        layout_app_configs = db_enum_apps_for_curr_layout(self.db, display_layout['hash'])
        layout_apps = extract_process_names(layout_app_configs)

        # add each app config to database
        logger.debug('Adding to database app configs for opened winows')
        for window in opened_windows:
            simplified_app_config = simplify_app_config(opened_windows[window])
            window_reference_log = f'\"{opened_windows[window]["window_title"]}\" ({opened_windows[window]["process_name"]})'

            # skip if window is not visible or does not fit into active screens:
            if opened_windows[window]["display_index"] < 0:
                logger.debug(
                    f'Skipping window {window_reference_log}')
                logger.debug(
                    '(reason: Window is not visible or out of displays boundaries')
                continue

            # skip if the same exact app config is already in database
            if layout_app_configs:
                #if simplified_app_config in layout_app_configs:
                if opened_windows[window]['process_name'] in layout_apps:
                    logger.debug(
                        f'Skipping window {window_reference_log}')
                    logger.debug('(reason: already in database; use "Freeze Layout (replace)" to force-update)')
                    continue

            # add unique and valid config to database
            db_add_app_config(self.db, display_layout['hash'], simplified_app_config)

        # (ps)(debug)
        #print(self.db.list_all())

        
    def open_preferences(self):
        # keyboard shortcuts
        # snap to the grid

        raise Exception('Not implemented')



##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
