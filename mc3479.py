# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`mc3479`
================================================================================

MC3479 Accelerometer Driver


* Author(s): Jose D. Montoya

Implementation Notes
--------------------


**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register

"""


from micropython import const
from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import ROUnaryStruct, UnaryStruct
from adafruit_register.i2c_bits import RWBits

try:
    from busio import I2C
    from typing_extensions import NoReturn
    from typing import Tuple
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_MC3479.git"

_I2C_ADDR = const(0x4C)
_REG_WHOAMI = const(0x98)
_SENSOR_STATUS_REG = const(0x05)
_MODE_REG = const(0x07)
_ACC_RANGE = const(0x20)

# Acceleration Data
ACC_X_LSB = const(0x0D)
ACC_X_MSB = const(0x0E)
ACC_Y_LSB = const(0x0F)
ACC_Y_MSB = const(0x10)
ACC_Z_LSB = const(0x11)
ACC_Z_MSB = const(0x12)

# Sensor Power
STANDBY = const(0)
NORMAL = const(1)

# Aceleration Range
ACCEL_RANGE_2G = const(0b000)
ACCEL_RANGE_4G = const(0b001)
ACCEL_RANGE_8G = const(0b010)
ACCEL_RANGE_16G = const(0b011)
ACCEL_RANGE_12G = const(0b100)

# pylint: disable= invalid-name, too-many-instance-attributes, missing-function-docstring
# pylint: disable=too-few-public-methods


class MC3479:
    """Driver for the MC3479 Sensor connected over I2C.

    :param ~busio.I2C i2c_bus: The I2C bus the MC3479 is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x4C`

    :raises RuntimeError: if the sensor is not found

    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`MC3479` class.
    First you will need to import the libraries to use the sensor

        .. code-block:: python

            import board
            import mc3479 as MC3479

    Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()  # uses board.SCL and board.SDA
            mc3479 = MC3479.MC3479(i2c)

    Now you have access to the attributes

        .. code-block:: python

            accx, accy, accz = mc3479.acceleration

    """

    _device_id = ROUnaryStruct(_REG_WHOAMI, "B")
    _status = UnaryStruct(_SENSOR_STATUS_REG, "B")
    _mode_reg = UnaryStruct(_MODE_REG, "B")
    _range_scale_control = UnaryStruct(_ACC_RANGE, "B")

    # Acceleration Data
    _acc_data_x_msb = UnaryStruct(ACC_X_MSB, "B")
    _acc_data_x_lsb = UnaryStruct(ACC_X_LSB, "B")
    _acc_data_y_msb = UnaryStruct(ACC_Y_MSB, "B")
    _acc_data_y_lsb = UnaryStruct(ACC_Y_LSB, "B")
    _acc_data_z_msb = UnaryStruct(ACC_Z_MSB, "B")
    _acc_data_z_lsb = UnaryStruct(ACC_Z_LSB, "B")

    _mode = RWBits(2, _MODE_REG, 0)

    _acc_range = RWBits(3, _ACC_RANGE, 4)

    acceleration_scale = {0: 16384, 1: 8192, 2: 4096, 3: 2048, 4: 2730}

    def __init__(self, i2c_bus: I2C, address: int = _I2C_ADDR) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

        if self._device_id != 0xA4:
            raise RuntimeError("Failed to find MC3479")

        self._mode = NORMAL

    @property
    def acceleration(self) -> Tuple[int, int, int]:

        factor = self.acceleration_scale[self.acceleration_range]

        x = (self._acc_data_x_msb * 256 + self._acc_data_x_lsb) / factor
        y = (self._acc_data_y_msb * 256 + self._acc_data_y_lsb) / factor
        z = (self._acc_data_z_msb * 256 + self._acc_data_z_lsb) / factor
        return x, y, z

    @property
    def sensor_mode(self) -> int:
        """

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`MC3479.STANDBY`             | :py:const:`0`           |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.NORMAL`              | :py:const:`1`           |
        +----------------------------------------+-------------------------+

        """
        return self._mode

    @sensor_mode.setter
    def sensor_mode(self, value: int) -> NoReturn:
        self._mode = value

    @property
    def acceleration_range(self) -> int:
        """

        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`MC3479.ACCEL_RANGE_2G`      | :py:const:`0b000`       |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.ACCEL_RANGE_4G`      | :py:const:`0b001`       |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.ACCEL_RANGE_8G`      | :py:const:`0b010`       |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.ACCEL_RANGE_16G`     | :py:const:`0b011`       |
        +----------------------------------------+-------------------------+
        | :py:const:`MC3479.ACCEL_RANGE_12G`     | :py:const:`0b100`       |
        +----------------------------------------+-------------------------+

        """
        return self._acc_range

    @acceleration_range.setter
    def acceleration_range(self, value: int) -> NoReturn:
        self._mode = STANDBY
        self._acc_range = value
        self._mode = NORMAL
