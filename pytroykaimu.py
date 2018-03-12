# -*- coding: utf-8 -*-
#
# pyTroykaIMU Inertial measurement unit control class
#
# Copyright 2016 Seliverstov Dmitriy <selidimail@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#
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
