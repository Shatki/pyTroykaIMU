pyTroykaIMU
==========

Библиотека на Python 3 для Raspberry Pi, позволяющая управлять [IMU-сенсором на 10 степеней свободы (Troyka-модуль)](http://amperka.ru/product/troyka-imu-10-dof)
от [Амперки](http://amperka.ru/).


Пример использования
====================
```python

from madgwickahrs import MadgwickAHRS
from pytroykaimu import TroykaIMU
 
imu = TroykaIMU()
filter = MadgwickAHRS(beta=1, sampleperiod=1/256)

while True:
    filter.update(imu.gyroscope.read_radians_per_second_xyz(),
                  imu.accelerometer.read_gxyz(),
                  imu.magnetometer.read_gauss_xyz())
    data = filter.quaternion.to_angle_axis()

    dataencode = str(data).encode('utf-8')
    if dataencode:
        print(data)

```

Состав библиотеки
====================
Название файла  | Содержание файла
----------------|----------------------
gost4401_81.py  | класс реализация модели атмосферы по ГОСТ4401
l3g4200d.py     | класс гироскопа TroykaIMU модуля
lis3mdl.py      | класс магнетометра TroykaIMU модуля