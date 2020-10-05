import json
import logging
import logging.config
import os
import re
import sys

from datetime import datetime
from ruamel.yaml import YAML



##########  Module Properties  ####################

logger = logging.getLogger(__name__)



##########  Functions  ############################

def get_root_dir():
    if getattr(sys, "frozen", False):
        return os.path.realpath(os.path.dirname(sys.executable))
    elif __file__:
        return os.path.realpath(sys.path[0])

def join_path(parent, child):
    return os.path.realpath(os.path.join(parent, child))

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
            env_var = re.match(
                '^@env\:([^@]+)@', logger_config["handlers"][handler]["filename"])
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

def load_config_yml(config_file_path):
    yaml = YAML(typ='safe')
    with open(config_file_path, "rt") as file:
        config = yaml.load(file)
    return config

def errpopup(exception):
    pass



##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
