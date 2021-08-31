"""
Created on 8 Aug 2021.

@author: Ben Lauret
"""

import logging
import struct
import binascii

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer

from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QAbstractSocket


class pyG5NetWorkManager(QObject):
    """pyG5NetWorkManager Object.

    This object listen on the XPlane multicast group
    and emit on the xpInstance signal the host address
    and port of the Xplane on the network

    Args:
        parent: Parent Widget

    Returns:
        self
    """

    xpInstance = pyqtSignal(QHostAddress, int)
    drefUpdate = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Object constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QObject.__init__(self, parent)

        # list the datarefs to request
        self.datarefs = [
            # ( dataref, frequency, unit, description, num decimals to display in formatted output )
            (
                "sim/cockpit/radios/nav1_vdef_dot",
                30,
                "Dots",
                "NAV1 Vertical deviation in dots",
                0,
                "_nav1gs",
            ),
            (
                "sim/cockpit/radios/nav2_vdef_dot",
                30,
                "Dots",
                "NAV2 Vertical deviation in dots",
                0,
                "_nav2gs",
            ),
            (
                "sim/cockpit/radios/gps_vdef_dot",
                30,
                "Dots",
                "GPS Vertical deviation in dots",
                0,
                "_gpsgs",
            ),
            (
                "sim/cockpit/radios/nav1_CDI",
                30,
                "Gs",
                "Nav 1 GS available",
                0,
                "_nav1gsavailable",
            ),
            (
                "sim/cockpit/radios/nav2_CDI",
                30,
                "Gs",
                "Nav 2 GS available",
                0,
                "_nav2gsavailable",
            ),
            (
                "sim/cockpit/radios/gps_has_glideslope",
                30,
                "Gs",
                "GPS GS available",
                0,
                "_gspgsavailable",
            ),
            (
                "sim/cockpit2/gauges/indicators/airspeed_acceleration_kts_sec_pilot",
                30,
                "Gs",
                "GPS CRS",
                0,
                "_kiasDelta",
            ),
            (
                "sim/cockpit2/radios/actuators/HSI_source_select_pilot",
                30,
                "°",
                "GPS CRS",
                0,
                "_hsiSource",
            ),
            (
                "sim/cockpit/radios/nav1_fromto",
                30,
                "°",
                "NAV1 CRS",
                0,
                "_nav1fromto",
            ),
            (
                "sim/cockpit/radios/nav2_fromto",
                30,
                "°",
                "NAV2 CRS",
                0,
                "_nav2fromto",
            ),
            (
                "sim/cockpit/radios/gps_fromto",
                30,
                "°",
                "NAV2 CRS",
                0,
                "_gpsfromto",
            ),
            (
                "sim/cockpit/radios/nav1_course_degm",
                30,
                "°",
                "NAV1 CRS",
                0,
                "_nav1crs",
            ),
            (
                "sim/cockpit/radios/nav2_course_degm",
                30,
                "°",
                "NAV2 CRS",
                0,
                "_nav2crs",
            ),
            (
                "sim/cockpit/radios/gps_course_degtm",
                30,
                "°",
                "GPS CRS",
                0,
                "_gpscrs",
            ),
            (
                "sim/cockpit/radios/gps_course_degtm",
                30,
                "°",
                "GPS CRS",
                0,
                "_nav1dev",
            ),
            (
                "sim/cockpit/radios/nav1_hdef_dot",
                30,
                "°",
                "NAV1 VOR coursedeflection",
                0,
                "_nav1dft",
            ),
            (
                "sim/cockpit/radios/nav2_hdef_dot",
                30,
                "°",
                "NAV1 VOR course deflection",
                0,
                "_nav2dft",
            ),
            (
                "sim/cockpit/radios/gps_hdef_dot",
                30,
                "°",
                "GPS course deflection",
                0,
                "_gpsdft",
            ),
            (
                "sim/flightmodel/position/magnetic_variation",
                30,
                "°",
                "Ground track heading",
                0,
                "_magneticVariation",
            ),
            (
                "sim/cockpit2/gauges/indicators/ground_track_mag_pilot",
                30,
                "°",
                "Ground track heading",
                0,
                "_groundTrack",
            ),
            (
                "sim/cockpit/autopilot/heading_mag",
                30,
                "°",
                "Horizontal Situation Indicator bug",
                0,
                "_headingBug",
            ),
            (
                "sim/weather/wind_direction_degt",
                30,
                "°",
                "The effective direction of the wind at the plane's location",
                0,
                "_windDirection",
            ),
            (
                "sim/weather/wind_speed_kt",
                30,
                "kt",
                "The effective speed of the wind at the plane's location.",
                0,
                "_windSpeed",
            ),
            (
                "sim/flightmodel/position/mag_psi",
                30,
                "°",
                "Magnetic heading of the aircraft",
                0,
                "_magHeading",
            ),
            (
                "sim/flightmodel/position/phi",
                30,
                "°",
                "Roll of the aircraft",
                0,
                "_rollAngle",
            ),
            (
                "sim/flightmodel/position/theta",
                30,
                "°",
                "Pitch of the aircraft",
                0,
                "_pitchAngle",
            ),
            (
                "sim/flightmodel/position/indicated_airspeed",
                30,
                "kt",
                "Indicated airpseed",
                0,
                "_kias",
            ),
            (
                "sim/cockpit2/gauges/indicators/true_airspeed_kts_pilot",
                30,
                "kt",
                "Indicated airpseed",
                0,
                "_ktas",
            ),
            (
                "sim/flightmodel/position/groundspeed",
                30,
                "kt",
                "Indicated airpseed",
                0,
                "_gs",
            ),
            (
                "sim/cockpit2/gauges/indicators/altitude_ft_pilot",
                30,
                "feet",
                "Altitude",
                0,
                "_altitude",
            ),
            (
                "sim/cockpit2/gauges/actuators/barometer_setting_in_hg_pilot",
                30,
                "feet",
                "Altimeter setting",
                0,
                "_alt_setting",
            ),
            (
                "sim/cockpit2/gauges/indicators/slip_deg",
                30,
                "°",
                "Slip angle",
                0,
                "_slip",
            ),
            (
                "sim/cockpit2/gauges/indicators/turn_rate_heading_deg_copilot",
                30,
                "°",
                "Turn Rate",
                0,
                "_turnRate",
            ),
            (
                "sim/flightmodel/position/vh_ind_fpm",
                30,
                "kt",
                "Indicated airpseed",
                0,
                "_vh_ind_fpm",
            ),
            (
                "sim/aircraft/view/acf_Vso",
                1,
                "kt",
                "stall speed",
                0,
                "_vs0",
            ),
            (
                "sim/aircraft/view/acf_Vs",
                1,
                "kt",
                "stall in Landing configuration speed",
                0,
                "_vs",
            ),
            (
                "sim/aircraft/view/acf_Vfe",
                1,
                "kt",
                "flap extended speed",
                0,
                "_vfe",
            ),
            (
                "sim/aircraft/view/acf_Vno",
                1,
                "kt",
                "normal operation speed",
                0,
                "_vno",
            ),
            (
                "sim/aircraft/view/acf_Vne",
                1,
                "kt",
                "never exceed speed",
                0,
                "_vne",
            ),
        ]

        self.logger = logging.getLogger(self.__class__.__name__)

        # Idle timer trigger reconnection
        self.idleTimerDuration = 10000
        self.idleTimer = QTimer()
        self.idleTimer.timeout.connect(self.reconnect)

        # Create local UDP socket
        self.udpSock = QUdpSocket(self)

        # manage received data
        self.udpSock.readyRead.connect(self.dataHandler)

        # manage stage change to send data request
        self.udpSock.stateChanged.connect(self.socketStateHandler)

        # bind the socket
        self.udpSock.bind(QHostAddress.AnyIPv4)

    @pyqtSlot()
    def reconnect(self):
        """Idle timer expired. Trigger reconnection process."""
        self.logger.info("Connection Timeout expired")

        self.udpSock.close()

    @pyqtSlot(QHostAddress, int)
    def xplaneConnect(self, addr, port):
        """Slot connecting triggering the connection to the XPlane."""
        # initiate connection
        for idx, dataref in enumerate(self.datarefs):
            cmd = b"RREF\x00"  # RREF command
            freq = dataref[1]
            ref = dataref[0].encode()
            message = struct.pack("<5sii400s", cmd, freq, idx, ref)
            self.logger.info("Request datatefs: {}".format(ref))
            assert len(message) == 413
            self.udpSock.writeDatagram(message, addr, port)

        # start the idle timer
        self.idleTimer.start(self.idleTimerDuration)

    @pyqtSlot()
    def socketStateHandler(self):
        """Socket State handler."""
        self.logger.info("socketStateHandler: {}".format(self.udpSock.state()))

        if self.udpSock.state() == QAbstractSocket.BoundState:
            self.logger.info("Started Multicast listenner")
            # instantiate the multicast listener
            self.listener = pyG5MulticastListener(self)

            # connect the multicast listenner to the connect function
            self.listener.xpInstance.connect(self.xplaneConnect)

        elif self.udpSock.state() == QAbstractSocket.UnconnectedState:
            # socket got disconnected issue reconnection
            self.udpSock.bind(QHostAddress.AnyIPv4)

    @pyqtSlot()
    def dataHandler(self):
        """dataHandler."""
        # data received restart the idle timer
        self.idleTimer.start(self.idleTimerDuration)

        while self.udpSock.hasPendingDatagrams():
            datagram = self.udpSock.receiveDatagram()
            data = datagram.data()
            retvalues = {}
            # Read the Header "RREFO".
            header = data[0:5]
            if header != b"RREF,":
                self.logger.error("Unknown packet: ", binascii.hexlify(data))
            else:
                # We get 8 bytes for every dataref sent:
                #    An integer for idx and the float value.
                values = data[5:]
                lenvalue = 8
                numvalues = int(len(values) / lenvalue)
                idx = 0
                value = 0
                for i in range(0, numvalues):
                    singledata = data[(5 + lenvalue * i) : (5 + lenvalue * (i + 1))]
                    (idx, value) = struct.unpack("<if", singledata)
                    retvalues[idx] = (
                        value,
                        self.datarefs[idx][1],
                        self.datarefs[idx][0],
                        self.datarefs[idx][5],
                    )
                self.drefUpdate.emit(retvalues)


class pyG5MulticastListener(QObject):
    """pyG5MulticastListener Object.

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
        self.logger.debug("Sock new state: {}".format(state))

    @pyqtSlot()
    def connectedSlot(self):
        """connectedSlot."""
        self.logger.debug("udp connected: {}".format(self.udpSock.state()))

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
