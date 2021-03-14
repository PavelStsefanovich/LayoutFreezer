import logging
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextBrowser,
    QVBoxLayout)
import re
import sys


##########  Global Properties  ####################

logger = logging.getLogger(__name__)

# @PavelStsefanovich:
# because html_template contains placeholders, it is embedded into the source
# to prevent potential failure due to modifications by user

html_template = '''
<html>
<head>
<style type="text/css">
  body {
    font-size: 90%;
    background-color: #ffffee;
  }
  h3 {
    color: #4169e1;
  }
</style>
</head>
<body>
<h3>{{product_name}} v{{version}}</h3>
<p>Home page: <a href="{{home_page}}"><i>{{home_page}}</i></a></p>
<hr>
<h5>User Data:</h5>
<p><b>Database:</b> {{database_path}}</p>
<p><b>Peferences:</b> {{preferences_path}}</p>
<h5>Installation:</h5>
<p><b>App directory:</b> {{install_dir}}</p>
<p><b>Logs directory:</b> {{logs_dir}}</p>
</body>
</html>
'''

hotkeys_statusbar_map = {
  True : {
    'text' : "To update a hotkey, type in a string in the format: \"<ctrl>+<alt>[+<shift>]+x\" and hit Enter",
    'style' : "padding: 5px; font-family: arial; color: #4169e1;"
  },
  False : {
    'text' : "\n ",
    'style' : "padding: 5px; font-family: arial;"
  }
}


##########  Classes  ##############################

class About(QDialog):

    def __init__(self, config):
        super().__init__()
        self.config = config

        # info panel
        about_html = self.generate_about_html(html_template)
        self.about = QTextBrowser()
        self.about.setOpenExternalLinks(True)
        self.about.setMinimumSize(400, 260)
        self.about.setHtml(about_html)

        # widgets
        self.clipboard = QClipboard(self)
        self.status_bar = QLabel()
        copy_button = QPushButton("Copy")
        copy_button.setMaximumWidth(75)
        copy_button.clicked.connect(self.copy_to_clipboard)
        close_button = QPushButton("Close")
        close_button.setMaximumWidth(75)
        close_button.clicked.connect(self.close)

        # layoyut
        clipboard_layout = QHBoxLayout()
        clipboard_layout.addWidget(self.status_bar)
        clipboard_layout.addWidget(copy_button)
        clipboard_layout.addWidget(close_button)

        # Create main layout and add widgets
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.about)
        main_layout.addLayout(clipboard_layout)
        self.setLayout(main_layout)


    def generate_about_html(self, html_template):
        html = html_template
        html = html.replace('{{product_name}}',     self.config["product_name"])
        html = html.replace('{{version}}',          self.config["version"])
        html = html.replace('{{home_page}}',        self.config["home_page"])
        html = html.replace('{{database_path}}',    self.config["database_path"])
        html = html.replace('{{preferences_path}}', self.config["preferences_path"])
        html = html.replace('{{install_dir}}',      self.config["install_dir"])
        html = html.replace('{{logs_dir}}',         self.config["logs_dir"])
        return html


    def copy_to_clipboard(self):
        logger.debug('copying text from "About" dialog into clipboard')
        self.clipboard.setText(self.about.toPlainText())
        self.status_bar.setText("Copied into clipboard")
        self.status_bar.setStyleSheet("font-family: arial; color: #4169e1;")


