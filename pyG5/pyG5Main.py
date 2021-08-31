"""
Created on 8 Aug 2021.

@author: Ben Lauret
"""

__version__ = "0.0.1beta4"
__appName__ = "pyG5"

import argparse
import logging
import platform
import sys


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
)

from pyG5.pyG5Network import pyG5NetWorkManager
from pyG5.pyG5View import pyG5DualStack


class pyG5App(QApplication):
    """pyG5App PyQt5 application.

    Args:
        sys.argv

    Returns:
        self
    """

    def __init__(self):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QApplication.__init__(self, sys.argv)

        # parse the command line arguments
        self.argument_parser()

        # set the verbosity
        if self.args.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        logging.info("{} v{}".format(self.__class__.__name__, __version__))

        self.networkManager = pyG5NetWorkManager()

        # The QWidget widget is the base class of all user interface objects in PyQt4.
        self.mainWindow = pyG5MainWindow()

        self.networkManager.drefUpdate.connect(
            self.mainWindow.pyG5DualStacked.pyG5AI.drefHandler
        )
        self.networkManager.drefUpdate.connect(
            self.mainWindow.pyG5DualStacked.pyG5HSI.drefHandler
        )

        # Show window
        # full screen for the RPI
        if platform.machine() in "armv7l":
            self.mainWindow.showFullScreen()
        else:
            self.mainWindow.show()

    def argument_parser(self):
        """Initialize the arguments passed from the command line."""
        self.parser = argparse.ArgumentParser(
            description="{} Application v{}".format(__appName__, __version__)
        )
        self.parser.add_argument(
            "-v", "--verbose", help="increase verbosity", action="store_true"
        )
        self.args = self.parser.parse_args()


class pyG5MainWindow(QMainWindow):
    """pyG5App PyQt5 application.

    Args:
        sys.argv

    Returns:
        self
    """

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QMainWindow.__init__(self, parent)

        self.setStyleSheet("background-color: black;")

        target = "FreeSans"

        if target in QFontDatabase().families():
            print("set font")
            font = QFont(target)
            self.setFont(font)

        self.setWindowTitle(__appName__)

        self.file_menu = QMenu("&File", self)
        self.file_menu.addAction("&Quit", self.close, Qt.CTRL + Qt.Key_W)
        self.file_menu.setStyleSheet("color : white;background: transparent;")

        menuBar = self.menuBar()
        menuBar.addMenu(self.file_menu)
        menuBar.setStyleSheet(
            """QMenuBar::item { color : white; background: transparent; }"""
        )

        self.pyG5DualStacked = pyG5DualStack()

        self.setCentralWidget(self.pyG5DualStacked)


if __name__ == "__main__":
    """Main application."""
    a = pyG5App()

    sys.exit(a.exec_())

    pass
