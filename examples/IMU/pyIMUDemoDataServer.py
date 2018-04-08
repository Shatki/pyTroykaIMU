from socket import *
from madgwickahrs import MadgwickAHRS
from pytroykaimu import TroykaIMU
import time
import datetime

# Адрес
HOST = ''
PORT = 21567
BUFSIZ = 128
ADDR = (HOST, PORT)

imu = TroykaIMU()

calibration_matrix = [[0.983175, 0.022738, -0.018581],
                      [0.022738, 0.942140, -0.022467],
                      [-0.018581, -0.022467, 1.016113]]

# raw measurements only
bias = [962.391696, -162.681348, 11832.188828]

imu.magnetometer.calibrate_matrix(calibration_matrix, bias)


imufilter = MadgwickAHRS(beta=1, sampleperiod=1 / 256)

# Запрет на ожидание
# tcpSerSock.setblocking(False)
def print_log(text):
    print('{}    {}'.format(datetime.datetime.now(), text))


def main():
    while True:
        try:
            print_log('IMU Demo data server was started')
            print_log('waiting for connection...')
            # Ждем соединения клиента
            tcpCliSock, addr = tcpSerSock.accept()
            # Время ожидания данных от клиента
            tcpCliSock.settimeout(0.02)
            print_log('connection from: ' + str(addr))

            # Соединились, передаем данные
            while True:
                imufilter.update(imu.gyroscope.read_radians_per_second_xyz(),
                              imu.accelerometer.read_gxyz(),
                              imu.magnetometer.read_calibrate_gauss_xyz())

                data = imufilter.quaternion

                dataencode = str(data).encode('utf-8').ljust(128, b' ')

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

except:
    print_log('Port is used. Change PORT and try again')

main()
