# ###################
# Licensed under the MIT license. See LICENSE
# ###################

import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt5.QtWidgets import *

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)
        
class DV_Menu(object):
    def create_menu(self):
        # Create menus
        self.menu_top = self.menuBar()
        self.menu_top.setNativeMenuBar(False)

        self.menu = QMenu(self.menu_top)
        self.menu.setTitle("&File")

        self.help_menu = QMenu(self.menu_top)
        self.help_menu.setTitle("&Help")

        # Menu actions
        quit_action = self.menu_create_action("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close the application")

        about_action = self.menu_create_action("&About",
            shortcut='F1', slot=self.on_about,
            tip='About the demo')

        about_action2 = self.menu_create_action("&About2",
            shortcut='F2', slot=self.on_about,
            tip='About the demo')

        # Add actions to menus
        self.menu.addAction(quit_action)

        self.help_menu.addAction(about_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(about_action2)


        # Add menus to top menu
        self.menu_top.addAction(self.menu.menuAction())
        self.menu_top.addAction(self.help_menu.menuAction())


    def on_about(self):
        msg = """ PyQt4 GUI data-viewer for internal MOSDEF data products
        """
        QMessageBox.about(self, "About the MOSDEF DV", msg.strip())

    def menu_add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def menu_create_action(self, text, slot=None, shortcut=None,
                        icon=None, tip=None, checkable=False,
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/{}.png".format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def create_menu_complicated(self, MainWindow):
        ### Slightly modified from code at
        ###     https://github.com/pythonthusiast/CrossPlatformQt
        MainWindow.setObjectName("MainWindow")
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralWidget = QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        
        MainWindow.setCentralWidget(self.centralWidget)
        
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setNativeMenuBar(False)
        self.menuBar.setObjectName("menuBar")
        
        self.menu_File = QMenu(self.menuBar)
        self.menu_File.setObjectName("menu_File")
        
        self.menu_Help = QMenu(self.menuBar)
        self.menu_Help.setObjectName("menu_Help")
        
        MainWindow.setMenuBar(self.menuBar)
        
        self.actionE_xit = QAction(MainWindow)
        self.actionE_xit.setMenuRole(QAction.ApplicationSpecificRole)
        self.actionE_xit.setShortcut("Ctrl+Q")
        self.actionE_xit.setObjectName("actionE_xit")
        
        self.action_About = QAction(MainWindow)
        self.action_About.setMenuRole(QAction.AboutRole)
        self.action_About.setShortcut("F1")
        self.action_About.setObjectName("action_About")
        
        self.menu_File.addAction(self.actionE_xit)
        self.menu_Help.addAction(self.action_About)
        
        self.menuBar.addAction(self.menu_File.menuAction())
        self.menuBar.addAction(self.menu_Help.menuAction())
        
        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
        
        # self.actionE_xit.triggered.connect(self.onExit)
        self.action_About.triggered.connect(self.on_about)
        
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.menu_File.setTitle(_translate("MainWindow", "&File", None))
        self.menu_Help.setTitle(_translate("MainWindow", "&Help", None))
        self.actionE_xit.setText(_translate("MainWindow", "E&xit", None))
        self.action_About.setText(_translate("MainWindow", "&About", None))
