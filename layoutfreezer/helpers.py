import json
import logging
import logging.config
import os
import re
import sys
import yaml
from datetime import datetime
from .gui import show_critical_error_dialog


##########  Global Properties  ####################

logger = logging.getLogger(__name__)


##########  Functions  ############################

def get_root_dir():
    if getattr(sys, "frozen", False):
        return os.path.realpath(os.path.dirname(sys.executable))
    elif __file__:
        return os.path.realpath(sys.path[0])


def setup_logger(
        logger_config_path="logger.json",
        start_time=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        timestamp_format="%Y-%m-%d_%H-%M-%S"):

    timestamp = start_time.strftime(timestamp_format)

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


def load_config_yml(config_file_path, log=True):
    if log:
        logger.debug(f'reading YAML file "{config_file_path}"')
    with open(config_file_path, "rt") as file:
        config = yaml.safe_load(file)
    if log:
        logger.debug(f'loaded YAML config: "{config}"')
    return config


def errpopup(errormessage=None, level=None):
    if level == 'critical':
        show_critical_error_dialog(errormessage=errormessage)


def dict_expand_vars(dic1=None, dic2=None):
    if not dic1:
        return dic1
    if not dic2:
        dic2 = dic1.copy()
    dic = dic1.copy()
    for el in dic1:
        if isinstance(dic1[el], dict):
            dic[el] = dict_expand_vars(dic[el], dic)
            continue
        if isinstance(dic1[el], str):
            if re.match(r'^\~[\\\/]', dic[el]):
                dic[el] = re.sub(
                    r'^\~(?=[\\\/])', os.path.expanduser('~').replace('\\', '/'), dic[el])
            el_placeholders = re.findall(r'\{\w+\}', dic[el])
            for placeholder in el_placeholders:
                env_var = re.match(r'^env_(\w+)', placeholder.strip('{}'))
                if env_var:
                    if env_var[1] in os.environ:
                        dic[el] = dic[el].replace(
                            placeholder, os.environ[env_var[1]])
                    continue
                placeholder_value = dic2.get(placeholder.strip('{}'))
                if isinstance(placeholder_value, str):
                    dic[el] = dic[el].replace(
                        placeholder, placeholder_value)

    return dic


##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
