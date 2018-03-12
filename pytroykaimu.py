# -*- coding: utf-8 -*-
from lis331dlh import LIS331DLH     # Акселерометр
from l3g4200d import L3G4200D       # Гироскоп
from lis3mdl import LIS3MDL         # Магнитометр
from lps331ap import LPS331AP       # Барометр


class pyTroykaIMU(object):
    def __init__(self):
        self.accelerometer = LIS331DLH()
        self.gyroscope = L3G4200D()
        self.magnetometer = LIS3MDL()
        self.barometer = LPS331AP()
