# -*- coding: utf-8 -*-
from lis3mdl import LIS3MDL
from time import sleep
import numpy
from numpy import linalg
"""
cal_lib.py - Ellipsoid into Sphere calibration library based upon numpy and linalg
Copyright (C) 2012 Fabio Varesano <fabio at varesano dot net>

Development of this code has been supported by the Department of Computer Science,
Universita' degli Studi di Torino, Italy within the Piemonte Project
http://www.piemonte.di.unito.it/


This program is free software: you can redistribute it and/or modify
it under the terms of the version 3 GNU General Public License as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

def callibration():
    print("################################################")
    print("Please twirl your device around a minute...")
    print("The experimental data will stored to LIS3MDL_calibr.txt file")
    print("Please use this file to calculate calibration matrix by Magneto software.")
    print("################################################")
    f = open('LIS3MDL_calibrate.txt', 'w')
    for i in range(0, 50):
        print("Номер ", i*100)
        for num in range(0, 100):
            data = magneto.read_gauss_xyz()
            f.write(str(data[0])+'\t'+str(data[1])+'\t'+str(data[2])+'\n')
            sleep(0.05)
    f.close()

def real_time_calibration(n=100):
    print("################################################")
    print("Please twirl your device around a minute...")
    print("The experimental data will get to array")
    print("This may take a moment to get your calculation data as scale and offsets values ")
    print("################################################")
    samples_x = []
    samples_y = []
    samples_z = []

    for num in range(0, n):
        x, y, z = magneto.read_xyz
        samples_x.append(float(x))
        samples_y.append(float(y))
        samples_z.append(float(z))
        sleep(0.07)
        array_x = numpy.array(samples_x)
        array_y = numpy.array(samples_y)
        array_z = numpy.array(samples_z)

    H = numpy.array([array_x, array_y, array_z, -array_y**2, -array_z**2, numpy.ones([len(array_x), 1])])
    H = numpy.transpose(H)
    w = array_x**2

    (X, residues, rank, shape) = linalg.lstsq(H, w)

    OSx = X[0] / 2
    OSy = X[1] / (2 * X[3])
    OSz = X[2] / (2 * X[4])

    A = X[5] + OSx**2 + X[3] * OSy**2 + X[4] * OSz**2
    B = A / X[3]
    C = A / X[4]

    SCx = numpy.sqrt(A)
    SCy = numpy.sqrt(B)
    SCz = numpy.sqrt(C)

    # type conversion from numpy.float64 to standard python floats
    offsets = [OSx, OSy, OSz]
    scale = [SCx, SCy, SCz]

    offsets = map(numpy.asscalar, offsets)
    scale = map(numpy.asscalar, scale)


    return (offsets, scale)



magneto = LIS3MDL()

#offsets, scale = real_time_calibration()
callibration()

#print('offsets:')
#for item in offsets:
#    print(item)

#print('scale:')
#for item in scale:
#    print(item)