class Preferences(QDialog):

    def __init__(self, prefs):
        super().__init__()
        self.prefs = prefs
        self.hotkey_format_regex = r'^\<ctrl\>\+\<alt\>(\+\<shift\>)?\+[a-zA-Z0-9]$'

        # checkbox: restore minimized
        restore_minimized = QCheckBox()
        restore_minimized.setFixedWidth(35)
        restore_minimized.setChecked(self.prefs["restore_minimized"]["value"])
        restore_minimized.stateChanged.connect(
            lambda: self.restore_minimized(restore_minimized.isChecked()))
        restore_minimized_descr = QLabel(self.prefs["restore_minimized"]["description"])
        restore_minimized_descr.setWordWrap(True)

        restore_minimized_layout = QHBoxLayout()
        restore_minimized_layout.addWidget(restore_minimized)
        restore_minimized_layout.addWidget(restore_minimized_descr)

        restore_minimized_groupbox = QGroupBox("Restore Minimized")
        restore_minimized_groupbox.setLayout(restore_minimized_layout)

        # checkbox: snap to grid
        snap_to_grid = QCheckBox()
        snap_to_grid.setFixedWidth(35)
        snap_to_grid.setChecked(self.prefs["snap_to_grid"]["value"])
        snap_to_grid.stateChanged.connect(
            lambda: self.snap_to_grid(snap_to_grid.isChecked()))
        snap_to_grid_descr = QLabel(
            self.prefs["snap_to_grid"]["description"])
        snap_to_grid_descr.setWordWrap(True)

        snap_to_grid_layout = QHBoxLayout()
        snap_to_grid_layout.addWidget(snap_to_grid)
        snap_to_grid_layout.addWidget(snap_to_grid_descr)

        snap_to_grid_groupbox = QGroupBox("Snap To Grid")
        snap_to_grid_groupbox.setLayout(snap_to_grid_layout)

        # checkbox: fit into screen
        fit_into_screen = QCheckBox()
        fit_into_screen.setFixedWidth(35)
        fit_into_screen.setChecked(self.prefs["fit_into_screen"]["value"])
        fit_into_screen.stateChanged.connect(
            lambda: self.fit_into_screen(fit_into_screen.isChecked()))
        fit_into_screen_descr = QLabel(
            self.prefs["fit_into_screen"]["description"])
        fit_into_screen_descr.setWordWrap(True)

        fit_into_screen_layout = QHBoxLayout()
        fit_into_screen_layout.addWidget(fit_into_screen)
        fit_into_screen_layout.addWidget(fit_into_screen_descr)

        fit_into_screen_groupbox = QGroupBox("Fit Into Screen")
        fit_into_screen_groupbox.setLayout(fit_into_screen_layout)

        # doublespinBox: match cutoff
        match_cutoff = QDoubleSpinBox()
        match_cutoff.setFixedWidth(35)
        match_cutoff.setValue(self.prefs["match_cutoff"]["value"])
        match_cutoff.setRange(0.1, 1.0)
        match_cutoff.setSingleStep(0.1)
        match_cutoff.setDecimals(1)
        match_cutoff.valueChanged.connect(
            lambda: self.match_cutoff(match_cutoff.value()))
        match_cutoff_descr = QLabel(
            self.prefs["match_cutoff"]["description"])
        match_cutoff_descr.setWordWrap(True)

        match_cutoff_layout = QHBoxLayout()
        match_cutoff_layout.addWidget(match_cutoff)
        match_cutoff_layout.addWidget(match_cutoff_descr)

        match_cutoff_groupbox = QGroupBox("Match Cutoff")
        match_cutoff_groupbox.setLayout(match_cutoff_layout)

        # checkbox: enable hotkeys
        enable_hotkeys = QCheckBox()
        enable_hotkeys.setFixedWidth(35)
        enable_hotkeys.setChecked(self.prefs["enable_hotkeys"]["value"])
        enable_hotkeys.stateChanged.connect(
            lambda: self.enable_hotkeys(enable_hotkeys.isChecked()))
        enable_hotkeys_descr = QLabel(
            self.prefs["enable_hotkeys"]["description"])
        enable_hotkeys_descr.setWordWrap(True)

        enable_hotkeys_layout = QHBoxLayout()
        enable_hotkeys_layout.addWidget(enable_hotkeys)
        enable_hotkeys_layout.addWidget(enable_hotkeys_descr)

        # lineedit: hotkeys shortcuts
        hotkey_freeze_new_name = QLabel("Freeze New:")
        hotkey_freeze_new_name.setFixedWidth(75)
        self.hotkey_freeze_new_status = QLabel()
        self.hotkey_freeze_new = QLineEdit(self.prefs["hotkeys"]["value"]["freeze_new"])
        self.hotkey_freeze_new.setFixedWidth(140)
        self.hotkey_freeze_new.editingFinished.connect(
            lambda: self.hotkey_freeze_new_update(self.hotkey_freeze_new.text()))
        self.hotkey_freeze_new.cursorPositionChanged.connect(self.hotkey_freeze_new_status.clear)

        hotkey_freeze_new_layout = QHBoxLayout()
        hotkey_freeze_new_layout.addWidget(hotkey_freeze_new_name)
        hotkey_freeze_new_layout.addWidget(self.hotkey_freeze_new)
        hotkey_freeze_new_layout.addWidget(self.hotkey_freeze_new_status)

        hotkey_freeze_all_name = QLabel("Freeze All:")
        hotkey_freeze_all_name.setFixedWidth(75)
        self.hotkey_freeze_all_status = QLabel()
        self.hotkey_freeze_all = QLineEdit(self.prefs["hotkeys"]["value"]["freeze_all"])
        self.hotkey_freeze_all.setFixedWidth(140)
        self.hotkey_freeze_all.editingFinished.connect(
            lambda: self.hotkey_freeze_all_update(self.hotkey_freeze_all.text()))
        self.hotkey_freeze_all.cursorPositionChanged.connect(self.hotkey_freeze_all_status.clear)

        hotkey_freeze_all_layout = QHBoxLayout()
        hotkey_freeze_all_layout.addWidget(hotkey_freeze_all_name)
        hotkey_freeze_all_layout.addWidget(self.hotkey_freeze_all)
        hotkey_freeze_all_layout.addWidget(self.hotkey_freeze_all_status)

        hotkey_restore_name = QLabel("Restore:")
        hotkey_restore_name.setFixedWidth(75)
        self.hotkey_restore_status = QLabel()
        self.hotkey_restore = QLineEdit(self.prefs["hotkeys"]["value"]["restore"])
        self.hotkey_restore.setFixedWidth(140)
        self.hotkey_restore.editingFinished.connect(
            lambda: self.hotkey_restore_update(self.hotkey_restore.text()))
        self.hotkey_restore.cursorPositionChanged.connect(self.hotkey_restore_status.clear)

        hotkey_restore_layout = QHBoxLayout()
        hotkey_restore_layout.addWidget(hotkey_restore_name)
        hotkey_restore_layout.addWidget(self.hotkey_restore)
        hotkey_restore_layout.addWidget(self.hotkey_restore_status)

        self.hotkeys_statusbar = QLabel()
        self.hotkeys_statusbar.setWordWrap(True)
        self.hotkeys_statusbar.setText(hotkeys_statusbar_map[self.prefs['enable_hotkeys']['value']]['text'])
        self.hotkeys_statusbar.setStyleSheet(hotkeys_statusbar_map[self.prefs['enable_hotkeys']['value']]['style'])

        close_button = QPushButton("Close")
        close_button.setMaximumWidth(75)
        close_button.clicked.connect(self.close)

        hotkeys_statusbar_layout = QHBoxLayout()
        hotkeys_statusbar_layout.addWidget(self.hotkeys_statusbar)
        hotkeys_statusbar_layout.addWidget(close_button)

        hotkeys_layout = QVBoxLayout()
        hotkeys_layout.addLayout(hotkey_freeze_new_layout)
        hotkeys_layout.addLayout(hotkey_freeze_all_layout)
        hotkeys_layout.addLayout(hotkey_restore_layout)

        self.hotkeys_groupbox = QGroupBox()
        self.hotkeys_groupbox.setFlat(True)
        self.hotkeys_groupbox.setDisabled(not self.prefs["enable_hotkeys"]["value"])
        self.hotkeys_groupbox.setLayout(hotkeys_layout)

        enable_hotkeys_outer_layout = QVBoxLayout()
        enable_hotkeys_outer_layout.addLayout(enable_hotkeys_layout)
        enable_hotkeys_outer_layout.addWidget(self.hotkeys_groupbox)

        enable_hotkeys_groupbox = QGroupBox("Enable Hotkeys")
        enable_hotkeys_groupbox.setLayout(enable_hotkeys_outer_layout)

        # Create main layout and add widgets
        main_layout = QVBoxLayout()
        main_layout.addWidget(restore_minimized_groupbox)
        main_layout.addWidget(snap_to_grid_groupbox)
        main_layout.addWidget(fit_into_screen_groupbox)
        main_layout.addWidget(match_cutoff_groupbox)
        main_layout.addWidget(enable_hotkeys_groupbox)
        main_layout.addWidget(self.hotkeys_groupbox)
        #main_layout.addWidget(hotkeys_statusbar_groupbox)
        main_layout.addLayout(hotkeys_statusbar_layout)
        self.setLayout(main_layout)


    def restore_minimized(self, isChecked):
        print(f'restore_minimized: {isChecked}')
        self.prefs["restore_minimized"]["value"] = isChecked


    def snap_to_grid(self, isChecked):
        print(f'snap_to_grid: {isChecked}')
        self.prefs["snap_to_grid"]["value"] = isChecked


    def fit_into_screen(self, isChecked):
        print(f'fit_into_screen: {isChecked}')
        self.prefs["fit_into_screen"]["value"] = isChecked


    def match_cutoff(self, value):
        rounded_value = round(value, 1)
        print(f'match_cutoff: {rounded_value}')
        self.prefs["match_cutoff"]["value"] = rounded_value


    def enable_hotkeys(self, isChecked):
        print(f'enable_hotkeys: {isChecked}')
        self.prefs["enable_hotkeys"]["value"] = isChecked
        self.hotkeys_groupbox.setDisabled(not isChecked)
        self.hotkeys_statusbar.setText(hotkeys_statusbar_map[isChecked]['text'])
        self.hotkeys_statusbar.setStyleSheet(hotkeys_statusbar_map[isChecked]['style'])


    def hotkey_freeze_new_update(self, text):
        print(f'hotkey_freeze_new: {text}')
        if re.match(self.hotkey_format_regex, text):
            self.prefs["hotkeys"]["value"]["freeze_new"] = text
            self.hotkey_freeze_new_status.setText(f'Updated!')
            self.hotkey_freeze_new_status.setStyleSheet("color: green;")
        else:
            self.hotkey_freeze_new.setText(self.prefs["hotkeys"]["value"]["freeze_new"])
            self.hotkey_freeze_new_status.setText('Failed to update: unsupported format')
            self.hotkey_freeze_new_status.setStyleSheet("color: red;")


    def hotkey_freeze_all_update(self, text):
        print(f'hotkey_freeze_all: {text}')
        if re.match(self.hotkey_format_regex, text):
            self.prefs["hotkeys"]["value"]["freeze_all"] = text
            self.hotkey_freeze_all_status.setText(f'Updated!')
            self.hotkey_freeze_all_status.setStyleSheet("color: green;")
        else:
            self.hotkey_freeze_all.setText(self.prefs["hotkeys"]["value"]["freeze_all"])
            self.hotkey_freeze_all_status.setText('Failed to update: unsupported format')
            self.hotkey_freeze_all_status.setStyleSheet("color: red;")


    def hotkey_restore_update(self, text):
        print(f'hotkey_restore: {text}')
        if re.match(self.hotkey_format_regex, text):
            self.prefs["hotkeys"]["value"]["restore"] = text
            self.hotkey_restore_status.setText(f'Updated!')
            self.hotkey_restore_status.setStyleSheet("color: green;")
        else:
            self.hotkey_restore.setText(self.prefs["hotkeys"]["value"]["restore"])
            self.hotkey_restore_status.setText('Failed to update: unsupported format')
            self.hotkey_restore_status.setStyleSheet("color: red;")


##########  Functions  ############################

def show_critical_error_dialog(errormessage="Critical error occured (no details provided)"):
    app = QApplication(sys.argv)
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Critical)
    msgBox.setText(errormessage)
    msgBox.show()
    app.exec_()


##########  Main  #################################

if __name__ == "__main__":
    raise Exception('This module is not intended to run as __main__')
