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


##########  Module Properties  ####################

logger = logging.getLogger(__name__)


##########  Functions  ############################

def get_hash(source_object):
    string_repr = str(source_object)
    return hashlib.sha1(string_repr.encode()).hexdigest()


def get_display_index(screens, win_rectangle):

    for scr_index in range(0, len(screens)):
        scr_rectangle = screens[scr_index]['rectangle']

        if win_rectangle[0] < scr_rectangle[0] or win_rectangle[0] > scr_rectangle[2]:
            continue

        if win_rectangle[1] < scr_rectangle[1] or win_rectangle[1] > scr_rectangle[3]:
            continue

        return scr_index

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


def enum_displays(qtapp):
    displays = []
    screens = qtapp.screens()

    for scr in screens:
        rect = scr.geometry().getRect()
        rectangle = [rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3]]
        display = {}
        display.update({'primary': False})
        display.update({'orientation': 'landscape'})
        display.update({'rectangle': rectangle})

        if rectangle[0] == 0 and rectangle[1] == 0:
            display['primary'] = True

        if scr.orientation() is QtCore.Qt.ScreenOrientation.PortraitOrientation:
            display['orientation'] = 'portrait'

        displays.append(display)

        logger.debug(f'Display: {display}')

    # sort displays to list them from left to right
    # (leftmost display has index 0)
    displays = sorted(displays, key=itemgetter(['rectangle'][0]))

    hsh = get_hash(displays)
    logger.debug(f'Current display layout: {displays}')
    logger.debug(f'Current display layout hash: {hsh}')
    return {'screens' : displays, 'hash' : hsh}


def move_window(hwnd, rect):
    pass


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
                        if callback_param["prefs"]["snap_to_grid"]:
                            rect = adjust_rect_to_grid(rect)

                        try:
                            proc = wapi.OpenProcess(wcon.PROCESS_ALL_ACCESS, 0, pid)
                            executable_path = wproc.GetModuleFileNameEx(proc, None)
                            process_name = os.path.basename(executable_path)

                            callback_param['windows_dict'].update({hwnd: {}})
                            callback_param['windows_dict'][hwnd].update({'pid' : pid})
                            callback_param['windows_dict'][hwnd].update({'process_name' : process_name})
                            callback_param['windows_dict'][hwnd].update({'executable_path' : executable_path})
                            callback_param['windows_dict'][hwnd].update({'window_title' : text})
                            callback_param['windows_dict'][hwnd].update({'window_rectangle': rect})

                            display_index = get_display_index(callback_param['screens'], rect)
                            display_orientation = callback_param['screens'][display_index]['orientation']
                            display_primary = callback_param['screens'][display_index]['primary']

                            callback_param['windows_dict'][hwnd].update({'display_index': display_index})
                            callback_param['windows_dict'][hwnd].update({'display_orientation': display_orientation})
                            callback_param['windows_dict'][hwnd].update({'display_primary': display_primary})

                            logger.debug(f'Window: {hwnd}: {callback_param["windows_dict"][hwnd]}')

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
