"""
Created on 6 Aug 2021.

@author: Ben Lauret
"""

import logging

from math import cos, radians, sin, sqrt, floor
from functools import wraps

from PySide6.QtCore import (
    QLine,
    QPoint,
    QPointF,
    QRectF,
    QLineF,
    Qt,
    Slot,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QPainter,
    QPolygonF,
    QColor,
    QLinearGradient,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

g5Width = 480
g5CenterX = g5Width / 2
g5Height = 360
g5CenterY = g5Height / 2


fmaHeight = 30

g5Diag = sqrt(g5Width**2 + g5Height**2)

mstokt = 1.94384


class pyG5DualStackFMA(QWidget):
    """Base class for the G5 wdiget view."""

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QWidget.__init__(self, parent)

        self.pyG5FMA = pyG5FMA()
        self.pyG5FMA.setFixedSize(g5Width, fmaHeight)

        self.pyG5AI = pyG5AIWidget()
        self.pyG5AI.setFixedSize(g5Width, g5Height)
        self.pyG5HSI = pyG5HSIWidget()
        self.pyG5HSI.setFixedSize(g5Width, g5Height)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.pyG5FMA)
        self.vlayout.addWidget(self.pyG5AI)
        self.vlayout.addWidget(self.pyG5HSI)
        self.vlayout.setSpacing(0)
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.vlayout)


class pyG5DualStack(QWidget):
    """Base class for the G5 wdiget view."""

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QWidget.__init__(self, parent)

        self.pyG5AI = pyG5AIWidget()
        self.pyG5AI.setFixedSize(g5Width, g5Height)
        self.pyG5HSI = pyG5HSIWidget()
        self.pyG5HSI.setFixedSize(g5Width, g5Height)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.pyG5AI)
        self.vlayout.addWidget(self.pyG5HSI)
        self.vlayout.setSpacing(0)
        self.vlayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.vlayout)

        # self.setFixedSize(480,800)


class pyG5Widget(QWidget):
    """Base class for the G5 wdiget view."""

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        QWidget.__init__(self, parent)

        self.logger = logging.getLogger(self.__class__.__name__)

        """property name, default value"""
        propertyList = [
            ("altitudeHold", 0),
            ("altitudeVNAV", 0),
            ("navSrc", 0),
            ("apAltitude", 0),
            ("apVS", 0),
            ("apAirSpeed", 0),
            ("apState", 0),
            ("apMode", 0),
            ("fuelPress", 0),
            ("lowVolts", 0),
            ("oilPres", 0),
            ("parkBrake", 0),
            ("lowVacuum", 0),
            ("lowFuel", 0),
            ("fuelSel", 4),
            ("xpdrMode", 0),
            ("xpdrCode", 5470),
            ("trims", 0),
            ("flaps", 0),
            ("fuelpump", 0),
            ("carbheat", 0),
            ("gpsdmedist", 0),
            ("gpshsisens", 0),
            ("nav1type", 0),
            ("nav2type", 0),
            ("gpstype", 0),
            ("avionicson", 1),
            ("hsiSource", 0),
            ("nav1fromto", 0),
            ("nav2fromto", 0),
            ("gpsfromto", 0),
            ("nav1crs", 0),
            ("nav1gsavailable", 0),
            ("nav1gs", 0),
            ("nav2crs", 0),
            ("gpscrs", 0),
            ("nav2gsavailable", 0),
            ("nav2gs", 0),
            ("nav1dft", 0),
            ("nav2dft", 0),
            ("gpsdft", 0),
            ("gpsgsavailable", 0),
            ("gpsvnavavailable", 0),
            ("gpsgs", 0),
            ("groundTrack", 0),
            ("magHeading", 0),
            ("windDirection", 0),
            ("windSpeed", 0),
            ("rollAngle", 0),
            ("pitchAngle", 0),
            ("gs", 0),
            ("kias", 0),
            ("kiasDelta", 0),
            ("ktas", 0),
            ("altitude", 0),
            ("altitudeSel", 0),
            ("alt_setting", 1013),
            ("alt_setting_metric", 1),
            ("vh_ind_fpm", 0),
            ("turnRate", 0),
            ("slip", 0),
            ("headingBug", 0),
            ("vs", 30),
            ("vs0", 23),
            ("vfe", 88),
            ("vno", 118),
            ("vne", 127),
        ]

        def _make_setter(val):
            """Generate a setter function."""

            @wraps(val)
            def setter(inputVal):
                setattr(self, "_{}".format(val), inputVal)
                self.repaint()

            return setter

        for prop in propertyList:
            setattr(self, "_{}".format(prop[0]), prop[1])
            setattr(self, "{}".format(prop[0]), _make_setter(prop[0]))

    def setPen(self, width, color, style=Qt.PenStyle.SolidLine):
        """Set the pen color and width."""
        pen = self.qp.pen()
        pen.setColor(color)
        pen.setWidth(width)
        pen.setStyle(style)
        self.qp.setPen(pen)

    @Slot(dict)
    def drefHandler(self, retValues):
        """Handle the DREF update."""
        for idx, value in retValues.items():
            try:
                setattr(self, value[3], value[0])
            except Exception as e:
                self.logger.error("failed to set value {}: {}".format(value[5], e))

    def getNavTypeString(self, navType, navIndex):
        """getNavTypeString.

        Args:
            type: type number

        Returns:
            string
        """
        value = int(navType)

        if value == 0:
            return ""
        elif value == 3:
            return "VOR" + navIndex
        elif value >= 4:
            return "LOC" + navIndex

        logging.error("Failed to decode navtype")


secWidth = 800
secHeight = 480


