import pytest


def test_setup(smbus2, icp10125):
    smbus2.i2c_msg.read().__iter__.return_value = [1, 72, 241]

    sensor = icp10125.ICP10125()
    del sensor


def test_setup_invalid_chip_id(smbus2, icp10125):
    smbus2.i2c_msg.read().__iter__.return_value = [0, 0, 129]

    with pytest.raises(RuntimeError):
        sensor = icp10125.ICP10125()
        del sensor


def test_setup_invalid_crc8(smbus2, icp10125):
    smbus2.i2c_msg.read().__iter__.return_value = [0, 0, 0]

    with pytest.raises(ValueError):
        sensor = icp10125.ICP10125()
        del sensor
