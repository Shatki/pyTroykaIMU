import smbus
import time
import math

bus = smbus.SMBus(1)


def writeMag(register, value):
    bus.write_byte_data(0x1C, register, value)
    return -1


def readMagx():
    Mag_l = bus.read_byte_data(0x1C, 0x28)
    Mag_h = bus.read_byte_data(0x1C, 0x29)
    Mag_total = (Mag_l | Mag_h << 8)
    return Mag_total if Mag_total < 32768 else Mag_total - 65536


def readMagy():
    Mag_l = bus.read_byte_data(0x1C, 0x2A)
    Mag_h = bus.read_byte_data(0x1C, 0x2B)
    Mag_total = (Mag_l | Mag_h << 8)
    return Mag_total if Mag_total < 32768 else Mag_total - 65536


def readMagz():
    Mag_l = bus.read_byte_data(0x1C, 0x2C)
    Mag_h = bus.read_byte_data(0x1C, 0x2D)
    Mag_total = (Mag_l | Mag_h << 8)
    return Mag_total if Mag_total < 32768 else Mag_total - 65536


def MagDataTotal():
    mtotal = (((readMagx() ** 2) + (readMagy() ** 2) + (readMagz() ** 2)) ** 0.5)
    mtotal = (mtotal * 4 * 6.842) / 32768
    return mtotal


while True:

    # initialise the Magnetometer
    writeMag(0x22, 0x00)
    writeMag(0x20, 0xD2)
    writeMag(0x21, 0x00)
    writeMag(0x23, 0x00)
    writeMag(0x24, 0x40)
    # writeMag(0x30,0x01)
    # writeMag(0x27,0xFF)
    # Read our  Magnetometer  values

    Magx = readMagx()
    Magy = readMagy()
    Magz = readMagz()
    print(Magx, Magy, Magz)

    # Calculate heading

    # Calculate heading
    heading = 180 * math.atan2(Magy, Magx) / 3.14

    if heading < 0:
        heading += 360

    print("Mtotal       : ", MagDataTotal(), "Guass")
    print("HEADING      : ", heading)
    print("****************************")
    time.sleep(0.5)