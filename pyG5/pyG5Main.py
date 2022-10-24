"""
Created on 8 Aug 2021.

@author: Ben Lauret
"""

__version__ = "0.0.2"
__appName__ = "pyG5"

import argparse
import logging
import sys
import platform


from PyQt5.QtCore import (
    Qt,
    QTimer,
    QCoreApplication,
    QSettings,
    pyqtSlot,
    QByteArray,
    pyqtSignal,
)
from PyQt5.QtGui import QFont, QFontDatabase, QCloseEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QAction,
)

from PyQt5.Qt import QEvent
from pyG5.pyG5Network import pyG5NetWorkManager
from pyG5.pyG5View import pyG5DualStack, pyG5SecondaryWidget


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

        QCoreApplication.setOrganizationName("pyG5")
        QCoreApplication.setOrganizationDomain("pyg5.org")
        QCoreApplication.setApplicationName("pyG5")
        self.settings = QSettings(
            QSettings.IniFormat,
            QSettings.UserScope,
            QCoreApplication.organizationDomain(),
            "pyG5",
        )

        # parse the command line arguments
        self.argument_parser()

        # set the verbosity
        if self.args.verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        logging.info("{} v{}".format(self.__class__.__name__, __version__))

        self.networkManager = pyG5NetWorkManager()

        self.paintTimer = QTimer()
        self.paintTimer.timeout.connect(
            self.painTimerCB
        )  # Let the interpreter run each 500 ms.
        self.paintTimer.start(25)  # You may change this if you wish.

        # The QWidget widget is the base class of all user interface objects in PyQt4.
        self.mainWindow = pyG5MainWindow()

        self.networkManager.drefUpdate.connect(
            self.mainWindow.pyG5DualStacked.pyG5AI.drefHandler
        )
        self.networkManager.drefUpdate.connect(
            self.mainWindow.pyG5DualStacked.pyG5HSI.drefHandler
        )

        # Show window
        self.mainWindow.loadSettings()

        if platform.machine() in "armv7l":

            self.mainWindow.setWindowFlags(
                self.mainWindow.windowFlags() | Qt.FramelessWindowHint
            )

        self.mainWindow.show()

        self.secondaryWindow = pyG5SecondWindow()
        if platform.machine() in "armv7l":
            self.secondaryWindow.setWindowFlags(
                self.secondaryWindow.windowFlags() | Qt.FramelessWindowHint
            )

        self.networkManager.drefUpdate.connect(self.secondaryWindow.cWidget.drefHandler)

        self.secondaryWindow.loadSettings()

        self.secondaryWindow.show()

        self.mainWindow.closed.connect(self.secondaryWindow.close)
        self.secondaryWindow.closed.connect(self.mainWindow.close)

    def painTimerCB(self):
        """Trigger update of all the widgets."""
        self.mainWindow.pyG5DualStacked.pyG5HSI.update()
        self.mainWindow.pyG5DualStacked.update()
        self.secondaryWindow.cWidget.update()

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

    closed = pyqtSignal()

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QMainWindow.__init__(self, parent)

        self.settings = QCoreApplication.instance().settings

        self.setStyleSheet("background-color: black;")

        target = "FreeSans"

        if target in QFontDatabase().families():
            print("set font")
            font = QFont(target)
            self.setFont(font)

        self.setWindowTitle(__appName__)
        action = QAction("&Quit", self)
        action.setShortcut(Qt.CTRL + Qt.Key_W)
        action.triggered.connect(self.close)
        self.addAction(action)

        self.pyG5DualStacked = pyG5DualStack()

        self.setCentralWidget(self.pyG5DualStacked)

    def changeEvent(self, event):
        """Window change event overload.

        Args:
            event

        Returns:
            self
        """
        if QEvent.ActivationChange == event.type():
            self.settings.setValue("mainWindow/windowState", self.saveState())
        elif QEvent.WindowStateChange == event.type():
            if Qt.WindowMinimized != self.windowState():
                try:
                    self.restoreState(self.settings.value("mainWindow/windowState"))
                except Exception as inst:
                    logging.warning("State restore: {}".format(inst))
                    pass

    def loadSettings(self):
        """Load settings helper."""
        try:
            self.restoreGeometry(
                self.settings.value("mainWindow/geometry", QByteArray())
            )
            self.restoreState(self.settings.value("mainWindow/windowState"))
        except Exception as inst:
            logging.warning("State restore: {}".format(inst))
            pass

    @pyqtSlot(QCloseEvent)
    def closeEvent(self, event):
        """Close event overload.

        Args:
            event

        Returns:
            self
        """
        self.settings.setValue("mainWindow/geometry", self.saveGeometry())
        self.settings.setValue("mainWindow/windowState", self.saveState())
        event.accept()
        self.closed.emit()
        QMainWindow.closeEvent(self, event)


class pyG5SecondWindow(QMainWindow):
    """pyG5App PyQt5 application.

    Args:
        sys.argv

    Returns:
        self
    """

    closed = pyqtSignal()

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QMainWindow.__init__(self, parent)

        self.settings = QCoreApplication.instance().settings

        self.setStyleSheet("background-color: black;")

        target = "FreeSans"

        if target in QFontDatabase().families():
            print("set font")
            font = QFont(target)
            self.setFont(font)

        self.setWindowTitle(__appName__)

        self.cWidget = pyG5SecondaryWidget()

        self.setCentralWidget(self.cWidget)

        action = QAction("&Quit", self)
        action.setShortcut(Qt.CTRL + Qt.Key_W)
        action.triggered.connect(self.close)
        self.addAction(action)

    def changeEvent(self, event):
        """Window change event overload.

        Args:
            event

        Returns:
            self
        """
        if QEvent.ActivationChange == event.type():
            self.settings.setValue("secWindow/secWindowState", self.saveState())
        elif QEvent.WindowStateChange == event.type():
            if Qt.WindowMinimized != self.windowState():
                try:
                    self.restoreState(self.settings.value("secWindow/secWindowState"))
                except Exception as inst:
                    logging.warning("State restore: {}".format(inst))
                    pass

    def loadSettings(self):
        """Load settings helper."""
        try:
            self.restoreGeometry(
                self.settings.value("secWindow/geometry", QByteArray())
            )
            self.restoreState(self.settings.value("secWindow/secWindowState"))
        except Exception as inst:
            logging.warning("State restore: {}".format(inst))
            pass

    @pyqtSlot(QCloseEvent)
    def closeEvent(self, event):
        """Close event overload.

        Args:
            event

        Returns:
            self
        """
        self.settings.setValue("secWindow/geometry", self.saveGeometry())
        self.settings.setValue("secWindow/secWindowState", self.saveState())
        event.accept()
        self.closed.emit()
        QMainWindow.closeEvent(self, event)


if __name__ == "__main__":
    """Main application."""
    a = pyG5App()

    sys.exit(a.exec_())

    pass
