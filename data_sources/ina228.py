# SPDX-FileCopyrightText: Bryan Siepert 2019 for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_ina228`
================================================================================
CircuitPython driver for the TI INA228 current and power sensor
* Author(s): Sergey Likhobabin
Implementation Notes
--------------------
**Hardware:**
* `INA260 Breakout <https://www.adafruit.com/products/4226>`_
**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
* https://github.com/adafruit/circuitpython/releases
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports

try:
    import typing
    from busio import I2C
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_INA260.git"

from micropython import const
import adafruit_bus_device.i2c_device as i2cdevice
import struct

from adafruit_register.i2c_struct import ROUnaryStruct
from adafruit_register.i2c_bits import ROBits, RWBits
from adafruit_register.i2c_bit import ROBit, RWBit

_REG_CONFIG = const(0x00)  # CONFIGURATION REGISTER (R/W)
_REG_CURRENT = const(0x07)  # SHUNT VOLTAGE REGISTER (R)
_REG_BUSVOLTAGE = const(0x05)  # BUS VOLTAGE REGISTER (R)
_REG_TEMP = const(0x06)
_REG_POWER = const(0x08)  # POWER REGISTER (R)
_REG_MFG_UID = const(0x3E)  # MANUFACTURER UNIQUE ID REGISTER (R)
_REG_DIE_UID = const(0x3F)  # DIE UNIQUE ID REGISTER (R)


# pylint: disable=too-few-public-methods
class Mode:
    """Modes avaible to be set

    +--------------------+---------------------------------------------------------------------+
    | Mode               | Description                                                         |
    +====================+=====================================================================+
    | ``Mode.CONTINUOUS``| Default: The sensor will continuously measure the bus voltage and   |
    |                    | shunt voltage across the shunt resistor to calculate ``power`` and  |
    |                    | ``current``                                                         |
    +--------------------+---------------------------------------------------------------------+
    | ``Mode.TRIGGERED`` | The sensor will immediately begin measuring and calculating current,|
    |                    | bus voltage, and power. Re-set this mode to initiate another        |
    |                    | measurement                                                         |
    +--------------------+---------------------------------------------------------------------+
    | ``Mode.SHUTDOWN``  |  Shutdown the sensor, reducing the quiescent current and turning off|
    |                    |  current into the device inputs. Set another mode to re-enable      |
    +--------------------+---------------------------------------------------------------------+

    """

    SHUTDOWN = const(0x00)
    TRIGGERED = const(0x02)
    CONTINUOUS = const(0x0B)


class ConversionTime:
    """Options for ``current_conversion_time`` or ``voltage_conversion_time``

    +----------------------------------+------------------+
    | ``ConversionTime``               | Time             |
    +==================================+==================+
    | ``ConversionTime.TIME_140_us``   | 140 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_204_us``   | 204 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_332_us``   | 332 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_588_us``   | 588 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_1_1_ms``   | 1.1 ms (Default) |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_2_116_ms`` | 2.116 ms         |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_4_156_ms`` | 4.156 ms         |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_8_244_ms`` | 8.244 ms         |
    +----------------------------------+------------------+

    """

    TIME_140_us = const(0x0)
    TIME_204_us = const(0x1)
    TIME_332_us = const(0x2)
    TIME_588_us = const(0x3)
    TIME_1_1_ms = const(0x4)
    TIME_2_116_ms = const(0x5)
    TIME_4_156_ms = const(0x6)
    TIME_8_244_ms = const(0x7)

    @staticmethod
    def get_seconds(time_enum: int) -> float:
        """Retrieve the time in seconds giving value read from register"""
        conv_dict = {
            0: 140e-6,
            1: 204e-6,
            2: 332e-6,
            3: 588e-6,
            4: 1.1e-3,
            5: 2.116e-3,
            6: 4.156e-3,
            7: 8.244e-3,
        }
        return conv_dict[time_enum]


class AveragingCount:
    """Options for ``averaging_count``

    +-------------------------------+------------------------------------+
    | ``AveragingCount``            | Number of measurements to average  |
    +===============================+====================================+
    | ``AveragingCount.COUNT_1``    | 1 (Default)                        |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_4``    | 4                                  |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_16``   | 16                                 |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_64``   | 64                                 |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_128``  | 128                                |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_256``  | 256                                |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_512``  | 512                                |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_1024`` | 1024                               |
    +-------------------------------+------------------------------------+

    """

    COUNT_1 = const(0x0)
    COUNT_4 = const(0x1)
    COUNT_16 = const(0x2)
    COUNT_64 = const(0x3)
    COUNT_128 = const(0x4)
    COUNT_256 = const(0x5)
    COUNT_512 = const(0x6)
    COUNT_1024 = const(0x7)

    @staticmethod
    def get_averaging_count(avg_count: int) -> float:
        """Retrieve the number of measurements giving value read from register"""
        conv_dict = {0: 1, 1: 4, 2: 16, 3: 64, 4: 128, 5: 256, 6: 512, 7: 1024}
        return conv_dict[avg_count]


