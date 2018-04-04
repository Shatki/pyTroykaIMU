from socket import *
# from madgwickahrs import MadgwickAHRS
from pytroykaimu import TroykaIMU
import time
import datetime

# Адрес
HOST = ''
PORT = 21567
BUFSIZ = 128
ADDR = (HOST, PORT)

imu = TroykaIMU()


def print_log(text):
    print('{}    {}'.format(datetime.datetime.now(), text))


# Запрет на ожидание
# tcpSerSock.setblocking(False)
def main():
    while True:
        try:
            print_log('Calibration data server was started')
            print_log('waiting for connection...')
            # Ждем соединения клиента
            tcpCliSock, addr = tcpSerSock.accept()
            # Время ожидания данных от клиента
            tcpCliSock.settimeout(0.02)
            print_log('connection from: ' + str(addr))

            # Соединились, передаем данные
            while True:
                m_x, m_y, m_z = imu.magnetometer.read_xyz()

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


try:
    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    tcpSerSock.bind(ADDR)
    tcpSerSock.listen(5)
    main()
except:
    print_log('Port is used. Change PORT and try again')
