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

calibration_matrix = [[0.858751, 0.029588, 0.022668],
                      [0.029588, 0.871676, 0.001220],
                      [0.022668, 0.001220, 0.892654]]

bias = [0.265855, -0.356333, 0.586471]

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

            data = "{:f};\t{:f};\t{:f};\t" \
                   "{:f};\t{:f};\t{:f};\t" \
                   "{:f};\t{:f};\t{:f};\t{:f}".format(m_x, m_y, m_z,
                                                      a_x, a_y, a_z,
                                                      g_x, g_y, g_z,
                                                      imu.magnetometer.read_azimut())

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
