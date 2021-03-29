'''
@PavelStsefanovich:
This module is intended for integration with machine learning algorithms
that can be used to learn users' apps positioning habits
to predict most probable layout configurations
for the apps that are not in the database.

However, currently this module only adjusts layout configuraion
for the apps that have been previously saved into the database.
It attempts some rudimentary guessing of positioning
for the apps with partial match (when process name matches,
but screen layout or title is different)
'''

from difflib import get_close_matches
import logging


##########  Global Properties  ####################

logger = logging.getLogger(__name__)


##########  Functions  ############################

def convert_rectangle_to_int(str_rect):
    return [int(i) for i in str_rect.strip('[()]').split(', ')]


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


def get_closest_match(normalized_config, matches, cutoff):
    curr_title = normalized_config[1]
    compare_titles = list(zip(*matches))[1]
    closest_match_title = get_close_matches(
        curr_title, compare_titles, n=1, cutoff=cutoff)
    if closest_match_title:
        logger.debug(f'most closely matching title: {closest_match_title[0]}')
        for m in matches:
            if m[1] == closest_match_title[0]:
                return m
    logger.debug(
        f'no closely matching titles found; using first config in the list for given process: {matches[0]}')
    return matches[0]


def guess_position(app_configs, screens, priority_order):
    params_index_map = {
        'process_name'        : 0,
        'window_title'        : 1,
        'window_rectangle'    : 2,
        'display_index'       : 3,
        'display_orientation' : 4,
        'display_primary'     : 5
    }

    params_common_value_map = {}

    most_common_element = lambda l:  max(set(l), key = l.count)

    index = 0
    for screen in screens:
        screen["index"] = index
        if screen["primary"]:
            screen["primary"] = 1
        else:
            screen["primary"] = 0
        index += 1

    all_indexes = list(map(lambda config: config[params_index_map["display_index"]], app_configs))
    params_common_value_map["display_index"] = most_common_element(all_indexes)

    all_orientations = list(map(lambda config: config[params_index_map["display_orientation"]], app_configs))
    params_common_value_map["display_orientation"] = most_common_element(all_orientations)

    all_isprimaries = list(map(lambda config: config[params_index_map["display_primary"]], app_configs))
    params_common_value_map["display_primary"] = most_common_element(all_isprimaries)

    # detirmine most appropriate display
    for param in priority_order:
        if param == 'display_index':
            # find matching display index from right to left
            while True:
                matching_screens = list(filter(lambda screen: screen["index"] == params_common_value_map[param], screens))
                if matching_screens:
                    screens = matching_screens
                    break
                params_common_value_map[param] -= 1
                # break if not found (should never happen)
                if params_common_value_map[param] == -1:
                    break

        else:
            # filter only matching screens, otherwise do not modify screens
            try:
                matching_screens = list(filter(lambda screen: screen[param.replace('display_', '')] == params_common_value_map[param], screens))
                if matching_screens:
                    screens = matching_screens
            except:
                pass

        # if only single screen remains, return it as result
        if len(screens) == 1:
            break

    # detirmine maximum appropriate window size
    max_width = 0
    max_height = 0

    for config in app_configs:
        rect = convert_rectangle_to_int(config[params_index_map["window_rectangle"]])
        if rect[2] - rect[0] > max_width:
            max_width = rect[2] - rect[0]
        if rect[3] - rect[1] > max_height:
            max_height = rect[3] - rect[1]

    adjusted_rect = screens[0]["rectangle"]
    adjusted_rect[2] = adjusted_rect[0] + max_width
    adjusted_rect[3] = adjusted_rect[1] + max_height

    return adjusted_rect


def adjust_window_rectangle(
        normalized_config,
        curr_display_app_configs,
        curr_app_all_saved_configs,
        display_layout,
        osscrn,
        prefs):

    # looking for matches in saved configurations
    matches = get_config_matches(normalized_config, curr_display_app_configs)
    if matches:
        if isinstance(matches, dict):
            # partial matches
            closest_match = get_closest_match(
                normalized_config,
                matches["partial_matches"],
                prefs["match_cutoff"]["value"]
            )
            adjusted_rect = convert_rectangle_to_int(closest_match[2])
        else:
            # full match
            adjusted_rect = convert_rectangle_to_int(matches[2])
    else:
        # no match
        if len(curr_app_all_saved_configs) >0:
            # try to guess, if there is at least one saved config for current app across display layouts
            adjusted_rect = guess_position(
                curr_app_all_saved_configs,
                display_layout["screens"],
                prefs["guess_params_priority_order"]["value"]
            )
        else:
            # if there are no saved configs at all for current app then just return current position
            adjusted_rect = convert_rectangle_to_int(normalized_config[2])

    # fit adjusted_rect into screen and grid
    if prefs["snap_to_grid"]["value"]:
        adjusted_rect = osscrn.adjust_rect_to_grid(adjusted_rect)
    if prefs["fit_into_screen"]["value"]:
        display_index = osscrn.get_display_index(display_layout['screens'], adjusted_rect)
        adjusted_rect = osscrn.fit_rect_into_screen(
            adjusted_rect, display_layout['screens'][display_index]['rectangle'])

    return adjusted_rect


##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
