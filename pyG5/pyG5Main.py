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


from PySide6.QtCore import (
    Qt,
    QTimer,
    QCoreApplication,
    QSettings,
    Slot,
    QByteArray,
    Signal,
    QEvent,
)
from PySide6.QtGui import QFont, QFontDatabase, QCloseEvent, QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
)

from pyG5.pyG5Network import pyG5NetWorkManager
from pyG5.pyG5View import pyG5DualStackFMA, pyG5SecondaryWidget


class pyG5App(QApplication):
    """pyG5App PySide6 application.

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
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
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

        # The QWidget widget is the base class of all user interface objects in PySide6.
        self.mainWindow = pyG5MainWindow()

        self.networkManager.drefUpdate.connect(
            self.mainWindow.pyG5DualStacked.pyG5AI.drefHandler
        )
        self.networkManager.drefUpdate.connect(
            self.mainWindow.pyG5DualStacked.pyG5HSI.drefHandler
        )

        self.networkManager.drefUpdate.connect(
            self.mainWindow.pyG5DualStacked.pyG5FMA.drefHandler
        )

        # Show window
        self.mainWindow.loadSettings()

        if platform.machine() == "aarch64":
            self.mainWindow.setWindowFlags(
                self.mainWindow.windowFlags() | Qt.FramelessWindowHint
            )
            self.mainWindow.setWindowState(Qt.WindowFullScreen)

        self.mainWindow.show()

        if self.args.mode == "full":
            self.secondaryWindow = pyG5SecondWindow()

            self.secondaryWindow.loadSettings()

            if platform.machine() == "aarch64":
                self.secondaryWindow.setWindowFlags(
                    self.secondaryWindow.windowFlags() | Qt.FramelessWindowHint
                )

                self.secondaryWindow.setWindowState(Qt.WindowFullScreen)

            # connect the value coming from the simulator
            self.networkManager.drefUpdate.connect(
                self.secondaryWindow.cWidget.drefHandler
            )

            # connect the value to update to the simulator
            self.secondaryWindow.cWidget.xpdrCodeSignal.connect(
                self.send_transponder_code
            )
            self.secondaryWindow.cWidget.xpdrModeSignal.connect(
                self.send_transponder_mode
            )

            self.secondaryWindow.show()

            self.secondaryWindow.closed.connect(self.mainWindow.close)
            self.mainWindow.closed.connect(self.secondaryWindow.close)

    def send_transponder_code(self, code):
        """Trigger the xpdr transmission to xplane."""
        self.networkManager.write_data_ref("sim/cockpit/radios/transponder_code", code)

    def send_transponder_mode(self, mode):
        """Trigger the xpdr transmission to xplane."""
        self.networkManager.write_data_ref("sim/cockpit/radios/transponder_mode", mode)

    def painTimerCB(self):
        """Trigger update of all the widgets."""
        self.mainWindow.pyG5DualStacked.pyG5HSI.update()
        self.mainWindow.pyG5DualStacked.update()
        if self.args.mode == "full":
            self.secondaryWindow.cWidget.update()

    def argument_parser(self):
        """Initialize the arguments passed from the command line."""
        self.parser = argparse.ArgumentParser(
            description="{} Application v{}".format(__appName__, __version__)
        )
        self.parser.add_argument(
            "-v", "--verbose", help="increase verbosity", action="store_true"
        )
        self.parser.add_argument(
            "-m",
            "--mode",
            help="Define the operating mode",
            choices=[
                "hsi",
                "full",
            ],
            default="hsi",
        )

        self.args = self.parser.parse_args()


class pyG5BaseWindow(QMainWindow):
    """pyG5App PySide6 application.

    Args:
        sys.argv

    Returns:
        self
    """

    closed = Signal()

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

        if target in QFontDatabase.families():
            font = QFont(target)
            self.setFont(font)

        self.setWindowTitle(__appName__)
        action = QAction("&Quit", self)
        action.setShortcut("Ctrl+w")
        action.triggered.connect(self.close)
        self.addAction(action)

    def changeEvent(self, event):
        """Window change event overload.

        Args:
            event

        Returns:
            self
        """
        if QEvent.Type.ActivationChange == event.type():
            self.settings.setValue(
                "{}/windowState".format(self.__class__.__name__), self.saveState()
            )
        elif QEvent.Type.WindowStateChange == event.type():
            if Qt.WindowMinimized != self.windowState():
                try:
                    self.restoreState(
                        self.settings.value(
                            "{}/windowState".format(self.__class__.__name__)
                        )
                    )
                except Exception as inst:
                    logging.warning("State restore: {}".format(inst))
                    pass

    def loadSettings(self):
        """Load settings helper."""
        try:
            self.restoreGeometry(
                self.settings.value(
                    "{}/geometry".format(self.__class__.__name__), QByteArray()
                )
            )
            self.restoreState(
                self.settings.value("{}/windowState".format(self.__class__.__name__))
            )
        except Exception as inst:
            logging.warning("State restore: {}".format(inst))
            pass

    @Slot(QCloseEvent)
    def closeEvent(self, event):
        """Close event overload.

        Args:
            event

        Returns:
            self
        """
        self.settings.setValue(
            "{}/geometry".format(self.__class__.__name__), self.saveGeometry()
        )
        self.settings.setValue(
            "{}/windowState".format(self.__class__.__name__), self.saveState()
        )
        event.accept()
        self.closed.emit()
        QMainWindow.closeEvent(self, event)


class pyG5MainWindow(pyG5BaseWindow):
    """pyG5App PySide6 application.

    Args:
        sys.argv

    Returns:
        self
    """

    closed = Signal()

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        pyG5BaseWindow.__init__(self, parent)

        self.pyG5DualStacked = pyG5DualStackFMA()

        self.setCentralWidget(self.pyG5DualStacked)


class pyG5SecondWindow(pyG5BaseWindow):
    """pyG5App PyQt5 application.

    Args:
        sys.argv

    Returns:
        self
    """

    closed = Signal()

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        pyG5BaseWindow.__init__(self, parent)

        self.cWidget = pyG5SecondaryWidget()

        self.setCentralWidget(self.cWidget)


if __name__ == "__main__":
    """Main application."""
    a = pyG5App()

    sys.exit(a.exec())

    pass
