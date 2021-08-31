"""
Created on 8 Aug 2021.

@author: Ben Lauret
"""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)

from pyG5.pyG5View import pyG5DualStack, g5Width, g5Height

sliderWdith = 300


def controlWidgetGen(control):
    """Generate control widget.

    Args:
        control: dictionary containing name, min, max

    Returns:
        QWdiget
    """
    layout = QGridLayout()

    w = QWidget()
    w.setLayout(layout)

    layout.addWidget(QLabel(control["name"], parent=w), 0, 0)

    slider = QSlider(Qt.Horizontal, parent=w)
    slider.setRange(control["min"], control["max"])

    spinbox = QSpinBox(parent=w)
    spinbox.setRange(control["min"], control["max"])

    slider.valueChanged.connect(spinbox.setValue)
    spinbox.valueChanged.connect(slider.setValue)

    layout.addWidget(slider, 0, 1)
    layout.addWidget(spinbox, 0, 2)

    return (w, slider)


def makeControlDict(name, min, max):
    """Generate control dictionary.

    Args:
        name: string
        min: int
        max: int

    Returns:
        dictionary
    """
    return {"name": name, "min": min, "max": max}


if __name__ == "__main__":
    # Create an PyQT4 application object.
    a = QApplication(sys.argv)

    # The QWidget widget is the base class of all user interface objects in PyQt4.
    w = QMainWindow()

    # Set window size.
    w.resize(sliderWdith + g5Width, g5Height)

    # Set window title
    w.setWindowTitle("Garmin G5")
    file_menu = QMenu("&File", w)
    file_menu.addAction("&Quit", w.close, Qt.CTRL + Qt.Key_W)

    menuBar = w.menuBar()
    menuBar.addMenu(file_menu)

    hlayout = QHBoxLayout()
    mainWidget = QWidget()
    mainWidget.setLayout(hlayout)

    scrollArea = QScrollArea(w)
    controlWidget = QWidget(w)
    scrollArea.setWidget(controlWidget)
    scrollArea.setFixedWidth(380)
    scrollArea.setMinimumHeight(160)
    scrollArea.setWidgetResizable(True)
    scrollArea.setObjectName("scrollArea")
    controlVLayout = QVBoxLayout()
    controlWidget.setLayout(controlVLayout)
    hlayout.addWidget(scrollArea)

    g5View = pyG5DualStack()
    hlayout.addWidget(g5View)

    controls = [
        makeControlDict("magHeading", 0, 360),
        makeControlDict("groundTrack", 0, 360),
        makeControlDict("pitchAngle", -25, +25),
        makeControlDict("rollAngle", -70, +70),
        makeControlDict("kias", 0, 230),
        makeControlDict("kiasDelta", -30, 30),
        makeControlDict("gs", 0, 230),
        makeControlDict("altitude", -1000, 45000),
        makeControlDict("vh_ind_fpm", -1500, 1500),
        makeControlDict("turnRate", -130, 130),
        makeControlDict("slip", -10, 10),
        makeControlDict("headingBug", 0, 360),
        makeControlDict("windDirection", 0, 360),
        makeControlDict("windSpeed", 0, 200),
        makeControlDict("hsiSource", 0, 2),
        makeControlDict("nav1crs", 0, 360),
        makeControlDict("nav1dft", -3, 3),
        makeControlDict("nav1gsavailable", 0, 1),
        makeControlDict("nav1gs", -30, 30),
        makeControlDict("nav2crs", 0, 360),
        makeControlDict("nav2dft", -3, 3),
        makeControlDict("nav2gsavailable", 0, 1),
        makeControlDict("nav2gs", -30, 30),
        makeControlDict("gpscrs", 0, 360),
        makeControlDict("gpsdft", -3, 3),
        makeControlDict("gpsgsavailable", 0, 1),
        makeControlDict("gpsgs", -30, 30),
    ]

    for control in controls:
        widget, slider = controlWidgetGen(control)
        try:
            slider.valueChanged.connect(getattr(g5View.pyG5AI, control["name"]))
            slider.valueChanged.connect(getattr(g5View.pyG5HSI, control["name"]))
            print("Slider connected: {}".format(control["name"]))
        except Exception as inst:
            print("{} control not connected to view: {}".format(control["name"], inst))

        controlVLayout.addWidget(widget)
    controlVLayout.addStretch()

    w.setCentralWidget(mainWidget)
    # Show window
    w.show()

    sys.exit(a.exec_())

    pass