class pyG5SecondaryWidget(pyG5Widget):
    """Generate G5 wdiget view."""

    xpdrCodeSignal = Signal(int)
    xpdrModeSignal = Signal(int)

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        pyG5Widget.__init__(self, parent)

        self.xpdrKeyboard = False

        self.setFixedSize(secWidth, secHeight)

        self.xpdrXbase = 20
        self.xpdrYbase = 20

        self.xpdrwidth = 160
        self.xpdrheight = 40

        self.xpdrRect = QRectF(
            self.xpdrXbase, self.xpdrYbase, self.xpdrwidth, self.xpdrheight
        )

        self.xpdrKeyXbase = 20
        self.xpdrKeyYbase = self.xpdrYbase + self.xpdrheight

        self.xpdrKeyWidth = 420
        self.xpdrKeyHeight = secHeight - (self.xpdrYbase + self.xpdrheight) - 20

        self.xpdrkeyRect = QRectF(
            self.xpdrKeyXbase, self.xpdrKeyYbase, self.xpdrKeyWidth, self.xpdrKeyHeight
        )

        self.xpdrPos = 3

        self.keyArea = []

        index = 0
        for i in [1, 2, 3, 4]:
            rect = QRectF(
                self.xpdrKeyXbase + 26.125 + index * 95,
                self.xpdrKeyYbase + 20,
                82.5,
                82.5,
            )
            self.keyArea.append([rect, i])
            index += 1

        index = 0
        for i in [5, 6, 7, 0]:
            rect = QRectF(
                self.xpdrKeyXbase + 26.125 + index * 95,
                self.xpdrKeyYbase + 20 + 95 + 20,
                82.5,
                82.5,
            )
            self.keyArea.append([rect, i])
            index += 1

        self.keyCtrlArea = []
        self.keyCtrlArea.append(
            [
                QRectF(
                    self.xpdrKeyXbase,
                    self.xpdrKeyYbase + self.xpdrKeyHeight / 2 + 40,
                    self.xpdrKeyWidth / 2,
                    self.xpdrKeyHeight / 4 - 20,
                ),
                "OFF",
                0,
            ]
        )
        self.keyCtrlArea.append(
            [
                QRectF(
                    self.xpdrKeyXbase,
                    self.xpdrKeyYbase + self.xpdrKeyHeight * 3 / 4 + 20,
                    self.xpdrKeyWidth / 2,
                    self.xpdrKeyHeight / 4 - 20,
                ),
                "ON",
                2,
            ]
        )

        self.keyCtrlArea.append(
            [
                QRectF(
                    self.xpdrKeyXbase + self.xpdrKeyWidth / 2,
                    self.xpdrKeyYbase + self.xpdrKeyHeight / 2 + 40,
                    self.xpdrKeyWidth / 2,
                    self.xpdrKeyHeight / 4 - 20,
                ),
                "STBY",
                1,
            ]
        )

        self.keyCtrlArea.append(
            [
                QRectF(
                    self.xpdrKeyXbase + self.xpdrKeyWidth / 2,
                    self.xpdrKeyYbase + self.xpdrKeyHeight * 3 / 4 + 20,
                    self.xpdrKeyWidth / 2,
                    self.xpdrKeyHeight / 4 - 20,
                ),
                "ALT",
                3,
            ]
        )

    def mousePressEvent(self, event):
        """Mouse Pressed event overload."""
        if self._avionicson:
            if self.xpdrRect.contains(event.position()):
                self.xpdrKeyboard = not self.xpdrKeyboard

            else:
                if self.xpdrkeyRect.contains(event.position()):
                    for key in self.keyArea:
                        if key[0].contains(event.position()):
                            # the input is a BCD value received as integer.
                            # First step is to turn it into a real integer
                            codestr = "{:04d}".format(int(self._xpdrCode))
                            code = 0
                            for idx, c in enumerate(codestr):
                                code |= int(c) << (4 * (3 - idx))

                            # code is the integer value of the string
                            # now apply on code the new number
                            code = code & ((0xF << (4 * self.xpdrPos)) ^ 0xFFFF)
                            code = code | (key[1] << (4 * self.xpdrPos))

                            # shift the position we update
                            self.xpdrPos = (self.xpdrPos - 1) % 4

                            # emit the new code value
                            self._xpdrCode = int("{:04x}".format(code))
                            self.xpdrCodeSignal.emit(self._xpdrCode)

                    for key in self.keyCtrlArea:
                        if key[0].contains(event.position()):
                            self.xpdrMode(key[2])
                            self.xpdrModeSignal.emit(key[2])
                            self.xpdrKeyboard = False
                else:
                    self.xpdrKeyboard = False

            if not self.xpdrKeyboard:
                self.xpdrPos = 3
        self.update()

    def paintEvent(self, event):
        """Paint the widget."""
        self.qp = QPainter(self)

        # Draw the background
        self.setPen(1, Qt.GlobalColor.black)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))
        self.qp.drawRect(0, 0, secWidth, secHeight)

        self.setPen(1, Qt.GlobalColor.white)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))

        # flaps settings
        flapXBase = 620
        flapYBase = 20
        flapHeight = secHeight - 40
        flapWidth = 130

        self.setPen(1, Qt.GlobalColor.white)
        self.qp.setBrush(QBrush(Qt.GlobalColor.white))
        font = self.qp.font()
        font.setPixelSize(30)
        font.setBold(True)
        self.qp.setFont(font)

        # draw the title
        self.qp.drawText(
            QRectF(
                flapXBase,
                flapYBase,
                flapWidth,
                40,
            ),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
            "FLAPS",
        )

        font.setPixelSize(20)
        font.setBold(False)
        self.qp.setFont(font)

        # draw the flaps angle legend
        for i in range(0, 4):
            self.qp.drawText(
                QRectF(
                    flapXBase,
                    flapYBase + 40 + int((flapHeight) * i / 4),
                    40,
                    40,
                ),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "{:02d}°".format(10 * i),
            )

        # draw the indicator rectangle
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))
        self.qp.drawRect(flapXBase + 90, flapYBase + 40, 40, flapHeight - 40)

        # draw the indicator legend white
        self.setPen(1, Qt.GlobalColor.white)
        self.qp.setBrush(QBrush(Qt.GlobalColor.white))
        rect = QRectF(
            flapXBase + 50,
            flapYBase + 40 + int((flapHeight - 40) / 3),
            40,
            flapHeight - 40 - +int((flapHeight - 40) / 3),
        )
        self.qp.drawRect(rect)
        self.setPen(1, Qt.GlobalColor.black)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))
        self.qp.drawText(
            rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, "8\n5"
        )

        # draw the indicator legend cyan
        self.setPen(1, Qt.GlobalColor.cyan)
        self.qp.setBrush(QBrush(Qt.GlobalColor.cyan))
        rect = QRectF(
            flapXBase + 50, flapYBase + 40, 40, int((flapHeight - 40) / 3 + 20)
        )
        self.qp.drawRect(rect)
        self.setPen(1, Qt.GlobalColor.black)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))
        self.qp.drawText(
            rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            "1\n1\n0",
        )

        self.setPen(1, Qt.GlobalColor.white)
        self.qp.setBrush(QBrush(Qt.GlobalColor.white))

        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(
                        flapXBase + flapWidth,
                        flapYBase + 50 + self._flaps * int((flapHeight - 100)),
                    ),
                    QPointF(
                        flapXBase + flapWidth,
                        flapYBase + 70 + self._flaps * int((flapHeight - 100)),
                    ),
                    QPointF(
                        flapXBase + flapWidth - 30,
                        flapYBase + 70 + self._flaps * int((flapHeight - 100)),
                    ),
                    QPointF(
                        flapXBase + flapWidth - 40,
                        flapYBase + 60 + self._flaps * int((flapHeight - 100)),
                    ),
                    QPointF(
                        flapXBase + flapWidth - 30,
                        flapYBase + 50 + self._flaps * int((flapHeight - 100)),
                    ),
                    QPointF(
                        flapXBase + flapWidth,
                        flapYBase + 50 + self._flaps * int((flapHeight - 100)),
                    ),
                ]
            )
        )

        # trim settings
        trimXBase = 460
        trimYBase = 20
        trimHeight = secHeight - 40
        trimWidth = 130

        self.setPen(1, Qt.GlobalColor.white)
        self.qp.setBrush(QBrush(Qt.GlobalColor.white))
        font = self.qp.font()
        font.setPixelSize(30)
        font.setBold(True)
        self.qp.setFont(font)

        # draw the title
        self.qp.drawText(
            QRectF(
                trimXBase + 40,
                trimYBase,
                90,
                40,
            ),
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
            "TRIM",
        )

        font.setPixelSize(20)
        font.setBold(False)
        self.qp.setFont(font)

        # draw the flaps angle legend
        self.qp.drawText(
            QRectF(
                trimXBase,
                trimYBase + 40 + int((trimHeight) / 2 - 40),
                80,
                40,
            ),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            "Take-off",
        )

        # draw the indicator rectangle
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))
        self.qp.drawRect(trimXBase + 90, trimYBase + 40, 40, trimHeight - 40)

        self.setPen(1, Qt.GlobalColor.white)
        self.qp.setBrush(QBrush(Qt.GlobalColor.white))

        trimShift = (trimHeight - 60) * (self._trims / 2 + 0.5)

        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(trimXBase + trimWidth, trimYBase + 40 + trimShift),
                    QPointF(trimXBase + trimWidth, trimYBase + 60 + trimShift),
                    QPointF(trimXBase + trimWidth - 30, trimYBase + 60 + trimShift),
                    QPointF(trimXBase + trimWidth - 40, trimYBase + 50 + trimShift),
                    QPointF(trimXBase + trimWidth - 30, trimYBase + 40 + trimShift),
                    QPointF(trimXBase + trimWidth, trimYBase + 40 + trimShift),
                ]
            )
        )

        # sqawk code and status
        if self._avionicson:
            font = self.qp.font()
            font.setPixelSize(self.xpdrheight - 6)
            font.setBold(True)
            self.qp.setFont(font)

            # draw the indicator rectangle
            self.setPen(2, Qt.GlobalColor.white)
            self.qp.setBrush(QBrush(Qt.GlobalColor.white))
            self.qp.drawRect(self.xpdrRect)

            self.setPen(1, Qt.GlobalColor.black)
            self.qp.setBrush(QBrush(Qt.GlobalColor.black))
            self.qp.drawText(
                self.xpdrRect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "XPDR",
            )

            self.setPen(2, Qt.GlobalColor.white)
            self.qp.setBrush(QBrush(Qt.GlobalColor.black))
            rect = QRectF(
                self.xpdrXbase + self.xpdrwidth,
                self.xpdrYbase,
                420 - self.xpdrwidth,
                self.xpdrheight,
            )
            self.qp.drawRect(rect)

            self.setPen(1, Qt.GlobalColor.white)
            self.qp.setBrush(QBrush(Qt.GlobalColor.white))

            if int(self._xpdrMode) == 0:
                xpdrMode = "OFF"
            elif int(self._xpdrMode) == 1:
                xpdrMode = "STDBY"
            elif int(self._xpdrMode) == 2:
                xpdrMode = "ON"
            elif int(self._xpdrMode) == 3:
                xpdrMode = "ALT"
            elif int(self._xpdrMode) == 4:
                xpdrMode = "TEST"

            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "{:04d} {}".format(int(self._xpdrCode), xpdrMode),
            )

        if self.xpdrKeyboard:
            self.setPen(2, Qt.GlobalColor.white)
            self.qp.setBrush(QBrush(Qt.GlobalColor.black))
            self.qp.drawRect(self.xpdrkeyRect)

            for key in self.keyArea:
                self.qp.drawEllipse(key[0])
                self.qp.drawText(
                    key[0],
                    Qt.AlignmentFlag.AlignCenter,
                    "{:01d}".format(key[1]),
                )

            for key in self.keyCtrlArea:
                self.qp.drawRect(key[0])
                self.qp.drawText(
                    key[0],
                    Qt.AlignmentFlag.AlignCenter,
                    key[1],
                )

        else:
            # carb heat status
            carbXbase = 20
            carbYbase = self.xpdrYbase + self.xpdrheight + 20

            carbwidth = 80
            carbheight = 80

            font.setPixelSize(20)
            font.setBold(False)
            self.qp.setFont(font)

            rect = QRectF(carbXbase, carbYbase, carbwidth, 40)

            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "CARB",
            )

            self.setPen(2, Qt.GlobalColor.white)
            if self._carbheat > 0.1:
                self.qp.setBrush(QBrush(Qt.GlobalColor.green))
            else:
                self.qp.setBrush(QBrush(Qt.GlobalColor.black))

            rect = QRectF(carbXbase, carbYbase + 40, carbwidth, carbheight)

            self.qp.drawEllipse(rect)

            # fuel pump status
            fuelXbase = 20
            fuelYbase = carbYbase + carbheight + 20

            fuelwidth = 80
            fuelheight = 80

            font.setPixelSize(20)
            font.setBold(False)
            self.qp.setFont(font)

            rect = QRectF(fuelXbase, fuelYbase, fuelwidth, 100)

            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "FUEL\nPUMP",
            )

            self.setPen(2, Qt.GlobalColor.white)
            self.qp.setBrush(QBrush(Qt.GlobalColor.green))

            rect = QRectF(fuelXbase, fuelYbase + 80, fuelwidth, fuelheight)

            if self._fuelpump > 0 and self._avionicson:
                self.qp.setBrush(QBrush(Qt.GlobalColor.green))
            else:
                self.qp.setBrush(QBrush(Qt.GlobalColor.black))

            self.qp.drawEllipse(rect)

            # fuel feed settings

            ffXBase = 120
            ffYBase = carbYbase + 40

            ffWdidth = 440 - ffXBase
            ffHeight = 220

            self.setPen(1, Qt.GlobalColor.white)
            self.qp.setBrush(QBrush(Qt.GlobalColor.white))
            rect = QRectF(ffXBase, carbYbase, ffWdidth, 20)
            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "FUEL FEED",
            )

            self.setPen(1, Qt.GlobalColor.white)
            self.qp.setBrush(QBrush(Qt.GlobalColor.black))

            rect = QRectF(ffXBase, ffYBase, ffWdidth, ffHeight)
            self.qp.drawRect(rect)

            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                "BOTH",
            )
            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
                "OFF",
            )

            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                "LEFT",
            )

            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                "RIGHT",
            )

            self.qp.translate(rect.center())

            if self._fuelSel == 0:
                self.qp.rotate(180)
            elif self._fuelSel == 1:
                self.qp.rotate(-90)
            elif self._fuelSel == 2:
                self.qp.rotate(45)
            elif self._fuelSel == 3:
                self.qp.rotate(90)
            elif self._fuelSel == 4:
                self.qp.rotate(0)
            else:
                self.qp.rotate(0)

            brect = QRectF(-50, -50, 100, 100)
            self.qp.drawEllipse(brect)

            self.setPen(1, Qt.GlobalColor.white)
            self.qp.setBrush(QBrush(Qt.GlobalColor.white))
            self.qp.drawPolygon(
                QPolygonF(
                    [
                        QPointF(-10, +50),
                        QPointF(+10, +50),
                        QPointF(+10, -50),
                        QPointF(0, -70),
                        QPointF(-10, -50),
                    ]
                )
            )

            self.setPen(1, Qt.GlobalColor.black)
            self.qp.setBrush(QBrush(Qt.GlobalColor.black))
            brect = QRectF(-5, -5, 10, 10)
            self.qp.drawEllipse(brect)

            self.qp.resetTransform()

            # advisory panel (low voltage)
            advXBase = 20
            advYBase = fuelYbase + fuelheight + 100

            advWdidth = 420
            advHeight = 100

            advTable = [
                {
                    "text": "LOW\nVOLTS",
                    "color": Qt.GlobalColor.red,
                    "name": "_lowVolts",
                },
                {"text": "LOW\nFUEL", "color": Qt.GlobalColor.red, "name": "_lowFuel"},
                {"text": "OIL\nPRESS", "color": Qt.GlobalColor.red, "name": "_oilPres"},
                {"text": "BRAKE", "color": Qt.GlobalColor.red, "name": "_parkBrake"},
                {
                    "text": "LOW\nVACUUM",
                    "color": Qt.GlobalColor.yellow,
                    "name": "_lowVacuum",
                },
                {
                    "text": "FUEL\nPRESS",
                    "color": Qt.GlobalColor.yellow,
                    "name": "_fuelPress",
                },
            ]

            grayColor = QColor("#5d5b59")
            self.setPen(1, grayColor)
            self.qp.setBrush(QBrush(Qt.GlobalColor.black))

            rect = QRectF(advXBase, advYBase, advWdidth, advHeight)
            self.qp.drawRect(rect)

            for i in range(0, 2):
                for j in range(0, 4):
                    advrect = QRectF(
                        advXBase + j * advWdidth / 4,
                        advYBase + i * advHeight / 2,
                        advWdidth / 4,
                        advHeight / 2,
                    )
                    self.qp.drawRect(advrect)

                    if j + 4 * i < len(advTable):
                        if getattr(self, advTable[4 * i + j]["name"]) == 1:
                            self.setPen(1, advTable[4 * i + j]["color"])

                        self.qp.drawText(
                            advrect,
                            Qt.AlignmentFlag.AlignHCenter
                            | Qt.AlignmentFlag.AlignVCenter,
                            advTable[4 * i + j]["text"],
                        )

                        self.setPen(1, grayColor)

        self.qp.end()


