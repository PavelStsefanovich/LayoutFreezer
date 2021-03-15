from datetime import datetime
from layoutfreezer import gui
import json
import logging
import logging.config
from os import path, makedirs, environ
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
        return path.realpath(path.dirname(sys.executable))
    elif __file__:
        return path.realpath(sys.path[0])


def setup_logger(
        logger_config_path="logger.json",
        logs_dir="logs",
        start_time=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        timestamp_format="%Y-%m-%d_%H-%M-%S"):

    timestamp = start_time.strftime(timestamp_format)

    # load logger config
    logger_config_path = path.abspath(logger_config_path)
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
            makedirs(logs_dir, exist_ok=True)
        except:
            pass

    # apply logger config
    logging.config.dictConfig(logger_config)


def load_yaml(yaml_file_path, log=True):
    if log:
        logger.debug(f'reading YAML file "{yaml_file_path}"')
    with open(yaml_file_path, "rt") as file:
        config = yaml.safe_load(file)
    if log:
        logger.debug(f'loaded YAML config: "{config}"')
    return config


def dump_yaml(data, yaml_file_path, log=True):
    if log:
        logger.debug(f'writing into YAML file "{yaml_file_path}"')
    with open(yaml_file_path, "w") as file:
        yaml.safe_dump(data, file, default_style='|')


def errpopup(errormessage=None, level=None):
    if level == 'critical':
        gui.show_critical_error_dialog(errormessage=errormessage)


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
                    r'^\~(?=[\\\/])', path.expanduser('~').replace('\\', '/'), dic[el])
            el_placeholders = re.findall(r'\{\w+\}', dic[el])
            for placeholder in el_placeholders:
                env_var = re.match(r'^env_(\w+)', placeholder.strip('{}'))
                if env_var:
                    if env_var[1] in environ:
                        dic[el] = dic[el].replace(
                            placeholder, environ[env_var[1]])
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


def db_add_app_config(db, dl_hash, normalized_config):
    logger.debug(f'adding to database: {normalized_config}')
    db.add(
        dl_hash,
        normalized_config[0],
        normalized_config[1],
        normalized_config[2],
        normalized_config[3],
        normalized_config[4],
        normalized_config[5]
    )


def db_delete_app_config(db, dl_hash, normalized_config):
    logger.debug(f'deleting window config from database: {normalized_config}')
    db.delete(dl_hash=dl_hash, name=normalized_config[0], title=normalized_config[1])


def db_delete_current_display_layout(db, dl_hash):
    logger.debug(f'deleting display layout from database: {dl_hash}')
    db.delete(dl_hash=dl_hash)


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


def get_config_matches(normalized_config, saved_app_configs):
    logger.debug(f'looking for saved config matches for: "{normalized_config}"')
    partial_matches = []
    for app_config in saved_app_configs:
        if app_config[0:2] == normalized_config[0:2]:
            logger.debug(f'found full match: {app_config}')
            return app_config
        elif app_config[0] == normalized_config[0]:
            logger.debug(f'found partial match: {app_config}')
            partial_matches.append(app_config)

    if partial_matches:
        return {'partial_matches' : partial_matches}

    logger.debug('no matches found')
    return None


##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
