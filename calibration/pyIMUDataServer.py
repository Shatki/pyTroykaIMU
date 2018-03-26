from socket import *
#from madgwickahrs import MadgwickAHRS
from pytroykaimu import TroykaIMU
import time

# Адрес
HOST = ''
PORT = 21567
BUFSIZ = 512
ADDR = (HOST, PORT)

imu = TroykaIMU()
#imufilter = MadgwickAHRS(beta=1, sampleperiod=1 / 256)

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

# Запрет на ожидание
# tcpSerSock.setblocking(False)

while True:
    try:
        print('waiting for connection...')
        # Ждем соединения клиента
        tcpCliSock, addr = tcpSerSock.accept()
        # Время ожидания данных от клиента
        tcpCliSock.settimeout(0.02)
        print('...connection from:', addr)

        # Соединились, передаем данные
        while True:
            # imufilter.update(imu.gyroscope.read_radians_per_second_xyz(),
            #              imu.accelerometer.read_gxyz(),
            #              imu.magnetometer.read_gauss_xyz())
            # data = imufilter.quaternion.to_angle_axis()

            m_x, m_y, m_z = imu.magnetometer.read_gauss_xyz()
            a_x, a_y, a_z = imu.accelerometer.read_gxyz()
            g_x, g_y, g_z = imu.gyroscope.read_radians_per_second_xyz()


            print( imu.magnetometer.read_gauss_x(),
                   imu.magnetometer.read_gauss_y(),
                   imu.magnetometer.read_gauss_z(),)

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
                    print('Cannot send data')
                    tcpCliSock.close()
                    break
                    # Ждем соединение

    except KeyboardInterrupt:
        # Закрываем сервер
        print('Server was closed')
        tcpSerSock.close()
        break
