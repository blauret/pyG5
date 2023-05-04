"""
Created on 8 Aug 2021.

@author: Ben Lauret
"""

import platform
import logging
import struct
import binascii
import os
from datetime import datetime as datetime_, timedelta

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer

from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QAbstractSocket

from PyQt5 import QtGui


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

    drefUpdate = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Object constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QObject.__init__(self, parent)

        self.xpHost = None
        # list the datarefs to request
        self.datarefs = [
            # ( dataref, frequency, unit, description, num decimals to display in formatted output )
            (
                "sim/flightmodel/controls/parkbrake",
                1,
                "onoff",
                "Parking brake set",
                0,
                "_parkBrake",
            ),
            (
                "sim/cockpit/warnings/annunciators/fuel_quantity",
                1,
                "onoff",
                "fuel selector",
                0,
                "_lowFuel",
            ),
            (
                "sim/cockpit/warnings/annunciators/oil_pressure_low[0]",
                1,
                "onoff",
                "fuel selector",
                0,
                "_oilPres",
            ),
            (
                "sim/cockpit/warnings/annunciators/fuel_pressure_low[0]",
                1,
                "onoff",
                "fuel selector",
                0,
                "_fuelPress",
            ),
            (
                "sim/cockpit/warnings/annunciators/low_vacuum",
                1,
                "onoff",
                "fuel selector",
                0,
                "_lowVacuum",
            ),
            (
                "sim/cockpit/warnings/annunciators/low_voltage",
                1,
                "onoff",
                "fuel selector",
                0,
                "_lowVolts",
            ),
            (
                "sim/cockpit2/fuel/fuel_tank_selector",
                30,
                "onoff",
                "fuel selector",
                0,
                "_fuelSel",
            ),
            (
                "sim/cockpit2/engine/actuators/carb_heat_ratio[0]",
                30,
                "onoff",
                "fuel pump on",
                0,
                "_carbheat",
            ),
            (
                "sim/cockpit/engine/fuel_pump_on[0]",
                10,
                "onoff",
                "fuel pump on",
                0,
                "_fuelpump",
            ),
            (
                "sim/flightmodel/controls/elv_trim",
                30,
                "mode",
                "Transponder mode",
                0,
                "_trims",
            ),
            (
                "sim/flightmodel/controls/flaprat",
                30,
                "mode",
                "Transponder mode",
                0,
                "_flaps",
            ),
            (
                "sim/cockpit/radios/transponder_mode",
                5,
                "mode",
                "Transponder mode",
                0,
                "_xpdrMode",
            ),
            (
                "sim/cockpit/radios/transponder_code",
                5,
                "code",
                "Transponder code",
                0,
                "_xpdrCode",
            ),
            (
                "sim/cockpit/radios/gps_dme_dist_m",
                1,
                "Gs",
                "GPS GS available",
                0,
                "_gpsdmedist",
            ),
            (
                "sim/cockpit2/radios/indicators/fms_fpta_pilot",
                1,
                "Gs",
                "GPS GS available",
                0,
                "_gpsvnavavailable",
            ),
            (
                # int	n	enum	GPS CDI sensitivity: 0=OCN, 1=ENR, 2=TERM, 3=DPRT, 4=MAPR, 5=APR, 6=RNPAR, 7=LNAV, 8=LNAV+V, 9=L/VNAV, 10=LP, 11=LPV, 12=LP+V, 13=GLS
                "sim/cockpit/radios/gps_cdi_sensitivity",
                1,
                "index",
                "GPS HSI sensitivity mode",
                0,
                "_gpshsisens",
            ),
            (
                "sim/cockpit/radios/gps_has_glideslope",
                1,
                "Gs",
                "GPS GS available",
                0,
                "_gpsgsavailable",
            ),
            (
                "sim/cockpit/radios/gps_gp_mtr_per_dot",
                1,
                "boolean",
                "Avionics powered on",
                0,
                "_gpsvsens",
            ),
            (
                "sim/cockpit/radios/",
                1,
                "boolean",
                "Avionics powered on",
                0,
                "_nav1type",
            ),
            (
                "sim/cockpit/radios/nav_type[1]",
                1,
                "boolean",
                "Avionics powered on",
                0,
                "_nav2type",
            ),
            (
                "sim/cockpit/gps/destination_type",
                1,
                "boolean",
                "Avionics powered on",
                0,
                "_gpstype",
            ),
            (
                "sim/cockpit/electrical/avionics_on",
                1,
                "boolean",
                "Avionics powered on",
                0,
                "_avionicson",
            ),
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
                "sim/cockpit2/radios/indicators/nav1_flag_from_to_pilot",
                30,
                "°",
                "NAV1 CRS",
                0,
                "_nav1fromto",
            ),
            (
                "sim/cockpit2/radios/indicators/nav2_flag_from_to_pilot",
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
                "sim/cockpit/radios/nav1_obs_degm",
                30,
                "°",
                "NAV1 CRS",
                0,
                "_nav1crs",
            ),
            (
                "sim/cockpit/radios/nav2_obs_degm",
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
                "sim/cockpit2/autopilot/altitude_dial_ft",
                30,
                "feet",
                "Altitude",
                0,
                "_altitudeSel",
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
                "sim/physics/metric_press",
                1,
                "feet",
                "Altimeter setting",
                0,
                "_alt_setting_metric",
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
                "sim/cockpit2/gauges/indicators/turn_rate_heading_deg_pilot",
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
        self.udpSock.bind(QHostAddress.AnyIPv4, 0, QUdpSocket.ShareAddress)

    @pyqtSlot()
    def write_data_ref(self, path, data):
        """Idle timer expired. Trigger reconnection process."""
        cmd = b"DREF\x00"  # DREF command
        message = struct.pack("<5sf", cmd, data)
        message += bytes(path, "utf-8") + b"\x00"
        message += " ".encode("utf-8") * (509 - len(message))
        if self.xpHost:
            self.udpSock.writeDatagram(message, self.xpHost, self.xpPort)

    @pyqtSlot()
    def reconnect(self):
        """Idle timer expired. Trigger reconnection process."""
        self.logger.info("Connection Timeout expired")

        self.udpSock.close()
        self.idleTimer.stop()

        # let the screensaver activate
        if platform.machine() in "aarch64":

            os.system("xset s on")
            os.system("xset s 1")

    @pyqtSlot(QHostAddress, int)
    def xplaneConnect(self, addr, port):
        """Slot connecting triggering the connection to the XPlane."""
        self.listener.xpInstance.disconnect(self.xplaneConnect)
        self.listener.deleteLater()

        self.xpHost = addr
        self.xpPort = port

        self.logger.info("Request datatefs")
        # initiate connection
        for idx, dataref in enumerate(self.datarefs):
            cmd = b"RREF\x00"  # RREF command
            freq = dataref[1]
            ref = dataref[0].encode()
            message = struct.pack("<5sii400s", cmd, freq, idx, ref)
            self.logger.info("Request datatefs: {}".format(ref))
            assert len(message) == 413
            self.udpSock.writeDatagram(message, addr, port)
            end = datetime_.now() + timedelta(milliseconds=20)
            while datetime_.now() < end:
                QtGui.QGuiApplication.processEvents()

        # start the idle timer
        self.idleTimer.start(self.idleTimerDuration)

        # now we can inhibit the screensaver
        if platform.machine() in "aarch64":
            os.system("xset s reset")
            os.system("xset s off")

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
            self.udpSock.bind(QHostAddress.AnyIPv4, 0, QUdpSocket.ShareAddress)

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
                    # if idx == 0:
                    #     print("idx: {}, value: {}".format(idx, value))
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
        self.udpSock.bind(QHostAddress.AnyIPv4, self.XPPort, QUdpSocket.ShareAddress)
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
