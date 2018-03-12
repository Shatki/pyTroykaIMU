# -*- coding: utf-8 -*-
"""
 * Partial implementation of standard atmospheric model as described in 
 * GOST 4401-81 useful for processing of data from meteorological balloon 
 * sensors.
 *
 * Supported modelling of temperature and pressure over the altitude span from
 * 0 up to 51km.
 *  
 * algorithm by Oleg Kochetov <ok@noiselab.ru>
 """

from math import log10

class GOST4401(object):
    G = 9.80665
    R = 287.05287
    E = 6356766
    MIN_PRESSURE = 6.69384
    MAX_PRESSURE = 101325.00
    MIN_GP_ALT = 0.00
    MAX_GP_ALT = 51000.00

    # Lookup table with averaged empirical parameters for
    # lower layers of atmosphere in accordance with ГОСТ 4401-81
    LUT_RECORDS = 6
    tab = {
        'altitude'          :   0,  # Geopotentional altitude
        'temperature'       :   1,  # degrees K
        'temp gradient'     :   2,  # degrees K per meter
        'pressure'          :   3,  # pascals
    }

    ag_table = [
        [0, 288.15, -0.0065, 101325.00],
        [11000, 216.65, 0.0, 22632.04],
        [20000, 216.65, 0.0010, 5474.87],
        [32000, 228.65, 0.0028, 868.0146],
        [47000, 270.65, 0.0, 110.9056],
        [51000, 270.65, -0.0028, 6.69384]
    ]

    @staticmethod
    def geopotential_to_geometric(self, altitude):
        return altitude * self.E / (self.E - altitude)

    @staticmethod
    def geometric_to_geopotential(self, altitude):
        return altitude * self.E / (self.E + altitude)

    def get_altitude(self, pressure):
        """
        Returns geometric altitude value for the given pressure.

        :param pressure: float pressure - pressure in pascals
        :return: float geometric altitude in meters
        """
        # Pressure in Pascals
        if (pressure <= self.MIN_PRESSURE) or (pressure > self.MAX_PRESSURE):
            return None

        for idx in range(0, self.LUT_RECORDS - 1):
            if ((pressure <= self.ag_table[idx][self.tab['pressure']]) and
                    (pressure > self.ag_table[idx + 1][self.tab['pressure']])):
                break
        Ps = float(self.ag_table[idx][self.tab['pressure']])
        Bm = float(self.ag_table[idx][self.tab['temp gradient']])
        Tm = float(self.ag_table[idx][self.tab['temperature']])
        Hb = float(self.ag_table[idx][self.tab['altitude']])

        if Bm != 0:
            geopot_H = ((Tm * pow(Ps / pressure, Bm * self.R / self.G) - Tm) / Bm)
        else:
            geopot_H = log10(Ps / pressure) * (self.R * Tm) / self.G * 0.434292

        return self.geopotential_to_geometric(self, Hb + geopot_H)

    def get_pressure(self, altitude):
        """
        Returns pressure in pascals for the given geometric altitude

        :param altitude: float altitude - geometric altitude in meters
        :return: float - pressure in pascals
        """
        geopot_H = self.geometric_to_geopotential(self, altitude)
        if (geopot_H < self.MIN_GP_ALT) or (geopot_H >= self.MAX_GP_ALT):
            return None

        for idx in range(0, self.LUT_RECORDS - 1):
            if ((geopot_H >= self.ag_table[idx][self.tab['altitude']]) and
                    (geopot_H < self.ag_table[idx + 1][self.tab['altitude']])):
                break

        Ps = float(self.ag_table[idx][self.tab['pressure']])
        Bm = float(self.ag_table[idx][self.tab['temp gradient']])
        Tm = float(self.ag_table[idx][self.tab['temperature']])
        Hb = float(self.ag_table[idx][self.tab['altitude']])

        if Bm != 0:
            lP = log10(Ps) - (self.G / (Bm * self.R)) * log10((Tm + Bm * (geopot_H - Hb)) / Tm)
        else:
            lP = log10(Ps) - 0.434294 * (self.G * (geopot_H - Hb)) / (self.R * Tm)

        return pow(10, lP)

    def get_temperature(self, altitude):
        """
        Returns temperature value in K for the given geometric altitude.

        :param altitude: float altitude - geometric altitude in meters
        :return: float - temperature in degrees K
        """
        geopot_H = self.geometric_to_geopotential(self, altitude)
        if (geopot_H < self.MIN_GP_ALT) or (geopot_H >= self.MAX_GP_ALT):
            return None

        for idx in range(0, self.LUT_RECORDS - 1):
            if ((geopot_H >= self.ag_table[idx][self.tab['altitude']]) and
                    (geopot_H < self.ag_table[idx + 1][self.tab['altitude']])):
                break

        Bm = float(self.ag_table[idx][self.tab['temp gradient']])
        Tm = float(self.ag_table[idx][self.tab['temperature']])
        Hb = float(self.ag_table[idx][self.tab['altitude']])
        temp = Tm

        if Bm != 0:
            temp += Bm * (geopot_H - Hb)

        return temp