class pyG5HSIWidget(pyG5Widget):
    """Generate G5 wdiget view."""

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        pyG5Widget.__init__(self, parent)

    def paintEvent(self, event):
        """Paint the widget."""
        self.qp = QPainter(self)

        greyColor = QColor(128, 128, 128, 255)
        rotatinghsiCircleRadius = 160
        hsiCircleRadius = 90
        hsiTextRadius = 120
        hsiCenter = 190
        groundTrackDiamondSize = 7

        headingBoxWidth = 50
        headingBoxHeight = 22

        font = self.qp.font()
        font.setPixelSize(headingBoxHeight - 2)
        font.setBold(True)
        self.qp.setFont(font)

        # Draw the background
        self.setPen(1, Qt.GlobalColor.black)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))
        self.qp.drawRect(0, 0, g5Width, g5Height)

        if self._avionicson == 0:
            self.setPen(1, Qt.GlobalColor.white)
            self.qp.drawLine(0, 0, g5Width, g5Height)
            self.qp.drawLine(0, g5Height, g5Width, 0)
            self.qp.end()
            return

        # Draw the Horizontal Situation Indicator circle
        self.setPen(2, greyColor)

        # offset the center to the Horizontal Situation Indicator center
        self.qp.translate(g5CenterX, hsiCenter)

        self.qp.drawArc(
            -hsiCircleRadius,
            -hsiCircleRadius,
            2 * hsiCircleRadius,
            2 * hsiCircleRadius,
            0,
            360 * 16,
        )

        # Draw the fixed Horizontal Situation Indicator marker
        hsiPeripheralMarkers = [
            45,
            90,
            135,
            225,
            270,
            315,
        ]
        self.setPen(2, Qt.GlobalColor.white)

        for marker in hsiPeripheralMarkers:
            self.qp.rotate(-marker)
            self.qp.drawLine(0, 170, 0, 185)
            self.qp.rotate(marker)

        # Draw the RotatingHSI lines and Text

        # rotate by the current magnetic heading
        self.qp.rotate(-self._magHeading)

        currentHead = 0
        while currentHead < 360:
            if (currentHead % 90) == 0:
                length = 20
            elif (currentHead % 10) == 0:
                length = 15
            else:
                length = 10
            self.qp.drawLine(
                0, rotatinghsiCircleRadius - length, 0, rotatinghsiCircleRadius
            )

            if currentHead == 0:
                text = "N"
            elif currentHead == 90:
                text = "E"
            elif currentHead == 180:
                text = "S"
            elif currentHead == 270:
                text = "W"
            elif (currentHead % 30) == 0:
                text = "{:2d}".format(int(currentHead / 10))
            else:
                text = ""

            if len(text):
                self.qp.translate(0, -hsiTextRadius)
                self.qp.rotate(+self._magHeading - currentHead)
                self.qp.drawText(
                    QRectF(
                        -self.qp.font().pixelSize() / 2 - 3,
                        -self.qp.font().pixelSize() / 2,
                        self.qp.font().pixelSize() + 6,
                        self.qp.font().pixelSize(),
                    ),
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                    text,
                )
                self.qp.rotate(-self._magHeading + currentHead)
                self.qp.translate(0, hsiTextRadius)

            self.qp.rotate(+5)
            currentHead += 5

        # draw the Heading bug
        self.setPen(1, Qt.GlobalColor.cyan)
        self.qp.setBrush(QBrush(Qt.GlobalColor.cyan))

        self.qp.rotate(180 + self._headingBug)

        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(-15, rotatinghsiCircleRadius - 3),
                    QPointF(+15, rotatinghsiCircleRadius - 3),
                    QPointF(+15, rotatinghsiCircleRadius + 6),
                    QPointF(+6, rotatinghsiCircleRadius + 6),
                    QPointF(0, rotatinghsiCircleRadius + 1),
                    QPointF(-6, rotatinghsiCircleRadius + 6),
                    QPointF(-15, rotatinghsiCircleRadius + 6),
                ]
            )
        )

        self.setPen(1, Qt.GlobalColor.black)
        gpscdianonciator = ""
        if int(self._hsiSource) == 2:
            cdiSource = "GPS"
            # 0=OCN, 1=ENR, 2=TERM, 3=DPRT, 4=MAPR, 5=APR, 6=RNPAR, 7=LNAV, 8=LNAV+V, 9=L/VNAV, 10=LP, 11=LPV, 12=LP+V, 13=GLS
            tableMap = [
                "OCN",
                "ENR",
                "TERM",
                "DPRT",
                "MAPR",
                "APR",
                "RNPAR",
                "LNAV",
                "LNAV+V",
                "L/VNAV",
                "LP",
                "LPV",
                "LP+V",
                "GLS",
                "",
            ]
            try:
                gpscdianonciator = tableMap[int(self._gpshsisens)]
            except IndexError:
                gpscdianonciator = tableMap[-1]

            navColor = Qt.GlobalColor.magenta
            navdft = self._gpsdft
            navfromto = self._gpsfromto
            navcrs = self._gpscrs
            if (self._gpsvnavavailable != -1000) or self._gpsgsavailable:
                vertAvailable = 1
            else:
                vertAvailable = 0
            gsDev = self._gpsgs
        elif int(self._hsiSource) == 1:
            cdiSource = "{}".format(self.getNavTypeString(self._nav2type, "2"))
            navColor = Qt.GlobalColor.green
            navdft = self._nav2dft
            navfromto = self._nav2fromto
            navcrs = self._nav2crs
            vertAvailable = self._nav2gsavailable
            gsDev = self._nav2gs
        else:
            cdiSource = "{}".format(self.getNavTypeString(self._nav1type, "1"))
            navColor = Qt.GlobalColor.green
            navdft = self._nav1dft
            navfromto = self._nav1fromto
            navcrs = self._nav1crs
            vertAvailable = self._nav1gsavailable
            gsDev = self._nav1gs

        self.qp.setBrush(QBrush(navColor))
        # Draw the CDI
        self.qp.rotate(90 - self._headingBug + navcrs)

        # CDI arrow
        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(rotatinghsiCircleRadius - 10, 0),
                    QPointF(rotatinghsiCircleRadius - 40, -20),
                    QPointF(rotatinghsiCircleRadius - 33, -3),
                    QPointF(hsiCircleRadius - 10, -3),
                    QPointF(hsiCircleRadius - 10, 3),
                    QPointF(rotatinghsiCircleRadius - 33, 3),
                    QPointF(rotatinghsiCircleRadius - 40, 20),
                ]
            )
        )
        # CDI bottom bar
        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(-rotatinghsiCircleRadius + 10, -3),
                    QPointF(-hsiCircleRadius + 10, -3),
                    QPointF(-hsiCircleRadius + 10, +3),
                    QPointF(-rotatinghsiCircleRadius + 10, +3),
                ]
            )
        )
        # CDI deflection bar
        if int(navfromto) != 0:
            hsiDeflectionBound = hsiCircleRadius / 75 * 2
            deflection = (
                max(min(navdft, hsiDeflectionBound), -hsiDeflectionBound) / 2 * 75
            )
            self.qp.drawPolygon(
                QPolygonF(
                    [
                        QPointF(hsiCircleRadius - 10, deflection - 3),
                        QPointF(-hsiCircleRadius + 10, deflection - 3),
                        QPointF(-hsiCircleRadius + 10, deflection + 3),
                        QPointF(hsiCircleRadius - 10, deflection + 3),
                    ]
                )
            )

            # NAV1 FromTo
            fromToTipX = 65
            if int(navfromto) == 2:
                self.qp.rotate(180)

            self.qp.drawPolygon(
                QPolygonF(
                    [
                        QPointF(fromToTipX - 10, 0),
                        QPointF(fromToTipX - 40, -20),
                        QPointF(fromToTipX - 30, 0),
                        QPointF(fromToTipX - 40, 20),
                    ]
                )
            )
            if int(navfromto) == 2:
                self.qp.rotate(180)

        self.qp.rotate(90)
        # CDI deflection circle
        self.setPen(2, Qt.GlobalColor.white)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))

        for i in [-81, -41, 31, 69]:
            self.qp.drawArc(
                QRectF(
                    i,
                    -6,
                    12,
                    12,
                ),
                0,
                360 * 16,
            )

        self.qp.resetTransform()

        font = self.qp.font()
        font.setPixelSize(15)
        font.setBold(False)
        self.qp.setFont(font)
        if int(self._hsiSource) == 2:
            self.setPen(2, Qt.GlobalColor.magenta)
        else:
            self.setPen(2, Qt.GlobalColor.green)

        self.qp.drawText(
            QRectF(g5CenterX - 70, hsiCenter - 50, 65, 18),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            cdiSource,
        )

        if len(gpscdianonciator):
            self.qp.drawText(
                QRectF(g5CenterX + 25, hsiCenter - 50, 65, 18),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                gpscdianonciator,
            )

        # Draw the heading Bug indicator bottom corner
        self.setPen(2, Qt.GlobalColor.cyan)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))

        headingWidth = 105
        headingHeigth = 30
        self.qp.drawRect(QRectF(g5Width, g5Height, -headingWidth, -headingHeigth))

        # draw the bug symbol
        self.setPen(1, Qt.GlobalColor.cyan)
        self.qp.setBrush(QBrush(Qt.GlobalColor.cyan))

        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(381, 336),
                    QPointF(381, 354),
                    QPointF(387, 354),
                    QPointF(387, 349),
                    QPointF(382, 346),
                    QPointF(382, 344),
                    QPointF(387, 341),
                    QPointF(387, 336),
                ]
            )
        )

        self.qp.drawText(
            QRectF(412, 336, 65, 18),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "{:03d}˚".format(int(self._headingBug)),
        )

        # draw the dist box
        if int(self._hsiSource) == 2:
            font.setPixelSize(12)
            font.setBold(False)
            self.qp.setFont(font)
            distRect = QRectF(g5Width - 105, 0, 105, 45)

            self.setPen(2, greyColor)
            self.qp.setBrush(QBrush(Qt.GlobalColor.black))
            self.qp.drawRect(distRect)

            self.qp.drawText(
                distRect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                "Dist NM",
            )

            font.setPixelSize(18)
            font.setBold(True)
            self.qp.setFont(font)
            self.setPen(1, navColor)

            distRect = QRectF(g5Width - 105, 12, 105, 45 - 12)
            self.qp.drawText(
                distRect,
                Qt.AlignmentFlag.AlignCenter,
                "{}".format(round(self._gpsdmedist, 1)),
            )

        # set default font size
        font = self.qp.font()
        font.setPixelSize(18)
        font.setBold(True)
        self.qp.setFont(font)

        # draw the wind box
        self.setPen(2, greyColor)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))

        self.qp.drawRect(0, 0, 105, 45)

        self.setPen(1, Qt.GlobalColor.white)
        self.qp.setBrush(QBrush(Qt.GlobalColor.white))

        self.qp.translate(25, 25)

        self.qp.rotate(180 - self._magHeading + self._windDirection)

        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(-5, 0),
                    QPointF(0, -10),
                    QPointF(5, 0),
                    QPointF(2, 0),
                    QPointF(2, 10),
                    QPointF(-2, 10),
                    QPointF(-2, 0),
                ]
            )
        )

        self.qp.resetTransform()

        self.qp.drawText(
            QRectF(50, 2, 50, 20),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "{:03d}˚".format(int(self._windDirection)),
        )

        self.qp.drawText(
            QRectF(50, 22, 50, 20),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "{:02d}kt".format(int(self._windSpeed * mstokt)),
        )

        # Draw the magnetic heading box
        self.setPen(2, greyColor)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))
        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(g5CenterX - headingBoxWidth / 2, 1),
                    QPointF(g5CenterX - headingBoxWidth / 2, headingBoxHeight),
                    QPointF(g5CenterX - 6, headingBoxHeight),
                    QPointF(g5CenterX, headingBoxHeight + 8),
                    QPointF(g5CenterX + 6, headingBoxHeight),
                    QPointF(g5CenterX + headingBoxWidth / 2, headingBoxHeight),
                    QPointF(g5CenterX + headingBoxWidth / 2, 1),
                ]
            )
        )

        self.qp.drawText(
            QRectF(
                g5CenterX - headingBoxWidth / 2, 1, headingBoxWidth, headingBoxHeight
            ),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            "{:03d}˚".format(int(self._magHeading)),
        )

        # Draw the ground track
        self.setPen(0, Qt.GlobalColor.transparent)
        self.qp.setBrush(QBrush(Qt.GlobalColor.magenta))
        self.qp.translate(g5CenterX, hsiCenter)
        self.qp.rotate(-self._magHeading + self._groundTrack)
        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(
                        -groundTrackDiamondSize,
                        -rotatinghsiCircleRadius - groundTrackDiamondSize,
                    ),
                    QPointF(
                        +groundTrackDiamondSize,
                        -rotatinghsiCircleRadius - groundTrackDiamondSize,
                    ),
                    QPointF(+0, -rotatinghsiCircleRadius),
                ]
            )
        )
        self.setPen(3, greyColor, Qt.PenStyle.DashLine)
        self.qp.drawLine(0, 0, 0, -rotatinghsiCircleRadius)
        self.qp.resetTransform()

        # draw the aircraft
        self.setPen(1, Qt.GlobalColor.white)
        self.qp.setBrush(QBrush(Qt.GlobalColor.white))

        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(240, 163),
                    QPointF(235, 169),
                    QPointF(235, 180),
                    QPointF(215, 195),
                    QPointF(215, 200),
                    QPointF(235, 195),
                    QPointF(235, 205),
                    QPointF(227, 213),
                    QPointF(227, 217),
                    QPointF(240, 213),
                    QPointF(253, 217),
                    QPointF(253, 213),
                    QPointF(245, 205),
                    QPointF(245, 195),
                    QPointF(265, 200),
                    QPointF(265, 195),
                    QPointF(245, 180),
                    QPointF(245, 169),
                ]
            )
        )

        # draw the GlideScope
        gsWidth = 16
        gsHeigth = 192
        gsCircleRad = 10
        gsFromLeft = 20
        gsDiamond = 16

        if vertAvailable:
            # Vertical guidance source
            rect = QRectF(
                g5Width - gsFromLeft - gsWidth,
                hsiCenter - gsHeigth / 2 - 15,
                gsWidth,
                15,
            )

            font.setPixelSize(12)
            self.qp.setFont(font)
            self.setPen(1, navColor)

            vertSourceTxt = "G"
            if int(self._hsiSource) == 2 and self._gpsgsavailable == 0:
                vertSourceTxt = "V"

            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                vertSourceTxt,
            )

            self.setPen(2, greyColor)
            self.qp.setBrush(QBrush(Qt.GlobalColor.transparent))

            self.qp.drawRect(rect)

            # main rectangle
            self.qp.drawRect(
                QRectF(
                    g5Width - gsFromLeft - gsWidth,
                    hsiCenter - gsHeigth / 2,
                    gsWidth,
                    gsHeigth,
                )
            )

            self.qp.drawLine(
                g5Width - gsFromLeft - gsWidth,
                hsiCenter,
                g5Width - gsFromLeft,
                hsiCenter,
            )

            for offset in [-70, -35, 35, 70]:
                self.qp.drawEllipse(
                    QPointF(
                        int(g5Width - gsFromLeft - gsWidth / 2),
                        int(hsiCenter + offset),
                    ),
                    gsCircleRad / 2,
                    gsCircleRad / 2,
                )

            self.setPen(1, Qt.GlobalColor.black)
            self.qp.setBrush(QBrush(navColor))

            self.qp.translate(
                g5Width - gsFromLeft - gsWidth, hsiCenter + gsDev / 2.5 * gsHeigth / 2
            )
            self.qp.drawPolygon(
                QPolygonF(
                    [
                        QPointF(0, 0),
                        QPointF(gsDiamond / 2, gsDiamond / 2),
                        QPointF(gsDiamond, 0),
                        QPointF(gsDiamond / 2, -gsDiamond / 2),
                    ]
                )
            )

            self.qp.resetTransform()

        # draw the CRS selection

        crsBoxHeight = 30
        crsBoxWidth = 105

        self.setPen(2, greyColor)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))

        rect = QRectF(0, g5Height - crsBoxHeight, crsBoxWidth, crsBoxHeight)
        self.qp.drawRect(rect)

        self.setPen(1, Qt.GlobalColor.white)

        font = self.qp.font()
        font.setPixelSize(15)
        self.qp.setFont(font)

        rect = QRectF(1, g5Height - crsBoxHeight + 1, crsBoxWidth - 2, crsBoxHeight - 2)
        self.qp.drawText(
            rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom, "CRS"
        )

        font = self.qp.font()
        font.setPixelSize(25)
        self.qp.setFont(font)
        if int(self._hsiSource) == 2:
            self.setPen(1, Qt.GlobalColor.magenta)
        else:
            self.setPen(1, Qt.GlobalColor.green)
        rect = QRectF(40, g5Height - crsBoxHeight + 1, 65, crsBoxHeight - 2)
        self.qp.drawText(
            rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            "{:03d}˚".format(int(navcrs)),
        )

        self.qp.end()


