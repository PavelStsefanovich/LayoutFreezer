import hashlib
import logging
from operator import itemgetter
import os
from PySide2 import QtCore
import sys
import win32api as wapi
import win32con as wcon
import win32gui as wgui
import win32process as wproc


##########  Global Properties  ####################

logger = logging.getLogger(__name__)


##########  Functions  ############################

def get_hash(source_object):
    string_repr = str(source_object)
    return hashlib.sha1(string_repr.encode()).hexdigest()


def get_display_index(screens, win_rectangle):
    for scr_index in range(0, len(screens)):
        scr_rectangle = screens[scr_index]['full_rectangle']
        if win_rectangle[0] >= scr_rectangle[0] and win_rectangle[0] <= scr_rectangle[2]:
            return scr_index
        if scr_index == 0 and win_rectangle[0] < scr_rectangle[0]:
            return 0
    if win_rectangle[0] > scr_rectangle[2]:
        return (len(screens) - 1)
    return -1


def adjust_rect_to_grid(rect):
    rect_adjusted = []
    for i in range(len(rect)):
        mod = rect[i] % 5
        if mod > 0:
            if mod < 3:
                rect_adjusted.append(rect[i] - mod)
            else:
                rect_adjusted.append(rect[i] + (5 - mod))
        else:
            rect_adjusted.append(rect[i])
    return rect_adjusted


def fit_rect_into_screen(rect, screen_rect):
    rect_adjusted = []
    for coord in rect:
        rect_adjusted.append(coord)
    if rect_adjusted[0] < screen_rect[0]:
        rect_adjusted[0] = screen_rect[0]
    if rect_adjusted[1] < screen_rect[1]:
        rect_adjusted[1] = screen_rect[1]
    if rect_adjusted[2] > screen_rect[2]:
        rect_adjusted[2] = screen_rect[2]
    if rect_adjusted[3] > screen_rect[3]:
        rect_adjusted[3] = screen_rect[3]
    return rect_adjusted


def is_maximized(hwnd):
    placement = wgui.GetWindowPlacement(hwnd)
    if placement[0] == 2 and placement[1] == 3:
        return True
    return False


def enum_displays(qtapp):
    displays = []
    screens = qtapp.screens()

    for scr in screens:
        rect = scr.availableGeometry().getRect()
        rectangle = [rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3]]
        display = {}
        display.update({'primary': False})
        display.update({'orientation': 'landscape'})
        display.update({'rectangle': rectangle})

        full_rect = scr.geometry().getRect()
        full_rectangle = [full_rect[0], full_rect[1], full_rect[0]+rect[2], full_rect[1]+rect[3]]
        display.update({'full_rectangle': full_rectangle})
        if full_rect[0] == 0 and full_rect[1] == 0:
            display.update({'primary': True})

        if scr.orientation() is QtCore.Qt.ScreenOrientation.PortraitOrientation:
            display.update({'orientation': 'portrait'})

        displays.append(display)

        logger.debug(f'display: {display}')

    # sort displays to list them from left to right
    # leftmost display has index 0
    displays = sorted(displays, key=itemgetter(['rectangle'][0]))

    hsh = get_hash(displays)
    logger.debug(f'current screen layout: {displays}')
    logger.debug(f'current screen layout hash: {hsh}')
    return {'screens' : displays, 'hash' : hsh}


def move_window(hwnd, rect):
    wgui.MoveWindow(hwnd, rect[0], rect[1],
                    rect[2] - rect[0], rect[3] - rect[1], True)


def callback(hwnd, callback_param):
    pid = wproc.GetWindowThreadProcessId(hwnd)[1]
    if pid:
        text = wgui.GetWindowText(hwnd)
        if text:
            style = wapi.GetWindowLong(hwnd, wcon.GWL_STYLE)
            if style & wcon.WS_VISIBLE:
                include = True
                if wgui.IsIconic(hwnd):
                    if callback_param["prefs"]["restore_minimized"]:
                        wgui.ShowWindow(hwnd, 9)
                    else:
                        include = False

                if include:
                    rect = wgui.GetWindowRect(hwnd)
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]

                    if width > 1 and height > 1:
                        try:
                            proc = wapi.OpenProcess(wcon.PROCESS_ALL_ACCESS, 0, pid)
                            executable_path = wproc.GetModuleFileNameEx(proc, None)
                            process_name = os.path.basename(executable_path)

                            callback_param['windows_dict'].update({hwnd: {}})
                            callback_param['windows_dict'][hwnd].update({'pid' : pid})
                            callback_param['windows_dict'][hwnd].update({'process_name' : process_name})
                            callback_param['windows_dict'][hwnd].update({'executable_path' : executable_path})
                            callback_param['windows_dict'][hwnd].update({'window_title' : text})

                            display_index = get_display_index(callback_param['screens'], rect)
                            display_orientation = callback_param['screens'][display_index]['orientation']
                            display_primary = callback_param['screens'][display_index]['primary']
                            callback_param['windows_dict'][hwnd].update({'display_index': display_index})
                            callback_param['windows_dict'][hwnd].update({'display_orientation': display_orientation})
                            callback_param['windows_dict'][hwnd].update({'display_primary': display_primary})

                            move = False
                            if callback_param["prefs"]["snap_to_grid"]:
                                rect = adjust_rect_to_grid(rect)
                                move = True
                            if callback_param["prefs"]["fit_into_screen"]:
                                rect = fit_rect_into_screen(rect, callback_param["screens"][display_index]['rectangle'])
                                move = True
                            if move:
                                move_window(hwnd, rect)
                            callback_param['windows_dict'][hwnd].update({'window_rectangle': rect})

                            logger.debug(f'window: {hwnd}: {callback_param["windows_dict"][hwnd]}')
                        except:
                            pass

                        try:
                            wapi.CloseHandle(proc)
                        except:
                            pass


def enum_opened_windows(screens, prefs):
    callback_param = {'screens' : screens}
    callback_param.update({'windows_dict' : {}})
    callback_param.update({'prefs' : prefs})
    wgui.EnumWindows(callback, callback_param)
    return callback_param['windows_dict']



##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
