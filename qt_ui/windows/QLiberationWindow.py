from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QMenuBar, QMainWindow, QAction, QToolBar
import webbrowser

from qt_ui.uiconstants import URLS
from qt_ui.windows.QLiberationMap import QLiberationMap
import qt_ui.uiconstants as CONST

class QLiberationWindow(QMainWindow):

    def __init__(self):
        super(QLiberationWindow, self).__init__()
        self.init_ui()

    def init_ui(self):

        self.setGeometry(300, 100, 270, 100)
        self.setWindowTitle("DCS Liberation")
        self.setWindowIcon(QIcon("../resources/icon.png"))
        self.statusBar().showMessage('Ready')
        self.init_menubar()
        self.init_toolbar()

        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        """hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)"""

        self.liberation_map = QLiberationMap()

        hbox.addWidget(self.liberation_map)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)


    def init_toolbar(self):
        self.tool_bar = self.addToolBar("File")
        self.tool_bar.addAction(QIcon(CONST.ICONS["New"]), "New")
        self.tool_bar.addAction(QIcon(CONST.ICONS["Open"]), "Open")
        self.tool_bar.addAction(QIcon(CONST.ICONS["Save"]), "Save")


    def init_menubar(self):
        self.menu = self.menuBar()

        file_menu = self.menu.addMenu("File")
        file_menu.addAction(QIcon(CONST.ICONS["New"]), "New Game")
        file_menu.addAction(QIcon(CONST.ICONS["Open"]), "Open")
        file_menu.addAction(QIcon(CONST.ICONS["Save"]), "Save")
        file_menu.addAction("Save As")

        help_menu = self.menu.addMenu("Help")
        help_menu.addAction("Online Manual", lambda: webbrowser.open_new_tab(URLS["Manual"]))
        help_menu.addAction("Troubleshooting Guide", lambda: webbrowser.open_new_tab(URLS["Troubleshooting"]))
        help_menu.addAction("Modding Guide", lambda: webbrowser.open_new_tab(URLS["Modding"]))
        help_menu.addSeparator()
        help_menu.addAction("Contribute", lambda: webbrowser.open_new_tab(URLS["Repository"]))
        help_menu.addAction("Forum Thread", lambda: webbrowser.open_new_tab(URLS["ForumThread"]))
        help_menu.addAction("Report an issue", lambda: webbrowser.open_new_tab(URLS["Issues"]))

        displayMenu = self.menu.addMenu("Display")

        tg_cp_visibility = QAction('Control Point', displayMenu)
        tg_cp_visibility.setCheckable(True)
        tg_cp_visibility.setChecked(True)
        tg_cp_visibility.toggled.connect(lambda: QLiberationMap.set_display_rule("cp", tg_cp_visibility.isChecked()))

        tg_go_visibility = QAction('Ground Objects', displayMenu)
        tg_go_visibility.setCheckable(True)
        tg_go_visibility.setChecked(True)
        tg_go_visibility.toggled.connect(lambda: QLiberationMap.set_display_rule("go", tg_go_visibility.isChecked()))

        tg_line_visibility = QAction('Lines', displayMenu)
        tg_line_visibility.setCheckable(True)
        tg_line_visibility.setChecked(True)
        tg_line_visibility.toggled.connect(lambda: QLiberationMap.set_display_rule("lines", tg_line_visibility.isChecked()))

        displayMenu.addAction(tg_go_visibility)
        displayMenu.addAction(tg_cp_visibility)
        displayMenu.addAction(tg_line_visibility)