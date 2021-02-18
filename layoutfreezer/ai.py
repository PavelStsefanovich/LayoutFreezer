'''
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
from layoutfreezer.helpers import get_config_matches
import logging


##########  Global Properties  ####################

logger = logging.getLogger(__name__)


##########  Functions  ############################

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
    logger.debug('no closely matching titles found')
    return normalized_config


def convert_rectangle_to_int(str_rect):
    return [int(i) for i in str_rect.strip('[()]').split(', ')]


def adjust_window_rectangle(
        normalized_config,
        saved_app_configs,
        display_layout,
        osscrn,
        prefs):

    # looking for matches in saved configurations
    matches = get_config_matches(normalized_config, saved_app_configs)
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
