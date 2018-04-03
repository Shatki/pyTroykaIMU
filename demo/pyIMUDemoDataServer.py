
from socket import *
#from madgwickahrs import MadgwickAHRS
from pytroykaimu import TroykaIMU
import time
import datetime

# Адрес
HOST = ''
PORT = 21567
BUFSIZ = 128
ADDR = (HOST, PORT)

imu = TroykaIMU()

calibration_matrix = [[1.000123, 0.026213, -0.018512],
                      [0.026213, 0.947828, -0.024011],
                      [-0.018512, -0.024011, 1.020657]]

bias = [1031.967291, -129.473185, 11690.446495]

imu.magnetometer.calibrate_matrix(calibration_matrix, bias)

#imufilter = MadgwickAHRS(beta=1, sampleperiod=1 / 256)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

# Запрет на ожидание
# tcpSerSock.setblocking(False)
def print_log(text):
    print('{}    {}'.format(datetime.datetime.now(), text))

while True:
    try:
        print_log('waiting for connection...')
        # Ждем соединения клиента
        tcpCliSock, addr = tcpSerSock.accept()
        # Время ожидания данных от клиента
        tcpCliSock.settimeout(0.02)
        print_log('connection from: ' + str(addr))

        # Соединились, передаем данные
        while True:
            # imufilter.update(imu.gyroscope.read_radians_per_second_xyz(),
            #              imu.accelerometer.read_gxyz(),
            #              imu.magnetometer.read_gauss_xyz())
            # data = imufilter.quaternion.to_angle_axis()

            m_x, m_y, m_z = imu.magnetometer.read_calibrate_gauss_xyz()
            a_x, a_y, a_z = imu.accelerometer.read_gxyz()
            g_x, g_y, g_z = imu.gyroscope.read_radians_per_second_xyz()

            print(imu.magnetometer.read_azimut())

            data = "{:f}; {:f}; {:f}; " \
                   "{:f}; {:f}; {:f}; " \
                   "{:f}; {:f}; {:f}".format(m_x, m_y, m_z,
                                             a_x, a_y, a_z,
                                             g_x, g_y, g_z)

            dataencode = data.encode('utf-8').ljust(128, b' ')

            if dataencode:
                try:
                    # отправляем данные
                    tcpCliSock.send(dataencode)
                    time.sleep(0.05)
                except:
                    # разрываем соединение, проблема с клиентом
                    print_log('Client terminated the connection')
                    tcpCliSock.close()
                    break
                    # Ждем соединение

    except KeyboardInterrupt:
        # Закрываем сервер
        print_log('Server was closed')
        tcpSerSock.close()
        break
