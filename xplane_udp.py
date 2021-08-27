"""
Created on 8 Aug 2021.

@author: Ben Lauret
"""

import sys
import logging

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QAbstractSocket, QNetworkDatagram


class XPG5(QApplication):
    """g5Widget Constructor.

    Args:
        parent: Parent Widget

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

        datarefs = [
            # ( dataref, unit, description, num decimals to display in formatted output )
            (
                "sim/flightmodel/position/latitude",
                "°N",
                "The latitude of the aircraft",
                6,
            ),
            (
                "sim/flightmodel/position/longitude",
                "°E",
                "The longitude of the aircraft",
                6,
            ),
            ("sim/flightmodel/misc/h_ind", "ft", "", 0),
            ("sim/flightmodel/position/y_agl", "m", "AGL", 0),
            (
                "sim/flightmodel/position/mag_psi",
                "°",
                "The real magnetic heading of the aircraft",
                0,
            ),
            (
                "sim/flightmodel/position/indicated_airspeed",
                "kt",
                "Air speed indicated - this takes into account air density and wind direction",
                0,
            ),
            (
                "sim/flightmodel/position/groundspeed",
                "m/s",
                "The ground speed of the aircraft",
                0,
            ),
            ("sim/flightmodel/position/vh_ind", "m/s", "vertical velocity", 1),
        ]
        for mydata in datarefs:
            print(mydata)
        self.listener = XPMulticastListener(self)
        self.listener.xpInstance.connect(self.udpConnect)

    @pyqtSlot(QHostAddress, int)
    def udpConnect(self, addr, port):
        """Slot connecting triggering the connection to the XPlane."""
        print("Connecting to {}:{}".format(addr.toString(), port))
        self.udpSock = QUdpSocket(self)
        self.udpSock.readyRead.connect(self.udpData)
        self.udpSock.stateChanged.connect(self.requestData)
        self.udpSock.connectToHost(addr, port)
        pass

    @pyqtSlot()
    def requestData(self):
        """udpData."""
        print(self.udpSock.state())
        if self.udpSock.state() == QAbstractSocket.ConnectedState:
            print("send RREF")
            req = b"sim/flightmodel/position/phi"
            req += b"\x00" * (400 - len(req))
            self.udpSock.writeDatagram(
                QNetworkDatagram(
                    b"RREF\0" + b"\x00\x00\x00\x00" + b"\x00\x00\x00\x00" + req
                )
            )

    @pyqtSlot()
    def udpData(self):
        """udpData."""
        print("data pending")
        while self.udpSock.hasPendingDatagrams():
            datagram = self.udpSock.receiveDatagram()
            print(datagram)


class XPMulticastListener(QObject):
    """XPMulticastListener Object.

    This object listen on the XPlane multicast group
    and emit on the xpInstance signal the host address
    and port of the Xplane on the network

    Args:
        parent: Parent Widget

    Returns:
        self
    """

    xpInstance = pyqtSignal(QHostAddress, int)

    def __init__(self, parent=None):
        """Object constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QObject.__init__(self, parent)

        self.logger = logging.getLogger(self.__class__.__name__)

        self.XPAddr = QHostAddress("239.255.1.1")
        self.XPPort = 49707

        # create the socket
        self.udpSock = QUdpSocket(self)

        self.udpSock.stateChanged.connect(self.stateChangedSlot)
        self.udpSock.readyRead.connect(self.udpData)
        self.udpSock.connected.connect(self.connectedSlot)
        self.udpSock.bind(QHostAddress.AnyIPv4, port=self.XPPort)
        if not self.udpSock.joinMulticastGroup(self.XPAddr):
            logging.error("Failed to join multicast group")

    @pyqtSlot(QAbstractSocket.SocketState)
    def stateChangedSlot(self, state):
        """stateChangedSlot."""
        logging.debug("Sock new state: {}".format(state))

    @pyqtSlot()
    def connectedSlot(self):
        """connectedSlot."""
        logging.debug("udp connected: {}".format(self.udpSock.state()))

    @pyqtSlot()
    def udpData(self):
        """udpData."""
        while self.udpSock.hasPendingDatagrams():
            datagram = self.udpSock.receiveDatagram()
            if "BECN" in str(datagram.data())[2:6]:
                self.xpInstance.emit(
                    datagram.senderAddress(),
                    int.from_bytes(bytes(datagram.data())[19:21], byteorder="little"),
                )
                self.udpSock.leaveMulticastGroup(self.XPAddr)
                self.udpSock.close()
                break


if __name__ == "__main__":
    # Create an PyQT5 application object.
    a = XPG5()

    # The QWidget widget is the base class of all user interface objects in PyQt4.
    w = QMainWindow()

    w.setWindowTitle("UDP Receiver")
    file_menu = QMenu("&File", w)
    file_menu.addAction("&Quit", w.close, Qt.CTRL + Qt.Key_W)

    menuBar = w.menuBar()
    menuBar.addMenu(file_menu)

    hlayout = QHBoxLayout()
    mainWidget = QWidget()
    mainWidget.setLayout(hlayout)
    controlVLayout = QVBoxLayout()
    hlayout.addLayout(controlVLayout)

    textBox = QLabel()
    w.setCentralWidget(textBox)
    # Show window
    w.show()

    sys.exit(a.exec_())

    pass
