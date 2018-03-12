# -*- coding: utf-8 -*-
#  Библиотека для работы с барометром
#  LPS331AP
#  MEMS pressure sensor: 260-1260 mbar absolute digital output barometer
#  Seliverstov Dmitriy 2017

import smbus


class LPS331AP(object):
    register = {
        'REF_P_XL'          : 0x08,
        'REF_P_L'           : 0x09,
        'REF_P_H'           : 0xA0,
        'WHO_AM_I'          : 0x0F,
        'RES_CONF'          : 0x10,
        'CTRL_REG1'         : 0x20,
        'CTRL_REG2'         : 0x21,
        'CTRL_REG3'	        : 0x22,
        'INT_CFG_REG'	    : 0x23,
        'INT_SOURCE_REG'    : 0x24,
        'THS_P_LOW_REG'     : 0x25,
        'THS_P_HIGH_REG'    : 0x26,
        'STATUS_REG'        : 0x27,
        'PRESS_POUT_XL_REH' : 0x28,
        'PRESS_OUT_L'	    : 0x29,
        'PRESS_OUT_H'	    : 0x2A,
        'TEMP_OUT_L'	    : 0x2B,
        'TEMP_OUT_H'	    : 0x2C,
        'AMP_CTRL'	        : 0x30,
        }

    pressure_measure = {
        'mmHg'              : 4096 * 1.3332237,       # 760mmHg = 1013,25 m bar = 101325 Pa
        'Pascal'            : 4096 * 0.01,            # 1 bar = 10000 Pa
        'mBar'              : 4096,                   # m bar output data
        'inchHg'            : 4096 * 33.86384,        # 760mmHg = 29,9213 inchHg
    }

    temperature_measure = {'C',
                           'K',
                           'F',
                           }

    output_data_rate = {
        'ONE SHOT'          : 0,  # One Shot
        'P(1Hz)T(1Hz)'      : 1,
        'P(7Hz)T(1Hz)'      : 2,
        'P(12,5Hz)T(1Hz)'   : 3,
        'P(25Hz)T(1Hz)'     : 4,
        'P(7Hz)T(7Hz)'      : 5,
        'P(12,5Hz)T(12,5Hz)': 6,
        'P(25Hz) T(25Hz)'   : 7,
    }

    # Default
    I2C_DEFAULT_ADDRESS_LOW = 0b1011100
    I2C_DEFAULT_ADDRESS_HIGH = 0b1011101
    I2C_IDENTITY = 0xbb

    DEFAULT_PRESSURE_MEASURE = 'mmHg'
    DEFAULT_TEMPERATURE_MEASURE = 'C'

    _ctrlReg1 = 0
    _ctrlReg2 = 0
    _ctrlReg3 = 0
    _address = I2C_DEFAULT_ADDRESS_LOW
    # Additional constants
    CELSIUS_TO_KELVIN_OFFSET = 273.15

    def __init__(self, port=1,
                 set_pressure_measure=DEFAULT_PRESSURE_MEASURE,
                 set_temperature_measure=DEFAULT_TEMPERATURE_MEASURE,
                 set_output_data_rate=output_data_rate['P(7Hz)T(7Hz)']):
        # Подключаемся к шине I2C
        self.wire = smbus.SMBus(port)
        # Устанавливаем адрес устройства
        if not self.auto_detect_address():
            print('cannot connect device in address ', self._address)
            return
        # Сброс всего по умолчанию
        self.soft_reset()
        # reboot
        self.reboot()
        # Включаем
        self.device_enable(True)
        # setup Output_data_rate
        self.setup_output_data_rate(set_output_data_rate)
        # Устанавливаем единицы измерения
        # Давления
        self._measure_of_pressure = set_pressure_measure
        # Температуры
        self._measure_of_temperature = set_temperature_measure

    def identity(self, address=_address):
        return self.wire.read_byte_data(address, self.register['WHO_AM_I']) == self.I2C_IDENTITY

    def auto_detect_address(self):
        # try each possible address and stop if reading WHO_AM_I returns the expected response
        if self.identity(self.I2C_DEFAULT_ADDRESS_LOW):
            self._address = self.I2C_DEFAULT_ADDRESS_LOW
            return self._address
        elif self.identity(self.I2C_DEFAULT_ADDRESS_HIGH):
            self._address = self.I2C_DEFAULT_ADDRESS_HIGH
            return self._address
        else:
            return False

    # Pressure read data
    def read_pressure_raw(self):
        # assert MSB to enable register address auto increment
        values = self.wire.read_i2c_block_data(self._address, self.register['PRESS_POUT_XL_REH'] | (1 << 7), 3)
        # Pressure output data: Pout(m bar)=(PRESS_OUT_H & PRESS_OUT_L & PRESS_OUT_XL)[dec]/4096
        return values[2] << 16 | values[1] << 8 | values[0]

    def read_pressure(self, measure=DEFAULT_PRESSURE_MEASURE):
        if measure in self.pressure_measure.keys():
            return self.read_pressure_raw() / self.pressure_measure[measure]
        else:
            return self.read_pressure_raw() / self.pressure_measure[self.DEFAULT_PRESSURE_MEASURE]

    # Temperature read data
    def read_temperature_raw(self):
        # assert MSB to enable register address auto increment
        return self.signed_int32(self.wire.read_word_data(self._address, self.register['TEMP_OUT_L'] | (1 << 7)))

    def read_temperature(self, measure=DEFAULT_TEMPERATURE_MEASURE):
        if measure in self.temperature_measure:
            return self.read_temperature_raw() / 480 + 42.5

    def read_temperature_k(self):
        return self.read_temperature_raw() / 480 + 42.5 + self.CELSIUS_TO_KELVIN_OFFSET

    def read_temperature_f(self):
        return self.read_temperature_raw() / 480 * 1.8 + 108.5

    # Register 1 operations
    # PD ODR2 ODR1 ODR0 DIFF_EN DBDU DELTA_EN SIM
    # Power-Down mode
    def device_enable(self, power=True):
        if power:
            self._ctrlReg1 |= (1 << 7)
        else:
            self._ctrlReg1 &= ~(1 << 7)
        self.wire.write_byte_data(self._address, self.register['CTRL_REG1'], self._ctrlReg1)

    def setup_output_data_rate(self, rate=output_data_rate['ONE SHOT']):
        self._ctrlReg1 |= (rate << 4)
        self.wire.write_byte_data(self._address, self.register['CTRL_REG1'], self._ctrlReg1)
        return

    # DIFF_EN bit is used to enable the circuitry for the computing of differential pressure output.
    # In default mode (DIF_EN=’0’) the circuitry is turned off. It is suggested to turn on
    # the circuitry only after the configuration of REF_P_x and THS_P_x
    def differential_pressure_output(self, enable=False):
        if enable:
            self._ctrlReg1 |= (1 << 3)
        else:
            self._ctrlReg1 &= ~(1 << 3)
        self.wire.write_byte_data(self._address, self.register['CTRL_REG1'], self._ctrlReg1)
        return

    def block_data_update(self, enable=False):
        if enable:
            self._ctrlReg1 |= (1 << 2)
        else:
            self._ctrlReg1 &= ~(1 << 2)
        self.wire.write_byte_data(self._address, self.register['CTRL_REG1'], self._ctrlReg1)
        return

    # Register 2 operations
    # BOOT RESERVED RESERVED RESERVED RESERVED SWRESET AUTO_ZERO ONE_SHOT
    def reboot(self):
        # Reboot memory content. Default value: 0 (0: normal mode; 1: reboot memory content)
        # BOOT bit is used to refresh the content of the internal registers stored in the Flash memory block.
        # At the device power-up the content of the Flash memory block is transferred to the internal registers
        # related to trimming functions to permit a good behavior of the device itself. If for any reason, the
        # content of the trimming registers is modified, it is sufficient to use this bit to restore the correct
        # values. When BOOT bit is set to ‘1’ the content of the internal Flash is copied inside the corresponding
        # internal registers and is used to calibrate the device. These values are factory trimmed and they are
        # different for every device. They permit good behavior of the device and normally they should not be
        # changed. At the end of the boot process the BOOT bit is set again to ‘0’.
        # BOOT bit takes effect after one ODR clock cycle.
        self.wire.write_byte_data(self._address, self.register['CTRL_REG2'], self._ctrlReg2 | (1 << 7))
        return

    def soft_reset(self):
        self._ctrlReg1, self._ctrlReg2 = 0, 0
        # Configuration registers and user register reset function. (0: Default value; 1: Reset operation)
        # SWRESET is the software reset bit. The device is reset to the power on configuration
        # if the SWRESET bit is set to ‘1’ and BOOT is set to ‘1’.
        self.wire.write_byte_data(self._address, self.register['CTRL_REG2'], self._ctrlReg2 | (1 << 2))

    def auto_zero(self, enable=False):
        # AUTO_ZERO, when set to ‘1’, the actual pressure output is copied in the REF_P_H & REF_P_L & REF_P_XL
        # and kept as reference and the PRESS_OUT_H & PRESS_OUT_L & PRESS _OUT_XL
        # is the difference between this reference and the pressure sensor value.
        if enable:
            self._ctrlReg2 |= (1 << 1)
        else:
            self._ctrlReg2 &= ~(1 << 1)
        self.wire.write_byte_data(self._address, self.register['CTRL_REG2'], self._ctrlReg2)
        return

    def one_shot(self, enable):
        # ONE_SHOT bit is used to start a new conversion when ODR1-ODR0 bits in CTRL_REG1 are set to “000”.
        # In this situation a single acquisition of temperature and pressure is started when ONE_SHOT bit is set to
        # ‘1’. At the end of conversion the new data are available in the output registers, the STAUS_REG[0]
        # and STAUS_REG[1] bits are set to ‘1’ and the ONE_SHOT bit comes back to ‘0’ by hardware.
        if enable:
            self._ctrlReg1 |= (self.output_data_rate['ONE SHOT'] << 4)
            self._ctrlReg2 |= 0b1
        else:
            self._ctrlReg2 &= ~0b1
        self.wire.write_byte_data(self._address, self.register['CTRL_REG2'], self._ctrlReg2)
        return

    @staticmethod
    def signed_int32(number):
        if number & (1 << 15):
            return number | ~65535
        else:
            return number & 65535
