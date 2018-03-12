# -*- coding: utf-8 -*-
#
# LIS3MDL maggnetic sensor control class
# Digital output magnetic sensor: ultra-low-power, high-performance 3-axis magnetometer
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
from math import atan2, pi, degrees


class LIS3MDL:
    register = {
        'WHO_AM_I'			: 0x0F,
        'CTRL_REG1'			: 0x20,
        'CTRL_REG2'			: 0x21,
        'CTRL_REG3'			: 0x22,
        'CTRL_REG4'			: 0x23,
        'CTRL_REG5'			: 0x24,
        'STATUS_REG'        : 0x27,
        'OUT_X_L'			: 0x28,
        'OUT_X_H'			: 0x29,
        'OUT_Y_L'			: 0x2A,
        'OUT_Y_H'			: 0x2B,
        'OUT_Z_L'			: 0x2C,
        'OUT_Z_H'			: 0x2D,
        'TEMP_OUT_L'        : 0x2E,
        'TEMP_OUT_H'        : 0x2F,
        'INT_CFG'			: 0x30,
        'INT_SRC'			: 0x31,
        'INT_THS_L'			: 0x32,
        'INT_THS_H'			: 0x33,
        }

    range_fs = (
        '4_GAUSS',
        '8_GAUSS',
        '12_GAUSS',
        '16_GAUSS',)

    adr_fs_conf = {
        '4_GAUSS'           : 0b00000000,
        '8_GAUSS'           : 0b00100000,
        '12_GAUSS'          : 0b01000000,
        '16_GAUSS'          : 0b01100000,
    }

    sens_fs = {
        '4_GAUSS'           : 6842,
        '8_GAUSS'           : 3421,
        '12_GAUSS'          : 2281,
        '16_GAUSS'          : 1711,
    }

    axis_operation_mode = {
        'LOW_POWER'         : 0b00000000,      # Low-power mode
        'MEDIUM_PERF'       : 0b00100000,      # Medium-performance mode
        'HIGH_PERF'         : 0b01000000,      # High-performance mode
        'ULTRA_HIGH_PERF'   : 0b01100000,      # Ultra-High-performance mode
    }
    
    configuration = {
        'ODR_0625'          : 0b0000000,      # 0.625 Hz
        'ODR_125'           : 0b0000100,      # 1.25  Hz
        'ODR_25'            : 0b0001000,      # 2.5   Hz
        'ODR_5'             : 0b0001100,      # 5     Hz
        'ODR_10'            : 0b0010000,      # 10    Hz
        'ODR_20'            : 0b0010100,      # 20    Hz
        'ODR_40'            : 0b0011000,      # 40    Hz
        'ODR_80'            : 0b0011100,      # 80    Hz
    }
    # Default
    I2C_DEFAULT_ADDRESS = 0b0011100
    I2C_IDENTITY = 0x3d

    _mult = sens_fs[range_fs[0]]
    _ctrlReg1 = 0
    _ctrlReg2 = 0
    _ctrlReg3 = 0
    _ctrlReg4 = 0
    _ctrlReg5 = 0

    _calibration_matrix = [[0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0],
                           [0.0, 0.0, 0.0]]

    _bias = [0.0, 0.0, 0.0]

    def __init__(self, port=1,
                 address=I2C_DEFAULT_ADDRESS,
                 sens_range=range_fs[0],
                 temperature_sensor_enable=True,
                 axis_operation_mode=axis_operation_mode['ULTRA_HIGH_PERF'],
                 output_data_rate=configuration['ODR_80']
                 ):
        # Подключаемся к шине I2C
        self.wire = smbus.SMBus(port)
        # Запоминаем адрес
        self._addr = address
        # Сбрасываем все регистры по умолчанию
        self.soft_reset()
        # Устанавливаем чувствительность
        self.set_range(sens_range)
        # Влючаем
        self.enable()
        # Temperature sensor enable
        self.temperature_sensor(temperature_sensor_enable)
        # Ultra High Performance Mode Selected for XY Axis
        self.operation_mode_xy_axis(axis_operation_mode)
        # Ultra High Performance Mode Selected for Z Axis
        self.operation_mode_z_axis(axis_operation_mode)
        # Output Data Rate of 80 Hz Selected
        self.output_data_rate(output_data_rate)

    def identity(self):
        return self.wire.read_byte_data(self._addr, self.register['WHO_AM_I']) == self.I2C_IDENTITY

    # Register 1 operations
    # TEMP_EN OM1 OM0 DO2 DO1 DO0 FAST_ODR ST
    # Temperature sensor enable. Default value: 0
    # (0: temperature sensor disabled; 1: temperature sensor enabled)
    def temperature_sensor(self, enable=False):
        if enable:
            self._ctrlReg1 |= (1 << 7)
        else:
            self._ctrlReg1 &= ~(1 << 7)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG1'], self._ctrlReg1)

    # X and Y axes operative mode selection. Default value: 00
    def operation_mode_xy_axis(self, mode=axis_operation_mode['LOW_POWER']):
        self._ctrlReg1 |= mode
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG1'], self._ctrlReg1)

    # Output data rate selection. Default value: 100
    def output_data_rate(self, rate=configuration['ODR_10']):
        self._ctrlReg1 |= rate
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG1'], self._ctrlReg1)

    # FAST_ODR enables data rates higher than 80 Hz. Default value: 0
    # (0: Fast_ODR disabled; 1: FAST_ODR enabled)
    def fast_odr(self, enable=False):
        if enable:
            self._ctrlReg1 |= (1 << 1)
        else:
            self._ctrlReg1 &= ~(1 << 1)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG1'], self._ctrlReg1)

    # Self-test enable. Default value: 0 (0: self-test disabled; 1: self-test enabled)
    def self_test(self, enable=False):
        if enable:
            self._ctrlReg1 |= (1 << 0)
        else:
            self._ctrlReg1 &= ~(1 << 0)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG1'], self._ctrlReg1)

    # Register 2 operations
    # 0 FS1 FS0 0 REBOOT SOFT_RST 0 0
    # Full-scale configuration. Default value: 00
    def set_range(self, sens_range=range_fs[0]):
        if sens_range in self.range_fs:
            self._ctrlReg2 = self.adr_fs_conf[sens_range]
            self._mult = self.sens_fs[sens_range]
            self.wire.write_byte_data(self._addr, self.register['CTRL_REG2'], self._ctrlReg2)

    def soft_reset(self):
        # Configuration registers and user register reset function. (0: Default value; 1: Reset operation)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG2'], self._ctrlReg2 | (1 << 2))

    def reboot(self):
        # Reboot memory content. Default value: 0 (0: normal mode; 1: reboot memory content)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG2'], self._ctrlReg2 | (1 << 3))

    # Register 3 operations
    # 0 0 LP 0 0 SIM MD1 MD0
    # Low-power mode configuration. Default value: 0
    # If this bit is ‘1’, DO[2:0] is set to 0.625 Hz and the system performs, for each channel,
    # the minimum number of averages. Once the bit is set to ‘0’,
    # the magnetic data rate is configured by the DO bits in CTRL_REG1 (20h) register.
    def low_power(self):
        self._ctrlReg3 |= (1 << 5)
        self._ctrlReg1 |= self.configuration['ODR_0625']
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG3'], self._ctrlReg3)

    # Power-Down mode
    def enable(self, power=True):
        if power:
            self._ctrlReg3 |= (3 << 0)
        else:
            self._ctrlReg3 &= ~(3 << 0)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG3'], self._ctrlReg3)

    # Register 4 operations
    # 0 0 0 0 OMZ1 OMZ0 BLE 0
    # X and Y axes operative mode selection. Default value: 00
    def operation_mode_z_axis(self, mode=axis_operation_mode['LOW_POWER']):
        self._ctrlReg4 |= (mode >> 3)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG4'], self._ctrlReg4)

    # Register 5 operations
    # FAST_READ BDU 0 0 0 0 0 0
    def fast_read(self, enable=False):
        if enable:
            self._ctrlReg5 |= (1 << 7)
        else:
            self._ctrlReg5 &= ~(1 << 7)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG5'], self._ctrlReg5)

    # Getting data operations
    def read_axis(self, reg):
        # assert MSB to enable register address auto increment
        return self.get_signed_number(self.wire.read_word_data(self._addr, reg | (1 << 7)))

    def read_xyz(self):
        # assert MSB to enable register address auto increment
        values = self.wire.read_i2c_block_data(self._addr, self.register['OUT_X_L'] | (1 << 7), 6)
        return (self.get_signed_number(values[1] << 8 | values[0]),
                self.get_signed_number(values[3] << 8 | values[2]),
                self.get_signed_number(values[5] << 8 | values[4]))

    def read_gauss_x(self):
        return self.read_axis(self.register['OUT_X_L']) / self._mult

    def read_gauss_y(self):
        return self.read_axis(self.register['OUT_Y_L']) / self._mult

    def read_gauss_z(self):
        return self.read_axis(self.register['OUT_Z_L']) / self._mult

    def read_gauss_xyz(self):
        gauss = self.read_xyz()
        return gauss[0] / self._mult, gauss[1] / self._mult, gauss[2] / self._mult

    def read_calibrate(self):
        return self.calibrate()

    def read_calibrate_gauss(self):
        calibrate_gauss = self.read_calibrate()
        return calibrate_gauss[0] / self._mult, calibrate_gauss[1] / self._mult, calibrate_gauss[2] / self._mult

    def calibrate(self):
        calibrated_values = [0.0, 0.0, 0.0]
        uncalibrated_values = self.read_xyz()
        # for i in range(0, 3):
        #    uncalibrated_values[i] -= self._bias[i]
        for i in range(0, 3):
            for j in range(0, 3):
                calibrated_values[i] += self._calibration_matrix[i][j] * (uncalibrated_values[j] - self._bias[j])
        return calibrated_values

    def calibrate_matrix(self, calibration_matrix, bias):
        self._bias = bias
        self._calibration_matrix = calibration_matrix
        return None

    def read_azimut(self):
        calibration = self.calibrate()
        two_pi = 2 * pi
        heading = atan2(calibration[1], calibration[0])
        if heading < 0:
            heading += two_pi
        elif heading > two_pi:
            heading -= two_pi
        return degrees(heading)

    @staticmethod
    def get_signed_number(number):
        if number & (1 << 15):
            return number | ~65535
        else:
            return number & 65535