class pyG5AIWidget(pyG5Widget):
    """Generate G5 wdiget view."""

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        pyG5Widget.__init__(self, parent)

        # parameters
        self.rollArcRadius = g5CenterY * 0.8
        self._pitchScale = 25

    def paintEvent(self, event):
        """Paint the widget."""
        diamondHeight = 14
        diamondWidth = 14

        self.qp = QPainter(self)

        if self._avionicson == 0:
            self.setPen(1, Qt.GlobalColor.black)
            self.qp.setBrush(QBrush(Qt.GlobalColor.black))
            self.qp.drawRect(0, 0, g5Width, g5Height)
            self.setPen(1, Qt.GlobalColor.white)
            self.qp.drawLine(0, 0, g5Width, g5Height)
            self.qp.drawLine(0, g5Height, g5Width, 0)
            self.qp.end()
            return

        # set default font size
        font = self.qp.font()
        font.setPixelSize(6)
        font.setBold(True)
        self.qp.setFont(font)

        self.setPen(1, Qt.GlobalColor.white)
        grad = QLinearGradient(g5CenterX, g5Height, g5CenterX, 0)
        grad.setColorAt(1, QColor(0, 50, 200, 255))
        grad.setColorAt(0, QColor(0, 255, 255, 255))
        self.qp.setBrush(grad)

        # draw contour + backgorun sky
        self.qp.drawRect(QRectF(0, 0, g5Width, g5Height))

        # draw the rotating part depending on the roll angle
        self.qp.translate(g5CenterX, g5CenterY)
        self.qp.rotate(-self._rollAngle)

        # draw the ground
        grad = QLinearGradient(
            g5CenterX,
            +self._pitchAngle / self._pitchScale * g5CenterY,
            g5CenterX,
            +g5Diag,
        )
        grad.setColorAt(0, QColor(152, 103, 45))
        grad.setColorAt(1, QColor(255, 222, 173))
        self.qp.setBrush(grad)

        self.qp.drawRect(
            QRectF(
                QPointF(
                    -g5Diag,
                    +self._pitchAngle / self._pitchScale * g5CenterY,
                ),
                QPointF(
                    +g5Diag,
                    +g5Diag,
                ),
            )
        )

        # draw the pitch lines
        height = 0
        pitch = 0
        width = [10, 20, 10, 30]
        mode = 0
        while height < self.rollArcRadius - 40:
            pitch += 2.5
            height = (
                pitch / self._pitchScale * g5CenterY
                + self._pitchAngle / self._pitchScale * g5CenterY
            )
            self.qp.drawLine(
                QPointF(
                    -width[mode],
                    height,
                ),
                QPointF(
                    width[mode],
                    height,
                ),
            )
            if width[mode] == 30:
                self.qp.drawText(QPoint(30 + 3, int(height + 2)), str(int(pitch)))
                self.qp.drawText(QPoint(-40, int(height + 2)), str(int(pitch)))
            mode = (mode + 1) % 4

        height = 0
        pitch = 0
        width = [10, 20, 10, 30]
        mode = 0
        while height > -self.rollArcRadius + 30:
            pitch -= 2.5
            height = (
                pitch / self._pitchScale * g5CenterY
                + self._pitchAngle / self._pitchScale * g5CenterY
            )
            self.qp.drawLine(
                QPointF(
                    -width[mode],
                    height,
                ),
                QPointF(
                    width[mode],
                    height,
                ),
            )
            if width[mode] == 30:
                self.qp.drawText(QPoint(30 + 3, int(height + 2)), str(abs(int(pitch))))
                self.qp.drawText(QPoint(-40, int(height + 2)), str(abs(int(pitch))))

            mode = (mode + 1) % 4

        # draw the static roll arc
        self.setPen(3, Qt.GlobalColor.white)

        bondingRect = QRectF(
            -self.rollArcRadius,
            -self.rollArcRadius,
            2 * self.rollArcRadius,
            2 * self.rollArcRadius,
        )
        self.qp.drawArc(bondingRect, 30 * 16, 120 * 16)

        # draw the Roll angle arc markers
        rollangleindicator = [
            [-30, 10],
            [-45, 5],
            [-135, 5],
            [-150, 10],
            [-60, 10],
            [-70, 5],
            [-80, 5],
            [-100, 5],
            [-110, 5],
            [-120, 10],
        ]

        self.qp.setBrush(QBrush(Qt.GlobalColor.white))
        self.setPen(2, Qt.GlobalColor.white)
        for lineParam in rollangleindicator:
            self.qp.drawLine(self.alongRadiusCoord(lineParam[0], lineParam[1]))

        self.setPen(1, Qt.GlobalColor.white)
        # draw the diamond on top of the roll arc
        self.qp.drawPolygon(
            QPolygonF(
                [
                    QPointF(
                        0,
                        -self.rollArcRadius - 2,
                    ),
                    QPointF(-diamondWidth / 2, -self.rollArcRadius - diamondHeight),
                    QPointF(+diamondWidth / 2, -self.rollArcRadius - diamondHeight),
                ]
            )
        )

        self.qp.resetTransform()

        # create the fixed diamond

        fixedDiamond = QPolygonF(
            [
                QPointF(g5CenterX, g5CenterY - self.rollArcRadius + 2),
                QPointF(
                    g5CenterX + diamondWidth / 2,
                    g5CenterY - self.rollArcRadius + diamondHeight,
                ),
                QPointF(
                    g5CenterX - diamondWidth / 2,
                    g5CenterY - self.rollArcRadius + diamondHeight,
                ),
            ]
        )

        self.qp.drawPolygon(fixedDiamond)

        # create the nose
        self.qp.setBrush(QBrush(Qt.GlobalColor.yellow))
        self.qp.setBackgroundMode(Qt.BGMode.OpaqueMode)

        self.setPen(1, Qt.GlobalColor.black)

        # solid polygon left
        nose = QPolygonF(
            [
                QPointF(g5CenterX - 1, g5CenterY + 1),
                QPointF(g5CenterX - 75, g5CenterY + 38),
                QPointF(g5CenterX - 54, g5CenterY + 38),
            ]
        )
        self.qp.drawPolygon(nose)

        # solid polygon right
        nose = QPolygonF(
            [
                QPointF(g5CenterX + 1, g5CenterY + 1),
                QPointF(g5CenterX + 75, g5CenterY + 38),
                QPointF(g5CenterX + 54, g5CenterY + 38),
            ]
        )
        self.qp.drawPolygon(nose)

        # solid marker left
        marker = QPolygonF(
            [
                QPointF(120, g5CenterY - 5),
                QPointF(155, g5CenterY - 5),
                QPointF(160, g5CenterY),
                QPointF(155, g5CenterY + 5),
                QPointF(120, g5CenterY + 5),
            ]
        )
        self.qp.drawPolygon(marker)

        # solid marker right
        marker = QPolygonF(
            [
                QPointF(360, g5CenterY - 5),
                QPointF(325, g5CenterY - 5),
                QPointF(320, g5CenterY),
                QPointF(325, g5CenterY + 5),
                QPointF(360, g5CenterY + 5),
            ]
        )
        self.qp.drawPolygon(marker)

        brush = QBrush(QColor(0x7E, 0x7E, 0x34, 255))
        self.qp.setBrush(brush)

        # cross pattern polygon left
        nose = QPolygonF(
            [
                QPointF(g5CenterX - 2, g5CenterY + 2),
                QPointF(g5CenterX - 33, g5CenterY + 38),
                QPointF(g5CenterX - 54, g5CenterY + 38),
            ]
        )
        self.qp.drawPolygon(nose)

        # cross pattern polygon right
        nose = QPolygonF(
            [
                QPointF(g5CenterX + 2, g5CenterY + 2),
                QPointF(g5CenterX + 33, g5CenterY + 38),
                QPointF(g5CenterX + 54, g5CenterY + 38),
            ]
        )
        self.qp.drawPolygon(nose)

        self.setPen(0, Qt.GlobalColor.transparent)
        # solid polygon right
        nose = QPolygonF(
            [
                QPointF(120, g5CenterY),
                QPointF(160, g5CenterY),
                QPointF(155, g5CenterY + 5),
                QPointF(120, g5CenterY + 5),
            ]
        )
        self.qp.drawPolygon(nose)
        # solid polygon right
        nose = QPolygonF(
            [
                QPointF(360, g5CenterY),
                QPointF(320, g5CenterY),
                QPointF(325, g5CenterY + 5),
                QPointF(360, g5CenterY + 5),
            ]
        )
        self.qp.drawPolygon(nose)

        #################################################
        # SPEED TAPE
        #################################################

        speedBoxLeftAlign = 7
        speedBoxHeight = 50
        speedBoxWdith = 75
        speedBoxSpikedimension = 10
        tasHeight = 30
        speedDeltaWidth = 4

        tapeScale = 50

        self.setPen(0, Qt.GlobalColor.transparent)

        self.qp.setBrush(QBrush(QColor(0, 0, 0, 90)))
        self.qp.drawRect(QRectF(0, 0, speedBoxLeftAlign + speedBoxWdith + 15, g5Height))

        if (self._kias + tapeScale / 2) > self._vne:
            brush = QBrush(QColor(Qt.GlobalColor.red))
            self.qp.setBrush(brush)

            self.qp.drawRect(
                QRectF(
                    speedBoxLeftAlign + speedBoxWdith + 8,
                    0,
                    8,
                    (1 - 2 * (self._vne - self._kias) / tapeScale) * g5CenterY,
                )
            )

        if (self._kias + tapeScale / 2) > self._vno:
            brush = QBrush(QColor(Qt.GlobalColor.yellow))
            self.qp.setBrush(brush)

            self.qp.drawRect(
                QRectF(
                    speedBoxLeftAlign + speedBoxWdith + 8,
                    (1 - 2 * (self._vne - self._kias) / tapeScale) * g5CenterY,
                    8,
                    (2 * (self._vne - self._vno) / tapeScale) * g5CenterY,
                )
            )

        if (self._kias + tapeScale / 2) > self._vs:
            brush = QBrush(QColor(Qt.GlobalColor.green))
            self.qp.setBrush(brush)
            self.qp.drawRect(
                QRectF(
                    speedBoxLeftAlign + speedBoxWdith + 8,
                    max(0, (1 - 2 * (self._vno - self._kias) / tapeScale) * g5CenterY),
                    8,
                    (1 - 2 * (self._vs - self._kias) / tapeScale) * g5CenterY,
                )
            )

        if (self._kias + tapeScale / 2) > self._vs:
            brush = QBrush(QColor(Qt.GlobalColor.white))
            self.qp.setBrush(brush)
            self.qp.drawRect(
                QRectF(
                    speedBoxLeftAlign + speedBoxWdith + 13,
                    max(0, (1 - 2 * (self._vfe - self._kias) / tapeScale) * g5CenterY),
                    3,
                    (1 - 2 * (self._vs0 - self._kias) / tapeScale) * g5CenterY,
                )
            )

        self.setPen(2, Qt.GlobalColor.white)

        self.qp.setBackgroundMode(Qt.BGMode.TransparentMode)
        font = self.qp.font()
        font.setPixelSize(speedBoxHeight - 15)

        # set default font size
        self.qp.setFont(font)

        currentTape = int(self._kias + tapeScale / 2)
        while currentTape > max(0, self._kias - tapeScale / 2):
            if (currentTape % 10) == 0:
                tapeHeight = (
                    1 - 2 * (currentTape - self._kias) / tapeScale
                ) * g5CenterY
                self.qp.drawLine(
                    QPointF(speedBoxLeftAlign + speedBoxWdith + 5, tapeHeight),
                    QPointF(speedBoxLeftAlign + speedBoxWdith + 15, tapeHeight),
                )

                self.qp.drawText(
                    QRectF(
                        speedBoxLeftAlign,
                        tapeHeight - speedBoxHeight / 2,
                        speedBoxWdith,
                        speedBoxHeight,
                    ),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    "{:d}".format(int(currentTape)),
                )

            elif (currentTape % 5) == 0:
                self.qp.drawLine(
                    QPointF(
                        speedBoxLeftAlign + speedBoxWdith + 8,
                        (1 - 2 * (currentTape - self._kias) / tapeScale) * g5CenterY,
                    ),
                    QPointF(
                        speedBoxLeftAlign + speedBoxWdith + 15,
                        (1 - 2 * (currentTape - self._kias) / tapeScale) * g5CenterY,
                    ),
                )

            currentTape -= 1

        speedBox = QPolygonF(
            [
                QPointF(speedBoxLeftAlign, g5CenterY + speedBoxHeight / 2),
                QPointF(
                    speedBoxLeftAlign + speedBoxWdith, g5CenterY + speedBoxHeight / 2
                ),
                QPointF(
                    speedBoxLeftAlign + speedBoxWdith,
                    g5CenterY + speedBoxSpikedimension,
                ),
                QPointF(
                    speedBoxLeftAlign + speedBoxWdith + speedBoxSpikedimension,
                    g5CenterY,
                ),
                QPointF(
                    speedBoxLeftAlign + speedBoxWdith,
                    g5CenterY - speedBoxSpikedimension,
                ),
                QPointF(
                    speedBoxLeftAlign + speedBoxWdith, g5CenterY - speedBoxHeight / 2
                ),
                QPointF(speedBoxLeftAlign, g5CenterY - speedBoxHeight / 2),
            ]
        )

        self.setPen(2, Qt.GlobalColor.white)

        brush = QBrush(QColor(0, 0, 0, 255))
        self.qp.setBrush(brush)

        self.qp.drawPolygon(speedBox)

        font = self.qp.font()
        font.setPixelSize(speedBoxHeight - 10)
        # set default font size
        self.qp.setFont(font)

        self.qp.drawText(
            QRectF(
                speedBoxLeftAlign,
                g5CenterY - speedBoxHeight / 2,
                speedBoxWdith,
                speedBoxHeight,
            ),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            "{:03d}".format(int(self._kias)),
        )

        # draw the TAS box
        rect = QRectF(
            0,
            0,
            speedBoxLeftAlign + speedBoxWdith + 15,
            tasHeight,
        )
        self.qp.drawRect(rect)

        font = self.qp.font()
        font.setPixelSize(20)
        # set default font size
        self.qp.setFont(font)

        self.qp.drawText(
            rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            "TAS {:03d} kt".format(int(self._ktas)),
        )

        # draw the TAS box
        rect = QRectF(
            0,
            g5Height - tasHeight,
            speedBoxLeftAlign + speedBoxWdith + 15,
            tasHeight,
        )
        self.qp.drawRect(rect)
        self.qp.drawText(
            rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "GS"
        )

        self.setPen(2, Qt.GlobalColor.magenta)

        self.qp.drawText(
            rect,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            "{:03d} kt".format(int(self._gs * mstokt)),
        )

        self.setPen(1, Qt.GlobalColor.magenta)

        brush = QBrush(Qt.GlobalColor.magenta)
        self.qp.setBrush(brush)

        self.qp.drawRect(
            QRectF(
                speedBoxLeftAlign + speedBoxWdith + 15,
                g5CenterY,
                speedDeltaWidth,
                -2 * (self._kiasDelta * 10) / tapeScale * g5CenterY,
            )
        )

        #################################################
        # ALTITUDE TAPE
        #################################################

        altBoxRightAlign = 7
        altBoxHeight = 30
        altBoxWdith = 75
        altBoxSpikedimension = 10
        altTapeScale = 300
        altTapeLeftAlign = g5Width - altBoxRightAlign - altBoxWdith
        altSettingHeight = 30

        vsScale = 30
        vsIndicatorWidth = 7

        alttapteLeftBound = altTapeLeftAlign - 1.5 * altBoxSpikedimension
        self.setPen(0, Qt.GlobalColor.transparent)
        self.qp.setBrush(QBrush(QColor(0, 0, 0, 90)))
        self.qp.drawRect(
            QRectF(alttapteLeftBound, 0, g5Width - alttapteLeftBound, int(g5Height))
        )
        self.setPen(2, Qt.GlobalColor.white)

        self.qp.setBackgroundMode(Qt.BGMode.TransparentMode)
        font = self.qp.font()
        font.setPixelSize(10)
        # set default font size
        self.qp.setFont(font)

        # VS tape
        currentTape = vsScale

        while currentTape >= 0:
            tapeHeight = (vsScale - currentTape) / vsScale * g5Height
            if (currentTape % 5) == 0:
                self.qp.drawLine(
                    QPointF(g5Width - 10, tapeHeight),
                    QPointF(g5Width, tapeHeight),
                )
                self.qp.drawText(
                    QRectF(
                        g5Width - 30,
                        tapeHeight - 5,
                        15,
                        vsIndicatorWidth + 3,
                    ),
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    "{:d}".format(abs(int(currentTape - vsScale / 2))),
                )
            else:
                self.qp.drawLine(
                    QPointF(g5Width - vsIndicatorWidth, tapeHeight),
                    QPointF(g5Width, tapeHeight),
                )

            currentTape -= 1
        # tapeHeight = (vsScale - currentTape) / vsScale * g5Height
        vsHeight = -self._vh_ind_fpm / 100 / vsScale * g5Height
        vsRect = QRectF(g5Width, g5CenterY, -vsIndicatorWidth, vsHeight)

        self.setPen(0, Qt.GlobalColor.transparent)

        brush = QBrush(QColor(Qt.GlobalColor.magenta))
        self.qp.setBrush(brush)

        self.qp.drawRect(vsRect)

        self.setPen(2, Qt.GlobalColor.white)

        font = self.qp.font()
        font.setPixelSize(20)
        # set default font size
        self.qp.setFont(font)

        # altitude tape
        currentTape = int(self._altitude + altTapeScale / 2)

        while currentTape > self._altitude - altTapeScale / 2:
            if (currentTape % 20) == 0:
                tapeHeight = (
                    1 - 2 * (currentTape - self._altitude) / altTapeScale
                ) * g5CenterY
                self.qp.drawLine(
                    QPointF(altTapeLeftAlign - 1.5 * altBoxSpikedimension, tapeHeight),
                    QPointF(altTapeLeftAlign - altBoxSpikedimension / 2, tapeHeight),
                )
                if (currentTape % 100) == 0:
                    self.qp.drawText(
                        QRectF(
                            altTapeLeftAlign,
                            tapeHeight - speedBoxHeight / 2,
                            speedBoxWdith,
                            speedBoxHeight,
                        ),
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        "{:d}".format(int(currentTape)),
                    )

            currentTape -= 1

        # altitude selector
        pen = self.qp.pen()
        pen.setColor(Qt.GlobalColor.cyan)
        pen.setWidth(2)
        self.qp.setPen(pen)
        brush = QBrush(QColor(Qt.GlobalColor.cyan))
        self.qp.setBrush(brush)

        altSelCenter = g5CenterY
        if self._altitudeSel >= int(self._altitude + altTapeScale / 2 - 24):
            altSelCenter = altSettingHeight
        elif self._altitudeSel <= int(self._altitude - altTapeScale / 2 + 24):
            altSelCenter = g5Height - altSettingHeight
        else:
            altSelCenter = (
                (floor(self._altitude + altTapeScale / 2) - self._altitudeSel)
                / altTapeScale
                * g5Height
            )

        altSel = QPolygonF(
            [
                QPointF(alttapteLeftBound, altSelCenter - altBoxHeight / 2),
                QPointF(alttapteLeftBound, altSelCenter + altBoxHeight / 2),
                QPointF(altTapeLeftAlign, altSelCenter + altBoxHeight / 2),
                QPointF(altTapeLeftAlign, altSelCenter + altBoxSpikedimension),
                QPointF(altTapeLeftAlign - altBoxSpikedimension, altSelCenter),
                QPointF(altTapeLeftAlign, altSelCenter - altBoxSpikedimension),
                QPointF(altTapeLeftAlign, altSelCenter - altBoxHeight / 2),
            ]
        )
        self.qp.drawPolygon(altSel)

        # Altitude Box
        self.setPen(2, Qt.GlobalColor.white)
        altBoxTextSplitRatio = 2 / 5
        altBox = QPolygonF(
            [
                QPointF(g5Width - altBoxRightAlign, g5CenterY - altBoxHeight),
                QPointF(
                    g5Width - altBoxRightAlign - altBoxWdith * altBoxTextSplitRatio,
                    g5CenterY - altBoxHeight,
                ),
                QPointF(
                    g5Width - altBoxRightAlign - altBoxWdith * altBoxTextSplitRatio,
                    g5CenterY - altBoxHeight / 2,
                ),
                QPointF(
                    altTapeLeftAlign,
                    g5CenterY - altBoxHeight / 2,
                ),
                QPointF(
                    altTapeLeftAlign,
                    g5CenterY - altBoxSpikedimension,
                ),
                QPointF(
                    altTapeLeftAlign - altBoxSpikedimension,
                    g5CenterY,
                ),
                QPointF(
                    altTapeLeftAlign,
                    g5CenterY + altBoxSpikedimension,
                ),
                QPointF(
                    altTapeLeftAlign,
                    g5CenterY + altBoxHeight / 2,
                ),
                QPointF(
                    g5Width - altBoxRightAlign - altBoxWdith * altBoxTextSplitRatio,
                    g5CenterY + altBoxHeight / 2,
                ),
                QPointF(
                    g5Width - altBoxRightAlign - altBoxWdith * altBoxTextSplitRatio,
                    g5CenterY + altBoxHeight,
                ),
                QPointF(g5Width - altBoxRightAlign, g5CenterY + altBoxHeight),
            ]
        )

        brush = QBrush(QColor(0, 0, 0, 255))
        self.qp.setBrush(brush)

        self.qp.drawPolygon(altBox)

        # implement the last 2 digits in 20 ft steps
        altStep = 20
        charWidth = 15

        if self._altitude < 0 and self._altitude > -1000:
            # Add the  minus sign
            dispRect = QRectF(
                altTapeLeftAlign,
                g5CenterY - altBoxHeight / 2,
                charWidth,
                altBoxHeight,
            )

            self.qp.drawText(
                dispRect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "-",
            )

            # extract lower digits
            altLowerDigit = int("{:05d}".format(int(self._altitude))[3:5])

            # floor the last to digit to the closest multiple of 20
            altLowerDigitrounded = 20 * floor(altLowerDigit / 20)

            altLowerDigitMod20 = altLowerDigit % 20

            if self._altitude >= -40:
                pass
                if altLowerDigitrounded == 20:
                    altArray = [20, 0, 20, 40, 60]
                elif altLowerDigitrounded == 40:
                    altArray = [0, 20, 40, 60, 80]
                else:
                    altArray = [40, 20, 0, 20, 40]

            else:
                altArray = []
                for i in range(5):
                    tmp = altLowerDigitrounded + altStep * (i - 2)
                    if int(self._altitude / 100) * 100 + tmp >= 0:
                        altArray.append(tmp % 100)
                    else:
                        altArray.append((100 - tmp) % 100)

            # define a clip rect to avoid overflowing the alt box
            self.qp.setClipRect(
                QRectF(
                    g5Width - altBoxRightAlign - altBoxWdith * altBoxTextSplitRatio,
                    g5CenterY - altBoxHeight,
                    altBoxWdith * altBoxTextSplitRatio,
                    2 * altBoxHeight,
                )
            )

            # draw the last 2 digits altitude
            self.qp.drawText(
                QRectF(
                    altTapeLeftAlign + altBoxWdith * (1 - altBoxTextSplitRatio),
                    g5CenterY
                    - 2 * altBoxHeight
                    - 0.8 * altBoxHeight * (altLowerDigitMod20 / 20),
                    altBoxWdith * altBoxTextSplitRatio,
                    4 * altBoxHeight,
                ),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "\n".join("{:02d}".format(t) for t in altArray),
            )

            # clear clip rect
            self.qp.setClipRect(0, 0, g5Width, g5Height)

        if self._altitude >= 0:
            # extract the last 2 digit
            altLowerDigit = int(self._altitude % 100)

            # floor the last to digit to the closest multiple of 20
            altLowerDigitrounded = 20 * floor(altLowerDigit / 20)

            altLowerDigitMod20 = altLowerDigit % 20

            # fill the array centered on the floor value in multiple of 20ft
            altArray = []
            for i in range(5):
                tmp = altLowerDigitrounded + altStep * (2 - i)
                if int(self._altitude / 100) * 100 + tmp >= 0:
                    altArray.append(tmp % 100)
                else:
                    altArray.append((100 - tmp) % 100)

            altString = "{:05d}".format(int(self._altitude))

            if self._altitude > 9900:
                dispRect = QRectF(
                    altTapeLeftAlign,
                    g5CenterY - altBoxHeight / 2,
                    charWidth,
                    altBoxHeight,
                )

                if (
                    altString[1] == "9"
                    and altString[2] == "9"
                    and altLowerDigitrounded == 80
                ):
                    self.qp.setClipRect(dispRect)

                    self.qp.drawText(
                        QRectF(
                            altTapeLeftAlign,
                            g5CenterY
                            - altBoxHeight / 2
                            - 20
                            + +0.8 * altBoxHeight * (altLowerDigitMod20 / 20),
                            charWidth,
                            60,
                        ),
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                        "{:01d}\n{}".format((int(altString[0]) + 1) % 10, altString[0])
                        if self._altitude >= 10000
                        else "{:01d}\n ".format((int(altString[0]) + 1) % 10),
                    )

                    self.qp.setClipRect(0, 0, g5Width, g5Height)

                else:
                    self.qp.drawText(
                        dispRect,
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                        altString[0] if self._altitude >= 10000 else "",
                    )

            if self._altitude >= 980:
                dispRect = QRectF(
                    altTapeLeftAlign + charWidth,
                    g5CenterY - altBoxHeight / 2,
                    charWidth,
                    altBoxHeight,
                )

                if altString[2] == "9" and altLowerDigitrounded == 80:
                    self.qp.setClipRect(dispRect)

                    self.qp.drawText(
                        QRectF(
                            altTapeLeftAlign + charWidth,
                            g5CenterY
                            - altBoxHeight / 2
                            - 20
                            + +0.8 * altBoxHeight * (altLowerDigitMod20 / 20),
                            charWidth,
                            60,
                        ),
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                        "{:01d}\n{}".format((int(altString[1]) + 1) % 10, altString[1])
                        if self._altitude >= 1000
                        else "{:01d}\n ".format((int(altString[1]) + 1) % 10),
                    )

                    self.qp.setClipRect(0, 0, g5Width, g5Height)

                else:
                    self.qp.drawText(
                        dispRect,
                        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                        altString[1] if self._altitude >= 1000 else "",
                    )
                    pass

            dispRect = QRectF(
                altTapeLeftAlign + 2 * charWidth,
                g5CenterY - altBoxHeight / 2,
                charWidth,
                altBoxHeight,
            )

            if altLowerDigitrounded == 80:
                self.qp.setClipRect(dispRect)

                self.qp.drawText(
                    QRectF(
                        altTapeLeftAlign + 2 * charWidth,
                        g5CenterY
                        - altBoxHeight / 2
                        - 20
                        + +0.8 * altBoxHeight * (altLowerDigitMod20 / 20),
                        charWidth,
                        60,
                    ),
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                    "{:01d}\n{}".format((int(altString[2]) + 1) % 10, altString[2]),
                )
                self.qp.setClipRect(0, 0, g5Width, g5Height)
            else:
                self.qp.drawText(
                    dispRect,
                    Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                    altString[2],
                )

            # define a clip rect to avoid overflowing the alt box
            self.qp.setClipRect(
                QRectF(
                    g5Width - altBoxRightAlign - altBoxWdith * altBoxTextSplitRatio,
                    g5CenterY - altBoxHeight,
                    altBoxWdith * altBoxTextSplitRatio,
                    2 * altBoxHeight,
                )
            )

            # draw the last 2 digits altitude
            self.qp.drawText(
                QRectF(
                    altTapeLeftAlign + altBoxWdith * (1 - altBoxTextSplitRatio),
                    g5CenterY
                    - 2 * altBoxHeight
                    + 0.8 * altBoxHeight * (altLowerDigitMod20 / 20),
                    altBoxWdith * altBoxTextSplitRatio,
                    4 * altBoxHeight,
                ),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "\n".join("{:02d}".format(t) for t in altArray),
            )

            # clear clip rect
            self.qp.setClipRect(0, 0, g5Width, g5Height)

        # draw the altimeter setting
        pen = self.qp.pen()
        pen.setColor(Qt.GlobalColor.cyan)
        pen.setWidth(2)
        self.qp.setPen(pen)
        leftAlign = altTapeLeftAlign - 1.5 * altBoxSpikedimension
        rect = QRectF(
            leftAlign,
            g5Height - altSettingHeight,
            g5Width - leftAlign,
            altSettingHeight,
        )
        self.qp.drawRect(rect)

        if 1:
            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "{:04.00f}".format(33.863886 * self._alt_setting),
            )
        else:
            self.qp.drawText(
                rect,
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                "{:02.02f}".format(self._alt_setting),
            )

        # draw the altitude selector
        pen = self.qp.pen()
        pen.setColor(Qt.GlobalColor.cyan)
        pen.setWidth(2)
        self.qp.setPen(pen)
        leftAlign = altTapeLeftAlign - 1.5 * altBoxSpikedimension
        rect = QRectF(
            leftAlign,
            0,
            g5Width - leftAlign,
            altSettingHeight,
        )
        self.qp.drawRect(rect)

        self.qp.drawText(
            rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            "{:d}ft".format(int(self._altitudeSel)),
        )

        #################################################
        # Turn coordinator
        #################################################

        turnrateHalfWidth = 62
        turnrateHeight = 15
        slipballHeigh = 320
        slipballRadius = 15
        slipballMarkeWidth = 6
        slipballMovementMax = 1
        slipballMovementWdith = 15

        self.setPen(1, QColor(0, 0, 0, 127))

        self.qp.drawLine(
            QPointF(g5CenterX, g5Height - turnrateHeight),
            QPointF(g5CenterX, g5Height),
        )
        self.qp.drawLine(
            QPointF(g5CenterX - turnrateHalfWidth, g5Height - turnrateHeight),
            QPointF(g5CenterX + turnrateHalfWidth, g5Height - turnrateHeight),
        )

        self.setPen(0, Qt.GlobalColor.transparent)

        brush = QBrush(QColor(Qt.GlobalColor.magenta))
        self.qp.setBrush(brush)
        rect = QRectF(
            g5CenterX,
            g5Height - turnrateHeight + 1,
            min(max(self._turnRate, -73), 73) / 32 * turnrateHalfWidth,
            turnrateHeight - 2,
        )
        self.qp.drawRect(rect)

        self.setPen(1, QColor(255, 255, 255, 128))

        self.qp.drawLine(
            QPointF(g5CenterX - turnrateHalfWidth, g5Height - turnrateHeight),
            QPointF(g5CenterX - turnrateHalfWidth, g5Height),
        )
        self.qp.drawLine(
            QPointF(g5CenterX + turnrateHalfWidth, g5Height - turnrateHeight),
            QPointF(g5CenterX + turnrateHalfWidth, g5Height),
        )

        # slip ball
        # draw the static roll arc
        self.setPen(2, QColor(0, 0, 0, 128))

        self.qp.setBrush(QBrush(QColor(220, 220, 220)))

        self.qp.drawRect(
            QRectF(
                g5CenterX - slipballRadius,
                slipballHeigh - slipballRadius,
                -slipballMarkeWidth,
                2 * slipballRadius,
            )
        )
        self.qp.drawRect(
            QRectF(
                g5CenterX + slipballRadius,
                slipballHeigh - slipballRadius,
                slipballMarkeWidth,
                2 * slipballRadius,
            )
        )
        # set slip ball gradian
        grad = QRadialGradient(
            g5CenterX - self._slip * slipballMovementMax * slipballMovementWdith,
            slipballHeigh,
            slipballRadius,
            g5CenterX - self._slip * slipballMovementMax * slipballMovementWdith,
            slipballHeigh,
        )
        grad.setColorAt(0, QColor(255, 255, 255, 200))
        grad.setColorAt(1, QColor(160, 160, 160, 200))
        self.qp.setBrush(grad)

        self.qp.drawEllipse(
            QPoint(
                int(
                    g5CenterX - self._slip * slipballMovementMax * slipballMovementWdith
                ),
                int(slipballHeigh),
            ),
            slipballRadius,
            slipballRadius,
        )

        self.qp.end()

    def pitchLine(self, offset, length):
        """Return a pitch line.

        As the pitch line is drawn using translate and rotate
        align the pitch line around the center

        Args:
            angle: in degrees
            length: in pixel

        Returns:
            Qline
        """
        pass

    def alongRadiusCoord(self, angle, length):
        """Return a line along the radius of the circle.

        Args:
            angle: in degrees
            length: in pixel

        Returns:
            Qline
        """
        startPoint = QPoint(
            int(self.rollArcRadius * cos(radians(angle))),
            int(self.rollArcRadius * sin(radians(angle))),
        )
        endPoint = QPoint(
            int((self.rollArcRadius + length) * cos(radians(angle))),
            int((self.rollArcRadius + length) * sin(radians(angle))),
        )

        return QLine(startPoint, endPoint)


