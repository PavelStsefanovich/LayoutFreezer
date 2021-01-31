from layoutfreezer import helpers
from layoutfreezer.db import Database
import logging
from PySide2 import QtGui
from PySide2 import QtWidgets
from os import path, makedirs
import sys
import traceback


##########  Global Properties  ####################

logger = logging.getLogger(__name__)


##########  Classes  ##############################

class SystemTrayApp():

    def __init__(self, iconpath, tooltip='SystemTrayApp', database_path='database', osscrn=None, prefs=None):
        self.osscrn = osscrn
        self.prefs = prefs

        # Initiate database connection
        database_path = path.abspath(database_path)
        logger.debug(f'database path: {database_path}')
        makedirs(path.split(database_path)[0], exist_ok=True)
        self.db = Database(database_path)

        # Init QApplication, QWidet and QMenu
        self.app = QtWidgets.QApplication([])
        self.widget = QtWidgets.QWidget()
        self.menu = QtWidgets.QMenu(self.widget)

        # Add items to menu
        self.menu_action_raise = self.menu.addAction("Freeze Layout")
        self.menu_action_raise.triggered.connect(self.freeze_layout)

        self.menu_action_raise = self.menu.addAction("Restore Layout")
        self.menu_action_raise.triggered.connect(self.restore_layout)

        self.menu_action_raise = self.menu.addSeparator()

        self.menu_action_raise = self.menu.addAction("Preferences")
        self.menu_action_raise.triggered.connect(self.open_preferences)

        self.menu_action_raise = self.menu.addSeparator()

        self.menu_action_exit = self.menu.addAction("Exit")
        self.menu_action_exit.triggered.connect(self.app.exit)

        # Create app icon
        iconpath = path.abspath(iconpath)
        logger.debug(f'systemTray icon path: {iconpath}')
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
        logger.info('USER COMMAND: "Freeze Layout"')

        logger.info('Getting current screen layout')
        display_layout = self.osscrn.enum_displays(self.app)

        logger.info('Looking for opened windows')
        opened_windows = self.osscrn.enum_opened_windows(display_layout['screens'], self.prefs)

        logger.info('Searching database for saved app position configurations for current screen layout')
        saved_app_configs = helpers.db_enum_apps_for_curr_screen_layout(self.db, display_layout['hash'])

        logger.info('Saving position configurations for opened apps into the database')
        for window in opened_windows:
            normalized_config = helpers.normalize_app_config(opened_windows[window])
            window_reference = f'{normalized_config[0]} [{normalized_config[1]}]'
            # skip if the same exact app config (process name + title) is already in database (based on preferences)
            if saved_app_configs:
                if helpers.app_config_already_saved(normalized_config, saved_app_configs):
                    logger.debug(f'preference "freeze_new_only" is set to "{self.prefs["freeze_new_only"]}"')
                    if self.prefs["freeze_new_only"]:
                        logger.debug(f'skipped: "{window_reference}" (reason: already in database)')
                        continue
                    logger.debug(f'removing config for: "{window_reference}"')
                    helpers.db_delete_app_config(self.db, display_layout['hash'], normalized_config)
            # add unique and valid app config to database
            logger.debug(f'adding config for: "{window_reference}"')
            helpers.db_add_app_config(self.db, display_layout['hash'], normalized_config)


    def open_preferences(self):
        # keyboard shortcuts
        # snap to the grid

        raise Exception('Not implemented')

#TODO remove
# self.db.clear()
#print(self.db.list_all())
# pass


##########  Functions  ############################

def excepthook(exc_type, exc_value, exc_tb):
    trace = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error(trace)


def load_preferences(preferences_path, preferences_default):
    preferences_path = path.abspath(preferences_path)
    preferences_default = path.abspath(preferences_default)
    logger.debug(f'preferences file path: {preferences_path}')
    makedirs(path.split(preferences_path)[0], exist_ok=True)
    try:
        prefs = helpers.load_config_yml(preferences_path)
    except Exception as e:
        logger.debug(e)
        logger.debug(f'copying default preferences from file "{preferences_default}"')
        helpers.copyfile(preferences_default, preferences_path)
        prefs = helpers.load_config_yml(preferences_path)
    return prefs


def run(main_config):
    sys.excepthook = excepthook

    logger.info("Gathering system info")
    main_config.update({'system': helpers.get_system_info()})

    logger.info("Importing OS-specific screen module")
    logger.debug(f'current os: {main_config["system"]["os"]}')
    osscrn = None
    if main_config["system"]["os"] == 'Windows':
        import layoutfreezer.os_screen.windows as osscrn
    if main_config["system"]["os"] == 'Linux':
        import layoutfreezer.os_screen.linux as osscrn
    if main_config["system"]["os"] == 'Mac':
        import layoutfreezer.os_screen.mac as osscrn

    logger.info('Loading preferences')
    prefs = load_preferences(
        main_config["preferences_path"], main_config["preferences_default"])

    logger.info("Initializing systray app")
    trayapp = SystemTrayApp(
        iconpath=main_config["systray_icon"],
        tooltip=f'{main_config["product_name"]} {main_config["version"]}',
        database_path=main_config["database_path"],
        osscrn=osscrn,
        prefs=prefs
    )

    trayapp.tray.showMessage(f'{main_config["product_name"]} has started',
                             'Use system tray icon for info and options', trayapp.icon)

    process = trayapp.app.exec_()
    logger.info('Stopping application')
    sys.exit(process)



##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
