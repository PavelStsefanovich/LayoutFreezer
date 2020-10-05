#import argparse
#import snap.app
import json
import logging
import logging.config
import os
import re
import sys
from datetime import datetime
#from ruamel.yaml import YAML



##########  Global Properties  ####################
global main_config, logger#, cmd_args
main_config = {}
main_config["start_time"] = datetime.now()
main_config["timestamp"] = main_config["start_time"].strftime("%Y-%m-%d_%H-%M-%S")

if getattr(sys, "frozen", False):
    main_config["root_dir"] = os.path.realpath(os.path.dirname(sys.executable))
elif __file__:
    main_config["root_dir"] = os.path.realpath(sys.path[0])

main_config["conf_dir"] = os.path.realpath(os.path.join(
    main_config["root_dir"], "config"))

# cmd_parser = argparse.ArgumentParser()
# cmd_parser.add_argument("--debug", "-d", help="Set log level: DEBUG (default is INFO)")
# cmd_args = vars(cmd_parser.parse_args())



##################   Functions  ###################
# def isadmin():
#     try:
#         return bool(ctypes.windll.shell32.IsUserAnAdmin())
#     except:
#         return False

def init():
    # setup logger
    try:
        setup_logger(
            logger_config_path=f'{main_config["conf_dir"]}\\logger.json',
            timestamp=main_config["timestamp"])
        logger = logging.getLogger(__name__)
        logger.info('Logger is up!')
    except:
        print('(!) ERROR: Failed to setup logger (!)')
        raise

    # load main config
    # logger.info('Loading main config')
    # with open(main, "rt") as file:
    #     logger_config = json.load(file)


def setup_logger(
        logger_config_path="logger.json",
        timestamp=datetime.now().strftime("%Y-%m-%d_%H-%M-%S")):

    # load logger config
    logger_config_path = os.path.abspath(logger_config_path)
    with open(logger_config_path, "rt") as file:
        logger_config = json.load(file)

    # resolve logfiles paths, create directories
    for handler in logger_config["handlers"]:
        try:
            # replace timestamp placeholder
            logger_config["handlers"][handler]["filename"] = logger_config["handlers"][handler]["filename"].replace(
                "@timestamp@", timestamp)
            
            # replace env var placeholder
            env_var = re.match('^@env\:([^@]+)@', logger_config["handlers"][handler]["filename"])            
            if isinstance(env_var, re.Match):
                logger_config["handlers"][handler]["filename"] = logger_config["handlers"][handler]["filename"].replace(
                    env_var.group(0), os.environ[env_var.group(1)], 1)

            logdir = os.path.split(os.path.abspath(
                logger_config["handlers"][handler]["filename"]))[0]
            os.makedirs(logdir, exist_ok=True)
        except:
            pass

    # apply logger config
    logging.config.dictConfig(logger_config)



##########  Main  #################################
if __name__ == "__main__":

    # invoke main program
    try:
        # run init
        print(main_config)
        init()
        print(main_config)
        print('done')

        # invoke main program
        # logger.info('Starting application')
        # preferences_path = main_config['layout']['preferences_path']
        # snap.main.run(main_config, preferences_path)
        # pass
    except Exception as e:
        try:
            #snap.app.errpopup(e)
            print(f'(!){e}')
            logger.exception(e)
        except:
            pass
        raise e