# pylint: enable=too-few-public-methods


class INA228:
    """Driver for the INA228 power and current sensor.

    :param ~busio.I2C i2c_bus: The I2C bus the INA228 is connected to.
    :param int address: The I2C device address for the sensor. Default is ``0x40``.

    """

    def __init__(self, i2c_bus: I2C, address: int = 0x40) -> None:
        self.i2c_device = i2cdevice.I2CDevice(i2c_bus, address)

        if self._manufacturer_id != self.TEXAS_INSTRUMENT_ID:
            raise RuntimeError(
                "Failed to find Texas Instrument ID, read "
                + f"{self._manufacturer_id} while expected {self.TEXAS_INSTRUMENT_ID}"
                " - check your wiring!"
            )

        if self._device_id != self.INA228_ID:
            raise RuntimeError(
                f"Failed to find INA260 ID, read {self._device_id} while expected {self.INA260_ID}"
                " - check your wiring!"
            )
        self.reset_bit = 1
        self.mode = Mode.CONTINUOUS

    def read_register(self, register, size: int, format: str):
        if size == 3:
            actual_size = 4
        else:
            actual_size = size
        buf = bytearray(1 + actual_size)
        buf[0] = register
        with self.i2c_device as i2c:
            i2c.write_then_readinto(out_buffer=buf, in_buffer=buf, out_end=1, in_start=1)
        if size == 3:
            buf[1] = 0
        result = struct.unpack_from(format, buf, 1)[0]
        print('Address {0}: {1}'.format(hex(register), ' '.join([hex(x) for x in buf])))
        return result

    _raw_current = ROUnaryStruct(_REG_CURRENT, ">l")
    _raw_voltage = ROUnaryStruct(_REG_BUSVOLTAGE, ">H")
    _raw_power = ROUnaryStruct(_REG_POWER, ">L")
    _raw_temp = ROUnaryStruct(_REG_TEMP, ">H")

    reset_bit = RWBit(_REG_CONFIG, 15, 2, False)
    """Setting this bit t 1 generates a system reset. Reset all registers to default values."""
    averaging_count = RWBits(3, _REG_CONFIG, 9, 2, False)
    """The window size of the rolling average used in continuous mode"""
    voltage_conversion_time = RWBits(3, _REG_CONFIG, 6, 2, False)
    """The conversion time taken for the bus voltage measurement"""
    current_conversion_time = RWBits(3, _REG_CONFIG, 3, 2, False)
    """The conversion time taken for the current measurement"""

    mode = RWBits(3, _REG_CONFIG, 0, 2, False)
    """The mode that the INA228 is operating in. Must be one of
    ``Mode.CONTINUOUS``, ``Mode.TRIGGERED``, or ``Mode.SHUTDOWN``
    """

    TEXAS_INSTRUMENT_ID = const(0x5449)
    INA228_ID = const(0x228)
    _manufacturer_id = ROUnaryStruct(_REG_MFG_UID, ">H")
    """Manufacturer identification bits"""
    _device_id = ROBits(12, _REG_DIE_UID, 4, 2, False)
    """Device identification bits"""
    revision_id = ROBits(4, _REG_DIE_UID, 0, 2, False)
    """Device revision identification bits"""

    @property
    def current(self) -> float:
        """The current (between V+ and V-) in mA"""
        #self.reset_bit = 1
        #self.mode = Mode.CONTINUOUS
        if self.mode == Mode.TRIGGERED:
            while self._conversion_ready_flag == 0:
                print('sdfs')
                pass
        current = self.read_register(_REG_CURRENT, 3, '>l')
        print('raw_current', current)
        current_lsb = 3.2 / 1048575
        result_current = current / 16 * current_lsb * 1000.0
        print('current', result_current);
        return result_current

    @property
    def voltage(self) -> float:
        """The bus voltage in V"""
        if self.mode == Mode.TRIGGERED:
            while self._conversion_ready_flag == 0:
                pass
        print(self._raw_voltage)
        return self._raw_voltage * 0.00125

    @property
    def temp(self) -> float:
        if self.mode == Mode.TRIGGERED:
            while self._conversion_ready_flag == 0:
                pass
        temp = self.read_register(_REG_TEMP, 2, '>H')
        return temp * 7.8125 / 1000.0;
        

    @property
    def power(self) -> int:
        """The power being delivered to the load in mW"""
        if self.mode == Mode.TRIGGERED:
            while self._conversion_ready_flag == 0:
                pass
        return self._raw_power * 10
