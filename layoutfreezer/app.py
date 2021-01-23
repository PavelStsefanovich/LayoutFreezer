import logging
import sys
import traceback
from .db import Database
from PySide2 import QtGui
from PySide2 import QtWidgets
from os import path, makedirs


##########  Global Properties  ####################

logger = logging.getLogger(__name__)


##########  Classes  ##############################

class SystemTrayApp():

    def __init__(self, iconpath, tooltip='SystemTrayApp', database_path='database'):
        # Initiate database connection
        database_path = database_path.replace('~', path.expanduser('~'))
        database_path = path.abspath(database_path)
        logger.debug(f'Database path: {database_path}')
        makedirs(path.split(database_path)[0], exist_ok=True)
        self.db = Database(database_path)

        # Set preferences file path
        # self.preferences_path = path.abspath(preferences_path)

        # Init QApplication, QWidet and QMenu
        self.app = QtWidgets.QApplication([])
        self.widget = QtWidgets.QWidget()
        self.menu = QtWidgets.QMenu(self.widget)

        # Add items to menu
        self.menu_action_raise = self.menu.addAction("Restore Layout")
        self.menu_action_raise.triggered.connect(self.restore_layout)

        # self.menu_action_raise = self.menu.addAction("Freeze Layout")
        # self.menu_action_raise.triggered.connect(self.freeze_layout)

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

    # def freeze_layout(self):
    #     logger.info('Freezing layout')

    #     # get current displays layout
    #     display_layout = osscreen.enum_displays(self.app)

    #     # find opened apps windows
    #     opened_windows = osscreen.enum_opened_windows(
    #         display_layout['screens'])

    #     # (ps)(debug)
    #     #self.db.clear()

    #     # search database for saved app configurations for current display layout
    #     layout_app_configs = db_enum_apps_for_curr_layout(
    #         self.db, display_layout['hash'])
    #     layout_apps = extract_process_names(layout_app_configs)

    #     # add each app config to database
    #     logger.debug('Adding to database app configs for opened winows')
    #     for window in opened_windows:
    #         simplified_app_config = simplify_app_config(opened_windows[window])
    #         window_reference_log = f'\"{opened_windows[window]["window_title"]}\" ({opened_windows[window]["process_name"]})'

    #         # skip if window is not visible or does not fit into active screens:
    #         if opened_windows[window]["display_index"] < 0:
    #             logger.debug(
    #                 f'Skipping window {window_reference_log}')
    #             logger.debug(
    #                 '(reason: Window is not visible or out of displays boundaries')
    #             continue

    #         # skip if the same exact app config is already in database
    #         if layout_app_configs:
    #             #if simplified_app_config in layout_app_configs:
    #             if opened_windows[window]['process_name'] in layout_apps:
    #                 logger.debug(
    #                     f'Skipping window {window_reference_log}')
    #                 logger.debug(
    #                     '(reason: already in database; use "Freeze Layout (replace)" to force-update)')
    #                 continue

    #         # add unique and valid config to database
    #         db_add_app_config(
    #             self.db, display_layout['hash'], simplified_app_config)

        # (ps)(debug)
        #print(self.db.list_all())

    def open_preferences(self):
        # keyboard shortcuts
        # snap to the grid

        raise Exception('Not implemented')


##########  Functions  ############################

def excepthook(exc_type, exc_value, exc_tb):
    trace = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error(trace)


def run(main_config):
    #TODO: validate main_config
    logger.debug("initializing systray app")
    sys.excepthook = excepthook

    trayapp = SystemTrayApp(
        iconpath=main_config["systray_icon"],
        tooltip=f'{main_config["product_name"]} {main_config["version"]}',
        database_path=main_config["database_path"]
    )

    trayapp.tray.showMessage(f'{main_config["product_name"]} has started',
                             'Use system tray icon for info and options', trayapp.icon)

    process = trayapp.app.exec_()
    logger.info('Stopping application')
    sys.exit(process)



##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