class pyG5FMA(pyG5Widget):
    """Generate G5 wdiget view."""

    def __init__(self, parent=None):
        """g5Widget Constructor.

        Args:
            parent: Parent Widget

        Returns:
            self
        """
        pyG5Widget.__init__(self, parent)

    def paintEvent(self, event):
        """Paint the widget."""
        self.qp = QPainter(self)

        self.setPen(1, Qt.GlobalColor.black)
        self.qp.setBrush(QBrush(Qt.GlobalColor.black))
        self.qp.drawRect(0, 0, g5Width, fmaHeight)

        if self._avionicson == 0:
            self.setPen(1, Qt.GlobalColor.white)
            self.qp.drawLine(0, 0, g5Width, fmaHeight)
            self.qp.drawLine(0, fmaHeight, g5Width, 0)
            self.qp.end()
            return

        # draw the FMA sections delimiters
        delimMargin = 5
        self.setPen(2, Qt.GlobalColor.white)
        self.qp.drawLine(
            QLineF(g5Width / 2, delimMargin, g5Width / 2, fmaHeight - delimMargin)
        )
        self.qp.drawLine(
            QLineF(g5Width / 3, delimMargin, g5Width / 3, fmaHeight - delimMargin)
        )

        self.setPen(2, Qt.GlobalColor.green)

        font = self.qp.font()
        font.setPixelSize(20)
        font.setBold(True)
        self.qp.setFont(font)

        # draw the text when the AP is engaged
        if self._apMode != 0:
            # Draw the AP mode
            mode = "AP" if self._apMode == 2 else "FD"
            self.qp.drawText(
                QRectF(
                    g5Width / 3 + delimMargin,
                    delimMargin,
                    g5Width / 6 - 2 * delimMargin,
                    fmaHeight - 2 * delimMargin,
                ),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                mode,
            )

            # find the engaged horizontal navigation mode
            if int(self._apState) & 0x2:
                hmode = "HDG"
            elif int(self._apState) & 0x4:
                hmode = "ROL"
            elif int(self._apState) & 0x200:
                if int(self._hsiSource) == 2:
                    hmode = "GPS"
                elif int(self._hsiSource) == 1:
                    hmode = "{}".format(self.getNavTypeString(self._nav2type, ""))
                elif int(self._hsiSource) == 0:
                    hmode = "{}".format(self.getNavTypeString(self._nav1type, ""))
                else:
                    hmode = "ERR"
            else:
                hmode = ""
            self.qp.drawText(
                QRectF(
                    g5Width / 6 + delimMargin,
                    delimMargin,
                    g5Width / 6 - 2 * delimMargin,
                    fmaHeight - 2 * delimMargin,
                ),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                hmode,
            )

            # find the engaged vertical navigation mode
            if int(self._apState) & 0x8:
                vmode = "FLC {} kts".format(int(self._apAirSpeed))
            elif int(self._apState) & 0x10:
                vmode = "VS {} fpm".format(int(self._apVS))
            elif int(self._apState) & 0x800:
                vmode = "GS"
            elif int(self._apState) & 0x4000:
                vmode = "ALT {} ft".format(int(self._altitudeHold))
            elif int(self._apState) & 0x40000:
                vmode = "VPATH"
            else:
                vmode = "PIT"

            self.qp.drawText(
                QRectF(
                    g5Width / 2 + delimMargin,
                    delimMargin,
                    g5Width * 2 / 6 - 2 * delimMargin,
                    fmaHeight - 2 * delimMargin,
                ),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                vmode,
            )

        # draw the armed horizontal navigation mode
        self.setPen(2, Qt.GlobalColor.white)

        if int(self._apState) & 0x100:
            if int(self._hsiSource) == 2:
                hmode = "GPS"
            elif int(self._hsiSource) == 1:
                hmode = "{}".format(self.getNavTypeString(self._nav2type, ""))
            elif int(self._hsiSource) == 0:
                hmode = "{}".format(self.getNavTypeString(self._nav1type, ""))
            else:
                hmode = "ERR"

            self.qp.drawText(
                QRectF(
                    delimMargin,
                    delimMargin,
                    g5Width / 6 - 2 * delimMargin,
                    fmaHeight - 2 * delimMargin,
                ),
                Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
                hmode,
            )
        vmode = ""
        if int(self._apState) & 0x20000:
            vmode += " VPATH" if len(vmode) else "VPTH"
        else:
            if int(self._apState) & 0x20:
                if self._altitudeVNAV > self._apAltitude:
                    vmode += " ALTV" if len(vmode) else "ALTV"
                else:
                    vmode += " ALTS" if len(vmode) else "ALTS"
        if int(self._apState) & 0x400:
            vmode += " GS" if len(vmode) else "GS"

        self.qp.drawText(
            QRectF(
                g5Width * 4 / 6 + delimMargin,
                delimMargin,
                g5Width * 2 / 6 - 2 * delimMargin,
                fmaHeight - 2 * delimMargin,
            ),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter,
            vmode,
        )

        self.qp.end()
