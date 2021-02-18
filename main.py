from datetime import datetime
from layoutfreezer import helpers, app
import logging
from os import path
import sys


##########  Global Properties  ####################

main_config = {}
main_config["start_time"] = datetime.now()
main_config["install_dir"] = helpers.get_root_dir()


##################   Functions  ###################

def init():
    # load config from file config.yml
    global main_config
    main_config_filepath = path.realpath(
        path.join(main_config["install_dir"], "config.yml"))
    errormessage = f'LayoutFreezer failed to start.\n'

    try:
        main_config.update(
            helpers.load_config_yml(
                config_file_path=main_config_filepath,
                log=False
            )
        )
    except Exception as e:
        errormessage += f'Reason: Failed to load main config.\n'
        errormessage += f'Exception: {e}'
        helpers.errpopup(errormessage=errormessage, level='critical')
        sys.exit()

    main_config = helpers.dict_expand_vars(main_config)

    # setup logger
    try:
        helpers.setup_logger(
            logger_config_path=main_config["logger_config"],
            logs_dir=main_config["logs_dir"],
            start_time=main_config["start_time"],
            timestamp_format=main_config["timestamp_format"]
        )
        global logger
        logger = logging.getLogger(__name__)
        logger.info('Logger is up!')
    except Exception as e:
        errormessage += f'Reason: Failed to setup logger.\n'
        errormessage += f'Exception: {e}'
        helpers.errpopup(errormessage=errormessage, level='critical')
        sys.exit()


def run():
    global main_config
    try:
        logger.info('Starting application')
        app.run(main_config)
    except Exception as e:
        logger.error('FATAL EXCEPTION OCCURRED:')
        logger.error(e)
        raise


##########  Main  #################################

if __name__ == "__main__":
    init()
    run()
