from layoutfreezer.ai import adjust_window_rectangle
from layoutfreezer import helpers
from layoutfreezer.db import Database
import logging
from os import path, makedirs
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon, QWidget
import subprocess
import sys
import traceback


##########  Global Properties  ####################

logger = logging.getLogger(__name__)


##########  Classes  ##############################

class SystemTrayApp(QSystemTrayIcon):

    def __init__(self, config, osscrn, app):
        super().__init__()
        self.config = config
        self.osscrn = osscrn
        self.app = app
        self.widget = QWidget()

        # Loading preferences
        logger.info('Loading preferences')
        self.prefs = helpers.load_preferences(
            self.config["preferences_path"], self.config["preferences_default_path"])

        # Initialize database connection
        database_path = path.abspath(self.config["database_path"])
        logger.debug(f'database path: {database_path}')
        makedirs(path.split(database_path)[0], exist_ok=True)
        self.db = Database(database_path)

        # System tray icon
        iconpath = path.abspath(self.config["systray_icon"])
        logger.debug(f'systemTray icon path: {iconpath}')
        self.setIcon(QIcon(iconpath))

        # System tray tooltip
        self.setToolTip(
            f'{self.config["product_name"]} {self.config["version"]}')

        # System tray menu
        stmenu = QMenu()

        action_freeze = stmenu.addAction("Freeze Layout")
        action_freeze.triggered.connect(self.freeze_layout)

        action_restore = stmenu.addAction("Restore Layout")
        action_restore.triggered.connect(self.restore_layout)

        stmenu.addSeparator()

        action_prefs = stmenu.addAction("Preferences")
        action_prefs.triggered.connect(self.open_preferences)

        action_clear_db = stmenu.addAction("Clear Database")
        action_clear_db.triggered.connect(self.clear_database)

        stmenu.addSeparator()

        action_exit = stmenu.addAction("Exit")
        action_exit.triggered.connect(self.app.exit)

        self.setContextMenu(stmenu)

        # Show app
        self.show()


    def freeze_layout(self):
        logger.info('USER COMMAND: "Freeze Layout"')

        logger.info('Getting current screen layout')
        display_layout = self.osscrn.enum_displays(self.app)

        logger.info('Reloading preferences')
        self.prefs = helpers.load_preferences(
            self.config["preferences_path"], self.config["preferences_default_path"])

        logger.info('Looking for opened windows')
        opened_windows = self.osscrn.enum_opened_windows(
            display_layout['screens'], self.prefs)

        logger.info('Searching database for saved app position configurations for current screen layout')
        saved_app_configs = helpers.db_enum_apps_for_curr_screen_layout(
            self.db, display_layout['hash'])

        logger.info('Saving position configurations for opened apps into the database')
        for window in opened_windows:
            normalized_config = helpers.normalize_app_config(opened_windows[window])
            window_reference = f'{normalized_config[0]} [{normalized_config[1]}]'
            # skip if the same exact app config (process name + title) is already in database
            # (based on 'freeze_new_only' preference)
            if saved_app_configs:
                matches = helpers.get_config_matches(normalized_config, saved_app_configs)
                if matches and not isinstance(matches, dict):
                    logger.debug(f'preference "freeze_new_only" is set to "{self.prefs["freeze_new_only"]["value"]}"')
                    if self.prefs["freeze_new_only"]["value"]:
                        logger.debug(f'skipped: "{window_reference}" (reason: already in database)')
                        continue
                    logger.debug(f'removing config for: "{window_reference}"')
                    helpers.db_delete_app_config(self.db, display_layout['hash'], normalized_config)
            # add unique and valid app config to database
            logger.debug(f'adding config for: "{window_reference}"')
            helpers.db_add_app_config(self.db, display_layout['hash'], normalized_config)

        logger.info('Finished processing command "Freeze Layout"')


    def restore_layout(self):
        logger.info('USER COMMAND: "Restore Layout"')

        logger.info('Getting current screen layout')
        display_layout = self.osscrn.enum_displays(self.app)

        logger.info('Reloading preferences')
        self.prefs = helpers.load_preferences(
            self.config["preferences_path"], self.config["preferences_default_path"])

        logger.info('Looking for opened windows')
        # workaround for this statement not working as expected:
        # prefs = self.prefs.copy()
        prefs = {}
        for el in self.prefs:
            prefs[el] = self.prefs[el].copy()
        prefs["snap_to_grid"]["value"] = False
        prefs["fit_into_screen"]["value"] = False
        opened_windows = self.osscrn.enum_opened_windows(
            display_layout['screens'], prefs)

        logger.info('Searching database for saved app position configurations for current screen layout')
        saved_app_configs = helpers.db_enum_apps_for_curr_screen_layout(
            self.db, display_layout['hash'])

        logger.info('Restoring position configurations for opened apps')
        for window in opened_windows:
            normalized_config = helpers.normalize_app_config(opened_windows[window])
            window_reference = f'{normalized_config[0]} [{normalized_config[1]}]'

            logger.debug(f'adjusting position config for: {window_reference}')
            adjusted_window_rectangle = adjust_window_rectangle(
                normalized_config,
                saved_app_configs,
                display_layout,
                self.osscrn,
                self.prefs)

            logger.debug(f'restoring window position: {window_reference}')
            self.osscrn.move_window(window, adjusted_window_rectangle)

        logger.info('Finished processing command "Restore Layout"')


    def open_preferences(self):
        logger.info('USER COMMAND: "Preferences"')

        #TODO temporary implementation using notepad
        logger.debug('opening preferences file in notepad.exe')
        commandline = f'notepad "{self.config["preferences_path"]}"'
        process = subprocess.run(commandline)
        if process.returncode != 0:
            raise Exception(process)

        logger.info('Finished processing command "Restore Layout"')


    def clear_database(self):
        logger.info('USER COMMAND: "Clear Database"')

        logger.debug('asking user for confirmation')
        reply = QMessageBox.warning(
            self.widget,
            self.config["product_name"],
            "You are about to delete all saved layouts from the database.",
            QMessageBox.Ok | QMessageBox.Abort,
            QMessageBox.Abort
        )

        if reply == QMessageBox.Ok:
            logger.debug('user clicked "OK"')
            logger.debug('dropping database')
            self.db.clear()
        elif reply == QMessageBox.Abort:
            logger.debug('user clicked "Abort"')
            logger.debug('operation cancelled')

        logger.info('Finished processing command "Clear Database"')


##########  Functions  ############################

def excepthook(exc_type, exc_value, exc_tb):
    trace = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error(trace)


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

    logger.info("Initializing systray app")
    application = QApplication(sys.argv)
    application.setQuitOnLastWindowClosed(False)
    trayapp = SystemTrayApp(config=main_config, osscrn=osscrn, app=application)
    trayapp.showMessage(f'{main_config["product_name"]} has started',
                             'Use system tray icon for info and options', trayapp.icon())

    application.exec_()
    logger.info('Stopping application')
    sys.exit()


##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
