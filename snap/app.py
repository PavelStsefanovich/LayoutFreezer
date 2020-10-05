import logging
import sys
import traceback

from .ui import SystemTrayApp



##########  Module Properties  ####################

logger = logging.getLogger(__name__)



##########  Functions  ############################

def excepthook(exc_type, exc_value, exc_tb):
    trace = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error(trace)


def run(main_config, preferences_path):
    logger.debug("Initializing systray app")
    sys.excepthook = excepthook

    trayapp = SystemTrayApp(
        iconpath=main_config["layout"]["systray_icon"],
        tooltip=f'{main_config["product"]} {main_config["version"]}',
        database_path=main_config["layout"]["database_path"],
        preferences_path=preferences_path)

    trayapp.tray.showMessage('Workstation Manager has started', 'Use system tray icon for info and options', trayapp.icon)

    process = trayapp.app.exec_()
    logger.info('Stopping application')
    sys.exit(process)



##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
