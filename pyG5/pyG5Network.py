"""
Created on 8 Aug 2021.

@author: Ben Lauret
"""

import platform
import logging
import struct
import binascii
import os
import re
import shutil
import subprocess
from datetime import datetime as datetime_, timedelta

from PySide6.QtCore import QObject, Slot, Signal, QTimer, QCoreApplication

from PySide6.QtNetwork import QUdpSocket, QHostAddress, QAbstractSocket

from PySide6 import QtGui


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

    drefUpdate = Signal(object)

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
                "sim/cockpit/radios/nav1_dme_dist_m",
                30,
                "kt",
                "dme Range anv1",
                0,
                "_nav1dme",
            ),
            (
                "sim/cockpit/radios/nav2_dme_dist_m",
                30,
                "kt",
                "dme Range nav2",
                0,
                "_nav2dme",
            ),
            (
                "sim/cockpit2/radios/indicators/nav1_bearing_deg_mag",
                30,
                "degrees",
                "Nav bearing",
                0,
                "_nav1bearing",
            ),
            (
                "sim/cockpit2/radios/indicators/nav2_bearing_deg_mag",
                30,
                "degrees",
                "Nav bearing",
                0,
                "_nav2bearing",
            ),
            (
                "sim/cockpit2/autopilot/altitude_hold_ft",
                20,
                "ft",
                "Altitude Hold",
                0,
                "_altitudeHold",
            ),
            (
                "sim/cockpit2/autopilot/altitude_vnav_ft",
                20,
                "ft",
                "Altitude VNAV",
                0,
                "_altitudeVNAV",
            ),
            (
                "sim/cockpit2/radios/indicators/nav_src_ref",
                20,
                "enum",
                "NAV source",
                0,
                "_navSrc",
            ),
            (
                "sim/cockpit/autopilot/altitude",
                20,
                "feet",
                "AP altitude selected",
                0,
                "_apAltitude",
            ),
            (
                "sim/cockpit/autopilot/vertical_velocity",
                20,
                "fpm",
                "NAV source",
                0,
                "_apVS",
            ),
            (
                "sim/cockpit/autopilot/airspeed",
                20,
                "kt",
                "AP air speed",
                0,
                "_apAirSpeed",
            ),
            (
                "sim/cockpit/autopilot/autopilot_mode",
                20,
                "enum",
                "AP mode",
                0,
                "_apMode",
            ),
            (
                "sim/cockpit/autopilot/autopilot_state",
                20,
                "enum",
                "AP state",
                0,
                "_apState",
            ),
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
                "GPS Horizontal Situation Indicator sensitivity mode",
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
                "sim/cockpit/radios/nav_type[0]",
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
        self._last_data_received_at = None
        self._last_stream_debug_at = None

        self._screensaver_inhibited = False
        self._screensaver_cookie = None
        self._session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()
        self._xset_path = shutil.which("xset")
        self._gdbus_path = shutil.which("gdbus")
        self._dbus_send_path = shutil.which("dbus-send")
        self._screensaver_dbus_service = None
        self._screensaver_backend = self._detect_screensaver_backend()
        self._can_manage_screensaver = self._screensaver_backend is not None
        if not self._can_manage_screensaver:
            self.logger.info(
                "Screensaver control disabled: system=%s machine=%s session=%s xset=%s gdbus=%s dbus-send=%s dbus-service=%s",
                platform.system(),
                platform.machine(),
                self._session_type or "unknown",
                self._xset_path,
                self._gdbus_path,
                self._dbus_send_path,
                self._screensaver_dbus_service,
            )
        else:
            self.logger.info(
                "Screensaver control enabled: system=%s machine=%s session=%s backend=%s xset=%s gdbus=%s dbus-send=%s dbus-service=%s",
                platform.system(),
                platform.machine(),
                self._session_type or "unknown",
                self._screensaver_backend,
                self._xset_path,
                self._gdbus_path,
                self._dbus_send_path,
                self._screensaver_dbus_service,
            )

        # Idle timer trigger reconnection
        self.idleTimerDuration = 10000
        self.idleTimer = QTimer()
        self.idleTimer.timeout.connect(self.reconnect)

        app = QCoreApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(self._on_about_to_quit)

        # Create local UDP socket
        self.udpSock = QUdpSocket(self)

        # manage received data
        self.udpSock.readyRead.connect(self.dataHandler)

        # manage stage change to send data request
        self.udpSock.stateChanged.connect(self.socketStateHandler)

        # bind the socket
        self.udpSock.bind(
            QHostAddress.SpecialAddress.AnyIPv4, 0, QUdpSocket.BindFlag.ShareAddress
        )

    @Slot()
    def write_data_ref(self, path, data):
        """Idle timer expired. Trigger reconnection process."""
        cmd = b"DREF\x00"  # DREF command
        message = struct.pack("<5sf", cmd, data)
        message += bytes(path, "utf-8") + b"\x00"
        message += " ".encode("utf-8") * (509 - len(message))
        if self.xpHost:
            self.udpSock.writeDatagram(message, self.xpHost, self.xpPort)

    @Slot()
    def reconnect(self):
        """Idle timer expired. Trigger reconnection process."""
        seconds_since_data = None
        if self._last_data_received_at is not None:
            seconds_since_data = (
                datetime_.now() - self._last_data_received_at
            ).total_seconds()

        self.logger.warning(
            "Connection timeout expired (idleTimer=%sms, last_data_age=%.2fs, inhibited=%s)",
            self.idleTimerDuration,
            seconds_since_data if seconds_since_data is not None else -1.0,
            self._screensaver_inhibited,
        )

        self.udpSock.close()
        self.idleTimer.stop()
        self._set_screensaver_inhibited(False)

    @Slot(QHostAddress, int)
    def xplaneConnect(self, addr, port):
        """Slot connecting triggering the connection to the XPlane."""
        self.logger.info("XPlane connect discovered: host=%s port=%s", addr.toString(), port)
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
        self.logger.debug("Idle timer started (%sms)", self.idleTimerDuration)
        self._set_screensaver_inhibited(True)

    @Slot()
    def socketStateHandler(self):
        """Socket State handler."""
        self.logger.info("socketStateHandler: %s", self.udpSock.state())

        if self.udpSock.state() == QAbstractSocket.SocketState.BoundState:
            self.logger.info("Started Multicast listenner")
            # instantiate the multicast listener
            self.listener = pyG5MulticastListener(self)

            # connect the multicast listenner to the connect function
            self.listener.xpInstance.connect(self.xplaneConnect)

        elif self.udpSock.state() == QAbstractSocket.SocketState.UnconnectedState:
            self.logger.warning(
                "Socket transitioned to UnconnectedState. Rebinding and allowing screensaver"
            )
            self._set_screensaver_inhibited(False)
            # socket got disconnected issue reconnection
            self.udpSock.bind(
                QHostAddress.SpecialAddress.AnyIPv4, 0, QUdpSocket.BindFlag.ShareAddress
            )

    def _run_xset(self, *args):
        """Run xset command and log failures without crashing."""
        completed = subprocess.run(
            ["xset", *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            self.logger.warning(
                "xset %s failed: rc=%s stderr=%s",
                " ".join(args),
                completed.returncode,
                (completed.stderr or "").strip(),
            )
        else:
            self.logger.debug("xset %s succeeded", " ".join(args))

    def _detect_screensaver_backend(self):
        """Select a screen inhibition backend for this host/session."""
        if platform.system() != "Linux":
            return None

        has_dbus = self._gdbus_path is not None or self._dbus_send_path is not None
        is_wayland = self._session_type == "wayland"

        if has_dbus:
            self._screensaver_dbus_service = self._detect_screensaver_dbus_service()

        # Wayland compositors do not expose xset reliably; prefer a DBus service
        # that we have verified is actually present on the session bus.
        if is_wayland and self._screensaver_dbus_service is not None:
            return "dbus"

        if self._xset_path is not None:
            return "xset"

        if self._screensaver_dbus_service is not None:
            return "dbus"

        return None

    def _dbus_name_has_owner(self, service_name):
        """Return whether a DBus service currently exists on the session bus."""
        if self._gdbus_path is not None:
            cmd = [
                "gdbus",
                "call",
                "--session",
                "--dest",
                "org.freedesktop.DBus",
                "--object-path",
                "/org/freedesktop/DBus",
                "--method",
                "org.freedesktop.DBus.NameHasOwner",
                service_name,
            ]
        elif self._dbus_send_path is not None:
            cmd = [
                "dbus-send",
                "--session",
                "--dest=org.freedesktop.DBus",
                "--type=method_call",
                "--print-reply",
                "/org/freedesktop/DBus",
                "org.freedesktop.DBus.NameHasOwner",
                f"string:{service_name}",
            ]
        else:
            return False

        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            self.logger.debug(
                "DBus owner probe failed for %s: rc=%s stderr=%s",
                service_name,
                completed.returncode,
                (completed.stderr or "").strip(),
            )
            return False

        output = "\n".join(
            part for part in [(completed.stdout or ""), (completed.stderr or "")] if part
        )
        return "true" in output.lower()

    def _detect_screensaver_dbus_service(self):
        """Pick the first supported DBus inhibition API available in this session."""
        candidates = [
            {
                "name": "org.freedesktop.ScreenSaver",
                "object_path": "/org/freedesktop/ScreenSaver",
                "interface": "org.freedesktop.ScreenSaver",
                "inhibit_method": "Inhibit",
                "uninhibit_method": "UnInhibit",
                "inhibit_args": lambda reason: ["pyG5", reason],
                "uninhibit_args": lambda cookie: [int(cookie)],
            },
            {
                "name": "org.gnome.SessionManager",
                "object_path": "/org/gnome/SessionManager",
                "interface": "org.gnome.SessionManager",
                "inhibit_method": "Inhibit",
                "uninhibit_method": "Uninhibit",
                "inhibit_args": lambda reason: ["pyG5", 0, reason, 8],
                "uninhibit_args": lambda cookie: [int(cookie)],
            },
        ]

        for candidate in candidates:
            if self._dbus_name_has_owner(candidate["name"]):
                return candidate

        return None

    def _run_screensaver_dbus(self, method, *method_args):
        """Call the selected DBus screensaver/session manager method."""
        service = self._screensaver_dbus_service
        if service is None:
            self.logger.warning("DBus screensaver call requested without a detected service")
            return None

        if self._gdbus_path is not None:
            cmd = [
                "gdbus",
                "call",
                "--session",
                "--dest",
                service["name"],
                "--object-path",
                service["object_path"],
                "--method",
                f"{service['interface']}.{method}",
                *[str(arg) for arg in method_args],
            ]
        elif self._dbus_send_path is not None:
            typed_args = []
            for arg in method_args:
                if isinstance(arg, int):
                    typed_args.append(f"uint32:{arg}")
                else:
                    typed_args.append(f"string:{arg}")

            cmd = [
                "dbus-send",
                "--session",
                f"--dest={service['name']}",
                "--type=method_call",
                "--print-reply",
                service["object_path"],
                f"{service['interface']}.{method}",
                *typed_args,
            ]
        else:
            self.logger.warning("DBus screensaver call requested without available client")
            return None

        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            self.logger.warning(
                "DBus %s failed: rc=%s stderr=%s",
                method,
                completed.returncode,
                (completed.stderr or "").strip(),
            )
            return None

        output = (completed.stdout or "").strip()
        self.logger.debug("DBus %s succeeded: %s", method, output)
        return output

    def _dbus_inhibit(self):
        """Request compositor/session inhibition and return cookie."""
        service = self._screensaver_dbus_service
        if service is None:
            return None

        reason = "Keep displays awake while X-Plane is connected"
        output = self._run_screensaver_dbus(
            service["inhibit_method"], *service["inhibit_args"](reason)
        )
        if output is None:
            return None

        cookie_match = re.search(r"\b(\d+)\b", output)
        if cookie_match is None:
            self.logger.warning("Could not parse DBus inhibit cookie from output: %s", output)
            return None

        return int(cookie_match.group(1))

    def _dbus_uninhibit(self, cookie):
        """Release compositor/session inhibition cookie."""
        service = self._screensaver_dbus_service
        if service is None:
            return

        self._run_screensaver_dbus(
            service["uninhibit_method"], *service["uninhibit_args"](cookie)
        )

    def _set_screensaver_inhibited(self, inhibit):
        """Enable or disable screensaver inhibition once per state change."""
        if not self._can_manage_screensaver:
            self.logger.debug(
                "Skip screensaver inhibit=%s (unsupported on this host)", inhibit
            )
            return

        if inhibit == self._screensaver_inhibited:
            self.logger.debug(
                "No screensaver state change required (already inhibit=%s)",
                self._screensaver_inhibited,
            )
            return

        self.logger.info(
            "Changing screensaver inhibition %s -> %s",
            self._screensaver_inhibited,
            inhibit,
        )

        if self._screensaver_backend == "xset":
            if inhibit:
                # Disable both screen blanking and DPMS to keep displays awake.
                self._run_xset("s", "off")
                self._run_xset("-dpms")
                self._run_xset("s", "noblank")
                self._screensaver_inhibited = True
            else:
                # Restore defaults so screen management returns to OS settings.
                self._run_xset("s", "default")
                self._run_xset("+dpms")
                self._screensaver_inhibited = False
            return

        if self._screensaver_backend == "dbus":
            if inhibit:
                cookie = self._dbus_inhibit()
                if cookie is None:
                    self.logger.warning(
                        "Failed to acquire DBus screensaver inhibit cookie; blanking control unchanged"
                    )
                    return
                self._screensaver_cookie = cookie
                self._screensaver_inhibited = True
            else:
                if self._screensaver_cookie is not None:
                    self._dbus_uninhibit(self._screensaver_cookie)
                self._screensaver_cookie = None
                self._screensaver_inhibited = False
            return

        self.logger.debug(
            "No screensaver backend available while inhibit=%s was requested", inhibit
        )

    @Slot()
    def _on_about_to_quit(self):
        """Restore screen management when the app exits."""
        self.logger.info("Application closing. Restoring screensaver behavior")
        self._set_screensaver_inhibited(False)

    @Slot()
    def dataHandler(self):
        """dataHandler."""
        # data received restart the idle timer
        self.idleTimer.start(self.idleTimerDuration)
        now = datetime_.now()
        self._last_data_received_at = now

        if (
            self._last_stream_debug_at is None
            or (now - self._last_stream_debug_at).total_seconds() >= 30
        ):
            self.logger.debug(
                "Data stream alive. idleTimer restarted (%sms), pending=%s",
                self.idleTimerDuration,
                self.udpSock.pendingDatagramSize(),
            )
            self._last_stream_debug_at = now

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
                    (idx, value) = struct.unpack("<if", singledata.data())
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

    xpInstance = Signal(QHostAddress, int)

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
        self.udpSock.bind(
            QHostAddress.SpecialAddress.AnyIPv4,
            self.XPPort,
            QUdpSocket.BindFlag.ShareAddress,
        )
        if not self.udpSock.joinMulticastGroup(self.XPAddr):
            logging.error("Failed to join multicast group")

    @Slot(QAbstractSocket.SocketState)
    def stateChangedSlot(self, state):
        """stateChangedSlot."""
        self.logger.debug("Sock new state: {}".format(state))

    @Slot()
    def connectedSlot(self):
        """connectedSlot."""
        self.logger.debug("udp connected: {}".format(self.udpSock.state()))

    @Slot()
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
