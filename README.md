pyTroykaIMU
==========

Библиотека на Python 3 для Raspberry Pi, позволяющая управлять [IMU-сенсором на 10 степеней свободы (Troyka-модуль)](http://amperka.ru/product/troyka-imu-10-dof)
от [Амперки](http://amperka.ru/).

![alt-текст](https://static-eu.insales.ru/images/products/1/799/58802975/troyka-imu-10-dof.1.jpg "IMU-сенсор на 10 степеней свободы (Troyka-модуль)")


Подключение
==========
![alt-текст](http://wiki.amperka.ru/_media/продукты:troyka-gpio-expander:gpio_ext.png "Подключение аналогично любому модулю Troyka")

Для подключения большего большего количества Troyka модулей очень удобно использовать, например [Troyka Pad](http://amperka.ru/product/troyka-pad-1x4)

![alt-текст](https://static-eu.insales.ru/images/products/1/2757/98380485/troyka_pad_all_in.jpg "Troyka Pad")

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
Название файла      | Содержание файла
--------------------|----------------------
igrf12py            | классы и утилиты для реализации стандартной геомагнитной модели поля Земли
gost4401_81.py      | класс реализация стандартной модели атмосферы по ГОСТ4401
l3g4200d.py         | класс гироскопа TroykaIMU модуля
lis3mdl.py          | класс магнетометра(компаса) TroykaIMU модуля
lis331dlh.py        | класс акселерометра TroykaIMU модуля
lps331ap.py         | класс барометра TroykaIMU модуля
madgwickahrs.py     | класс магнетометра TroykaIMU модуля
pytroykaimu.py      | класс TroykaIMU модуля
quaternion.py       | класс реализации кватернионов и операций над ними



- Трёхосный гироскоп L3G4200D покажет скорость вращения относительно собственных осей X, Y и Z
- Трёхосный магнетометр/компас LIS3MDL покажет напряженность магнитного поля относительно собственных осей. Это поможет определить направление на Север
- Трёхосный акселерометр LIS331DLH покажет ускорение относительно собственных осей X, Y и Z. Это поможет определить направление к центру Земли 
- Барометр LPS331AP покажет атмосферное давление и поможет вычислить высоту над уровнем моря.



IGRF12py
==========

Реализация класса стантартного [международного геомагнитного аналитического поля (IGRF)](https://ru.wikipedia.org/wiki/Международное_геомагнитное_аналитическое_поле) 
позволяющего более эффективно использовать магнитометр на TroykaIMU модуле.

.. image:: https://travis-ci.org/scivision/pyigrf12.svg?branch=master
    :target: https://travis-ci.org/scivision/pyigrf12
    
.. image:: https://coveralls.io/repos/github/scivision/pyigrf12/badge.svg?branch=master
    :target: https://coveralls.io/github/scivision/pyigrf12?branch=master

Про использования данных пожно почитать, например тут:
- http://geologyandpython.com/igrf.html
- http://geomag.nrcan.gc.ca/calc/calc-en.php