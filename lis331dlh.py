# -*- coding: utf-8 -*-
#   Библиотека для работы с датчиком ускорения
#   LIS331DLH
#   MEMS digital output motion sensor ultra low-power high performance 3-axes “nano” accelerometer
import smbus


class LIS331DLH(object):
    register = {
        'WHO_AM_I'	: 0x0F,
        'CTRL_REG1'			: 0x20,
        'CTRL_REG2'			: 0x21,
        'CTRL_REG3'			: 0x22,
        'CTRL_REG4'			: 0x23,
        'CTRL_REG5'			: 0x24,
        'HP_FILTER_RESET'   : 0x25,
        'REFERENCE'			: 0x26,
        'STATUS_REG'        : 0x27,
        'OUT_X_L'			: 0x28,
        'OUT_X_H'			: 0x29,
        'OUT_Y_L'			: 0x2A,
        'OUT_Y_H'			: 0x2B,
        'OUT_Z_L'			: 0x2C,
        'OUT_Z_H'			: 0x2D,
        'INT1_CFG'			: 0x30,
        'INT1_SRC'			: 0x31,
        'INT1_THS'			: 0x32,
        'INT1_DURATION'		: 0x33,
        'INT2_CFG'			: 0x34,
        'INT2_SRC' 			: 0x35,
        'INT2_THS'			: 0x36,
        'INT2_DURATION'		: 0x37,
    }

    range_fs = (
        '2G',
        '4G',
        '8G')

    mult_sens = {
        '2G'                : 2 / 32767.0,
        '4G'                : 4 / 32767.0,
        '8G'                : 8 / 32767.0,
    }

    adr_fs_conf = {
        '2G'                : 0x00,
        '4G'                : 0x10,
        '8G'                : 0x30,
    }

    output_data_rate = {
        'LOW POWER 0,5Hz'   : 0b01000,
        'LOW POWER 1Hz'     : 0b01100,
        'LOW POWER 2Hz'     : 0b10000,
        'LOW POWER 5Hz'     : 0b10100,
        'LOW POWER 10Hz'    : 0b11000,
        'NORMAL 50Hz'       : 0b00100,
        'NORMAL 1O0Hz'      : 0b00101,
        'NORMAL 400Hz'      : 0b00110,
        'NORMAL 1000Hz'     : 0b00111,
    }

    I2C_DEFAULT_ADDRESS = 0b0011000
    I2C_IDENTITY = 0x32

    _mult = mult_sens[range_fs[0]]
    _ctrlReg1 = 0
    _ctrlReg2 = 0
    _ctrlReg3 = 0
    _ctrlReg4 = 0
    _ctrlReg5 = 0
    # Additional constants
    G = 9.8

    def __init__(self, port=1,
                 address=I2C_DEFAULT_ADDRESS,
                 sens_range=range_fs[0],
                 data_rate=output_data_rate['NORMAL 50Hz']):
        # Подключаемся к шине I2C
        self.wire = smbus.SMBus(port)
        # Запоминаем адрес
        self._addr = address
        # Сбрасываем все регистры по умолчанию
        self.reboot()
        # Устанавливаем чувствительность
        self.set_range(sens_range)
        # Устанавливаем чувствительность (Установка ODR включает прибор)
        self.set_output_data_rate(data_rate)
        # x axis enable
        self.axis_x(True)
        # y axis enable
        self.axis_y(True)
        # z axis enable
        self.axis_z(True)

    def identity(self):
        return self.wire.read_byte_data(self._addr, self.register['WHO_AM_I']) == self.I2C_IDENTITY

    # Register 1 operations
    # PM2 PM1 PM0 DR1 DR0 Zen Yen Xen
    # Power-Down mode
    # PM2 - PM0 Power mode selection. Default value: 000 (000: Power-down; Others: refer to Table 19)
    def enable(self, power=True):
        if power:
            self._ctrlReg1 &= 0x1f
            self._ctrlReg1 |= (1 << 5)
        else:
            self._ctrlReg1 &= 0x1f
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG1'], self._ctrlReg1)

    # Data rate selection. Default value: 00 (00:50 Hz; Others: refer to Table 20)
    def set_output_data_rate(self, rate=output_data_rate['NORMAL 50Hz']):
        self._ctrlReg1 &= 0x7
        self._ctrlReg1 |= (rate << 3)
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

    # Register 2 operations
    # BOOT HPM1 HPM0 FDS HPen2 HPen1 HPCF1 HPCF0
    # Reboot memory content. Default value: 0 (0: normal mode; 1: reboot memory content)
    def reboot(self):
        # Reboot memory content. Default value: 0 (0: normal mode; 1: reboot memory content)
        self.wire.write_byte_data(self._addr, self.register['CTRL_REG2'], self._ctrlReg2 | (1 << 7))

    # Register 4 operations
    # BDU BLE FS1 FS0 STsign 0 ST SIM
    # устанавливаем максимальное измеряемое ускорение в G
    def set_range(self, sens_range=range_fs[0]):
        if sens_range in self.range_fs:
            self._ctrlReg4 &= 0x30      # Clear
            self._ctrlReg4 |= self.adr_fs_conf[sens_range]
            self._mult = self.mult_sens[sens_range]
            self.wire.write_byte_data(self._addr, self.register['CTRL_REG4'], self._ctrlReg4)

    def read_axis(self, reg):
        # assert MSB to enable register address auto increment
        return self.segned_int32(self.wire.read_word_data(self._addr, reg | (1 << 7)))

    def read_xyz(self):
        # assert MSB to enable register address auto increment
        values = self.wire.read_i2c_block_data(self._addr, self.register['OUT_X_L'] | (1 << 7), 6)
        return (self.segned_int32(values[1] << 8 | values[0]),
                self.segned_int32(values[3] << 8 | values[2]),
                self.segned_int32(values[5] << 8 | values[4]))

    def read_gx(self):
        return self.read_axis(self.register['OUT_X_L']) * self._mult

    def read_gy(self):
        return self.read_axis(self.register['OUT_Y_L']) * self._mult

    def read_gz(self):
        return self.read_axis(self.register['OUT_Z_L']) * self._mult

    def read_ax(self):
        return self.read_axis(self.register['OUT_X_L']) * self._mult * self.G

    def read_ay(self):
        return self.read_axis(self.register['OUT_Y_L']) * self._mult * self.G

    def read_az(self):
        return self.read_axis(self.register['OUT_Z_L']) * self._mult * self.G

    def read_gxyz(self):
        gx, gy, gz = self.read_xyz()
        return gx * self._mult, gy * self._mult, gz * self._mult

    def read_axyz(self):
        gx, gy, gz = self.read_xyz()
        return gx * self._mult * self.G, gy * self._mult * self.G, gz * self._mult * self.G

    @staticmethod
    def segned_int32(number):
        if number & (1 << 15):
            return number | ~65535
        else:
            return number & 65535
