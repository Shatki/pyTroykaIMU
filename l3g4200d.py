# -*- coding: utf-8 -*-
#
# L3G4200D gyroscope control class
# MEMS motion sensor: ultra-stable three-axis digital output gyroscope
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

import smbus


class L3G4200D(object):
    register = {
        'WHO_AM_I'          : 0x0F,
        'CTRL_REG1'         : 0x20,
        'CTRL_REG2'	        : 0x21,
        'CTRL_REG3'		    : 0x22,
        'CTRL_REG4'		    : 0x23,
        'CTRL_REG5'		    : 0x24,
        'REFERENCE'		    : 0x25,
        'OUT_TEMP'          : 0x26,
        'STATUS_REG'        : 0x27,
        'OUT_X_L'		    : 0x28,
        'OUT_X_H'		    : 0x29,
        'OUT_Y_L'		    : 0x2A,
        'OUT_Y_H'		    : 0x2B,
        'OUT_Z_L'		    : 0x2C,
        'OUT_Z_H'		    : 0x2D,
        'FIFO_CTRL_REG'     : 0x2E,
        'FIFO_SRC_REG'      : 0x2F,
        'INT1_CFG'		    : 0x30,
        'INT1_SRC'		    : 0x31,
        'INT1_THS_XH'	    : 0x32,
        'INT1_TSH_XL'	    : 0x33,
        'INT1_TSH_YH'	    : 0x34,
        'INT1_TSH_YL' 	    : 0x35,
        'INT1_TSH_ZH'       : 0x36,
        'INT1_TSH_ZL'	    : 0x37,
        'INT1_DURATION'	    : 0x38,
    }

    range_fs = (
        '250',
        '500',
        '2000',)

    adr_fs_conf = {
        '250'               : 0x00,
        '500'               : 0x10,
        '2000'              : 0x20,
    }

    sens_fs = {
        '250'               : 0.00875,
        '500'               : 0.0175,
        '2000'              : 0.07,
    }

    # Default
    I2C_DEFAULT_ADDRESS = 0b01101000
    I2C_IDENTITY = 0xD3

    _mult = sens_fs[range_fs[0]]
    _addr = 0
    _ctrlReg1 = 0
    _ctrlReg2 = 0
    _ctrlReg3 = 0
    _ctrlReg4 = 0
    _ctrlReg5 = 0
    # Additional constants
    DEG_TO_RAD = 0.0175

    def __init__(self, port=1,
                 address=I2C_DEFAULT_ADDRESS,
                 sens_range=range_fs[0]):
        # Подключаемся к шине I2C
        self.wire = smbus.SMBus(port)
        # Запоминаем адрес
        self._addr = address
        # Сбрасываем все регистры по умолчанию
        self.reboot()
        # Устанавливаем чувствительность
        self.set_range(sens_range)
        # Влючаем
        self.enable()
        # x axis enable
        self.axis_x(True)
        # y axis enable
        self.axis_y(True)
        # z axis enable
        self.axis_z(True)

    def identity(self):
        return self.wire.read_byte_data(self._addr, self.register['WHO_AM_I']) == self.I2C_IDENTITY

    # Register 1 operations
    # CtrlReg1  - DR1 DR0 BW1 BW0 PD Zen Yen Xen
    # Power-Down mode
    # Power down mode enable. Default value: 0 (0: power down mode, 1: normal mode or sleep mode)
    def enable(self, power=True):
        if power:
            self._ctrlReg1 |= (1 << 3)
        else:
            self._ctrlReg1 &= ~(1 << 3)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG1'], self._ctrlReg1)

    # X axis enable. Default value: 1 (0: X axis disabled; 1: X axis enabled)
    def axis_x(self, enable=True):
        if enable:
            self._ctrlReg1 |= (1 << 0)
        else:
            self._ctrlReg1 &= ~(1 << 0)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG1'], self._ctrlReg1)

    # Y axis enable. Default value: 1 (0: Y axis disabled; 1: Y axis enabled)
    def axis_y(self, enable=True):
        if enable:
            self._ctrlReg1 |= (1 << 1)
        else:
            self._ctrlReg1 &= ~(1 << 1)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG1'], self._ctrlReg1)

    # Z axis enable. Default value: 1 (0: Z axis disabled; 1: Z axis enabled)
    def axis_z(self, enable=True):
        if enable:
            self._ctrlReg1 |= (1 << 2)
        else:
            self._ctrlReg1 &= ~(1 << 2)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG1'], self._ctrlReg1)

    # Register 4 operations
    # BDU BLE FS1 FS0 - ST1 ST0 SIM
    def set_range(self, sens_range=range_fs[0]):
        if sens_range in self.range_fs:
            self._ctrlReg4 = self.adr_fs_conf[sens_range]
            self._mult = self.sens_fs[sens_range]
            self.wire.write_byte_data(self._addr, self.register['CTRL_REG4'], self._ctrlReg4)

    # Register 5 operations
    # BOOT FIFO_EN -- HPen INT1_Sel1 INT1_Sel0 Out_Sel1 Out_Sel0
    def reboot(self):
        # Reboot memory content. Default value: 0 (0: normal mode; 1: reboot memory content)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG5'], self._ctrlReg5 | (1 << 7))

    def read_axis(self, reg):
        # assert MSB to enable register address auto increment
        return self.signed_int32(self.wire.read_word_data(self._addr, reg | (1 << 7)))

    def read_xyz(self):
        # assert MSB to enable register address auto increment
        values = self.wire.read_i2c_block_data(self._addr, self.register['OUT_X_L'] | (1 << 7), 6)
        return (self.signed_int32(values[1] << 8 | values[0]),
                self.signed_int32(values[3] << 8 | values[2]),
                self.signed_int32(values[5] << 8 | values[4]))

    def read_degrees_per_second_xyz(self):
        x, y, z = self.read_xyz()
        return x * self._mult, y * self._mult, z * self._mult

    def read_radians_per_second_xyz(self):
        x, y, z = self.read_xyz()
        return x * self._mult * self.DEG_TO_RAD, y * self._mult * self.DEG_TO_RAD, z * self._mult * self.DEG_TO_RAD

    def read_x(self):
        return self.read_axis(self.register['OUT_X_L'])

    def read_y(self):
        return self.read_axis(self.register['OUT_Y_L'])

    def read_z(self):
        return self.read_axis(self.register['OUT_Z_L'])

    def read_degrees_per_second_x(self):
        return self.read_x() * self._mult

    def read_degrees_per_second_y(self):
        return self.read_y() * self._mult

    def read_degrees_per_second_z(self):
        return self.read_z() * self._mult

    def read_radians_per_second_x(self):
        return self.read_x() * self._mult * self.DEG_TO_RAD

    def read_radians_per_second_y(self):
        return self.read_y() * self._mult * self.DEG_TO_RAD

    def read_radians_per_second_z(self):
        return self.read_z() * self._mult * self.DEG_TO_RAD

    @staticmethod
    def signed_int32(number):
        if number & (1 << 15):
            return number | ~65535
        else:
            return number & 65535
