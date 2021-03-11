import logging
from PySide2.QtGui import QClipboard
from PySide2.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextBrowser,
    QVBoxLayout)
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

        # copy button and status bar
        self.clipboard = QClipboard(self)
        self.status_bar = QLabel()
        copy_button = QPushButton("Copy")
        copy_button.setMaximumWidth(75)
        copy_button.clicked.connect(self.copy_to_clipboard)
        clipboard_layout = QHBoxLayout()
        clipboard_layout.addWidget(self.status_bar)
        clipboard_layout.addWidget(copy_button)

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


    # copy to clipboard
    def copy_to_clipboard(self):
        logger.debug('copying text from "About" dialog into clipboard')
        self.clipboard.setText(self.about.toPlainText())
        self.status_bar.setText("Copied into clipboard")



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
