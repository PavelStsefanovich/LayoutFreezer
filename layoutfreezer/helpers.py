from datetime import datetime
from .gui import show_critical_error_dialog
import json
import logging
import logging.config
import os
import platform
import re
from shutil import copyfile
import sys
import yaml


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
        logs_dir="logs",
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
            # replace placeholders
            logger_config["handlers"][handler]["filename"] = logger_config["handlers"][handler]["filename"].replace(
                "@logs_dir@", logs_dir)
            logger_config["handlers"][handler]["filename"] = logger_config["handlers"][handler]["filename"].replace(
                "@timestamp@", timestamp)
            os.makedirs(logs_dir, exist_ok=True)
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


def get_system_info():
    sys_info = {}
    sys_info["os"] = platform.system()
    # more entries as needed
    return sys_info


def db_enum_apps_for_curr_screen_layout(db, dl_hash, normalize=True):
    logger.debug(f'looking in database for saved app position configurations for screen layout "{dl_hash}"')
    layout_app_configs = db.search(dl_hash=dl_hash, order_by='process_name')

    if normalize:
        results = []
        for item in layout_app_configs:
            results.append(item[2:])
    else:
        results = layout_app_configs

    if results:
        logger.debug(f'found saved app position configurations: {results}')
    else:
        logger.debug(f'no saved app position configurations found for screen layout "{dl_hash}"')

    return results


def db_add_app_config(db, dl_hash, normalized_app_config):
    logger.debug(f'adding to database: {normalized_app_config}')
    db.add(
        dl_hash,
        normalized_app_config[0],
        normalized_app_config[1],
        normalized_app_config[2],
        normalized_app_config[3],
        normalized_app_config[4],
        normalized_app_config[5]
    )


def db_delete_app_config(db, dl_hash, normalized_app_config):
    #TODO: implement
    # saved_config = db.search(dl_hash=dl_hash
    pass


def normalize_app_config(app_config):
    result = (
        app_config['process_name'],
        app_config['window_title'],
        str(app_config['window_rectangle']),
        app_config['display_index'],
        app_config['display_orientation'],
        int(app_config['display_primary'])
    )
    return result


def app_config_already_saved(normalized_app_config, saved_app_configs):
    #TODO: implement
    return True


##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
