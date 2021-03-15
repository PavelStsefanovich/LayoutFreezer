from layoutfreezer.ai import adjust_window_rectangle
from layoutfreezer.gui import About, Preferences
from layoutfreezer import helpers
from layoutfreezer.db import Database
import logging
from os import path, makedirs
from pynput import keyboard
from PySide2.QtCore import Signal, Slot
from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QDialog,
    QMenu,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget)
import subprocess
import sys
import traceback


##########  Global Properties  ####################

logger = logging.getLogger(__name__)
listener = None


##########  Classes  ##############################

class SystemTrayApp(QSystemTrayIcon):

    freeze_all = Signal()
    freeze_new = Signal()
    restore = Signal()

    def __init__(self, config, osscrn, app):
        super().__init__()
        self.config = config
        self.osscrn = osscrn
        self.app = app
        self.widget = QWidget()
        self.about_dialog = None
        self.prefs_dialog = None
        self.freeze_all.connect(self.run_freeze_all)
        self.freeze_new.connect(self.run_freeze_new)
        self.restore.connect(self.run_restore)

        # Load preferences
        logger.info('Loading preferences')
        self.prefs = self.load_preferences()

        # Initialize database connection
        database_path = path.abspath(self.config["database_path"])
        logger.debug(f'database path: {database_path}')
        makedirs(path.split(database_path)[0], exist_ok=True)
        self.db = Database(database_path)

        # Icons
        app_iconpath = path.abspath(self.config["systray_icon"])
        self.favicon = QIcon(app_iconpath)
        if not path.isfile(app_iconpath):
            raise FileNotFoundError(f'App icon file not found: {app_iconpath}')
        self.setIcon(self.favicon)
        self.freeze_iconpath = path.abspath(self.config["freeze_icon"])
        if not path.isfile(self.freeze_iconpath):
            raise FileNotFoundError(f'Menu icon file not found: {self.freeze_iconpath}')
        self.restore_iconpath = path.abspath(self.config["restore_icon"])
        if not path.isfile(self.restore_iconpath):
            raise FileNotFoundError(f'Menu icon file not found: {self.restore_iconpath}')

        # System tray tooltip
        self.setToolTip(
            f'{self.config["product_name"]} {self.config["version"]}')

        # System tray menu
        self.set_context_menu()

        # hotkey listener
        self.set_hotkeys_listener()

        # Show app
        logger.info("App is up!")
        self.show()


    def set_context_menu(self):
        stmenu = QMenu()

        action_freeze_new = QAction(
            QIcon(self.freeze_iconpath), "Freeze New", self)
        action_freeze_new.setShortcut(QKeySequence(
            self.prefs["hotkeys"]["value"]["freeze_new"].replace('<', '').replace('>', '')))
        action_freeze_new.triggered.connect(self.freeze_layout)
        stmenu.addAction(action_freeze_new)

        action_freeze_all = QAction("Freeze All", self)
        action_freeze_all.setShortcut(QKeySequence(
            self.prefs["hotkeys"]["value"]["freeze_all"].replace('<', '').replace('>', '')))
        action_freeze_all.triggered.connect(self.freeze_layout_all)
        stmenu.addAction(action_freeze_all)

        action_restore = QAction(
            QIcon(self.restore_iconpath), "Restore Layout", self)
        action_restore.setShortcut(QKeySequence(
            self.prefs["hotkeys"]["value"]["restore"].replace('<', '').replace('>', '')))
        action_restore.triggered.connect(self.restore_layout)
        stmenu.addAction(action_restore)

        stmenu.addSeparator()

        action_prefs = stmenu.addAction("Preferences")
        action_prefs.triggered.connect(self.open_preferences)

        action_clear_db = stmenu.addAction("Clear Database")
        action_clear_db.triggered.connect(self.clear_database)

        action_prefs = stmenu.addAction("About")
        action_prefs.triggered.connect(self.open_about)

        stmenu.addSeparator()

        action_exit = stmenu.addAction("Exit")
        action_exit.triggered.connect(self.app.exit)

        self.setContextMenu(stmenu)


    def load_preferences(self):
        preferences_path = path.abspath(
            self.config["preferences_path"])
        preferences_default_path = path.abspath(
            self.config["preferences_default_path"])
        logger.debug(f'preferences file path: {preferences_path}')
        makedirs(path.split(preferences_path)[0], exist_ok=True)
        try:
            prefs = helpers.load_yaml(preferences_path)
        except Exception as e:
            logger.debug(e)
            logger.debug(
                f'copying default preferences from file "{preferences_default_path}"')
            helpers.copyfile(preferences_default_path, preferences_path)
            prefs = helpers.load_yaml(preferences_path)
        return prefs


    def save_preferences(self):
        logger.debug('saving preferences')
        preferences_path = path.abspath(
            self.config["preferences_path"])
        helpers.dump_yaml(self.prefs, preferences_path)


    @Slot()
    def run_freeze_all(self):
        logger.debug(f'hotkeys detected: {self.prefs["hotkeys"]["value"]["freeze_all"]}')
        self.freeze_layout_all()


    @Slot()
    def run_freeze_new(self):
        logger.debug(f'hotkeys detected: {self.prefs["hotkeys"]["value"]["freeze_new"]}')
        self.freeze_layout()


    @Slot()
    def run_restore(self):
        logger.debug(f'hotkeys detected: {self.prefs["hotkeys"]["value"]["restore"]}')
        self.restore_layout()


    def set_hotkeys_listener(self):
        global listener
        try:
            listener.stop()
        except:
            pass
        if self.prefs["enable_hotkeys"]["value"]:
            listener = keyboard.GlobalHotKeys({
                self.prefs['hotkeys']['value']['freeze_all']      : self.freeze_all.emit,
                self.prefs['hotkeys']['value']['freeze_new'] : self.freeze_new.emit,
                self.prefs['hotkeys']['value']['restore']         : self.restore.emit})
            listener.start()


    def freeze_layout_all(self):
        self.freeze_layout(all=True)


    def freeze_layout(self, all=False):
        if all:
            logger.info('USER COMMAND: "Freeze All"')
        else:
            logger.info('USER COMMAND: "Freeze New"')

        logger.info('Getting current screen layout')
        display_layout = self.osscrn.enum_displays(self.app)

        logger.info('Reloading preferences')
        self.prefs = self.load_preferences()

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
            if saved_app_configs:
                matches = helpers.get_config_matches(normalized_config, saved_app_configs)
                if matches and not isinstance(matches, dict):
                    if not all:
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
        self.prefs = self.load_preferences()

        logger.info('Looking for opened windows')
        # prefs = self.prefs.copy() |--> this does not work as expected, workaround below:
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
        if self.prefs_dialog:
            logger.debug('user re-issued command: "Preferences" while dialog is open')
            self.prefs_dialog.show()
            self.prefs_dialog.raise_()
            self.prefs_dialog.activateWindow()
        else:
            logger.info('USER COMMAND: "Preferences"')
            self.prefs_dialog = Preferences(self.prefs, self.favicon)
            self.prefs_dialog.show()
            self.prefs_dialog.exec_()
            self.prefs = self.prefs_dialog.prefs
            self.prefs_dialog = None
            self.save_preferences()
            self.set_hotkeys_listener()
            self.set_context_menu()
            logger.info('Finished processing command "Preferences"')


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


    def open_about(self):
        if self.about_dialog:
            logger.debug('user re-issued command: "About" while dialog is open')
            self.about_dialog.show()
            self.about_dialog.raise_()
            self.about_dialog.activateWindow()
        else:
            logger.info('USER COMMAND: "About"')
            self.about_dialog = About(self.config, self.favicon)
            self.about_dialog.show()
            self.about_dialog.exec_()
            self.about_dialog = None
            logger.info('Finished processing command "About"')



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
    listener.stop()
    logger.info('Stopping application')
    sys.exit()


##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
