import struct
import time

from smbus2 import SMBus, i2c_msg

__version__ = "1.0.0"

NORMAL = 0x6825
LOW_POWER = 0x609C
LOW_NOISE = 0x70DF
ULTRA_LOW_NOISE = 0x7866
NORMAL_T_FIRST = 0x6825
NORMAL_P_FIRST = 0x48A3
LOW_POWER_T_FIRST = 0x609C
LOW_POWER_P_FIRST = 0x401A
LOW_NOISE_T_FIRST = 0x70DF
LOW_NOISE_P_FIRST = 0x5059
ULN_T_FIRST = 0x7866
ULN_P_FIRST = 0x58E0

SOFT_RESET = 0x805D
READ_ID = 0xEFC8
MOVE_ADDRESS_PTR = 0xC595
READ_OTP = 0xC7F7

DEFAULT_I2C_ADDRESS = 0x63
CHIP_ID = 0x08

OK = 0
CRC_FAIL = 1

MEASUREMENT_DELAYS = {
    NORMAL: 7,           # 5.6 to 6.3ms
    LOW_POWER: 2,        # 1.6 to 1.8ms
    LOW_NOISE: 24,       # 20.8 to 23.8ms
    ULTRA_LOW_NOISE: 95  # 83.2 to 94.5ms
}


class ICP10125:
    sensor_constants = [0, 0, 0, 0]

    def __init__(self, address=None):
        if address is None:
            address = DEFAULT_I2C_ADDRESS
        self.address = address

        self.bus = SMBus(1)

        chip_id = self.chip_id()
        if chip_id != CHIP_ID:
            raise RuntimeError(f"ICP10125: Invalid Chip ID {chip_id:02x}, expected: {CHIP_ID:02x}")

        self.read_otp()

    def rdwr(self, command, length=0, delay=0):
        if isinstance(command, int):
            msg_w = i2c_msg.write(self.address, struct.pack(">H", command))
        else:
            msg_w = i2c_msg.write(self.address, command)

        self.bus.i2c_rdwr(msg_w)

        time.sleep(delay / 1000.0)

        if length > 0:
            msg_r = i2c_msg.read(self.address, length)
            self.bus.i2c_rdwr(msg_r)
            if length == 1:
                return list(msg_r)[0]
            else:
                result = list(msg_r)
                data = []
                for chunk in range(0, len(result), 3):
                    if self.crc8(result[chunk : chunk + 2]) != result[chunk + 2]:
                        raise ValueError("ICP10125: Invalid CRC8 in response.")
                    data.append((result[chunk] << 8) | result[chunk + 1])
                if len(data) == 1:
                    return data[0]
                else:
                    return data

        return []

    def chip_id(self):
        result = self.rdwr(READ_ID, 3)
        return result & 0x3F

    def read_otp(self):
        move_address_ptr = [
            MOVE_ADDRESS_PTR >> 8, MOVE_ADDRESS_PTR & 0xff,
            0x00, 0x66, 0x9C  # Address CRC8
        ]
        self.rdwr(move_address_ptr)

        for x in range(4):
            self.sensor_constants[x] = self.rdwr(READ_OTP, 3)

    def reset(self):
        self.rdwr(SOFT_RESET, delay=0.1)

    def measure(self, measure_command=NORMAL):
        delay = MEASUREMENT_DELAYS[measure_command]

        result = self.rdwr(measure_command, 9, delay)

        temperature = result[0]
        pressure = (result[1] << 8) | (result[2] >> 8)

        self.process_data(pressure, temperature)

        return self.pressure, self.temperature

    def calculate_altitude(self, pressure, qnh=1013.25):
        return 44330.0 * (1.0 - pow(pressure / qnh, 1.0 / 5.255))

    def process_data(self, p_LSB, T_LSB):
        LUT_lower = 3.5 * (1 << 20)
        LUT_upper = 11.5 * (1 << 20)
        quadr_factor = 1.0 / 16777216.0
        offst_factor = 2048.0

        t = T_LSB - 32768
        s1 = LUT_lower + (self.sensor_constants[0] * t * t) * quadr_factor
        s2 = offst_factor * self.sensor_constants[3] + (self.sensor_constants[1] * t * t) * quadr_factor
        s3 = LUT_upper + (self.sensor_constants[2] * t * t) * quadr_factor

        A, B, C = self.calculate_conversion_constants([s1, s2, s3])

        self.pressure = A + B / (C + p_LSB)
        self.temperature = -45.0 + 175.0 / 65536.0 * T_LSB

    def calculate_conversion_constants(self, p_LUT):
        p_Pa = [45000.0, 80000.0, 105000.0]

        C = (p_LUT[0] * p_LUT[1] * (p_Pa[0] - p_Pa[1]) +   # noqa: W504
        p_LUT[1] * p_LUT[2] * (p_Pa[1] - p_Pa[2]) +        # noqa: W504
        p_LUT[2] * p_LUT[0] * (p_Pa[2] - p_Pa[0])) / (p_LUT[2] * (p_Pa[0] - p_Pa[1]) +   # noqa: W504
        p_LUT[0] * (p_Pa[1] - p_Pa[2]) +                   # noqa: W504
        p_LUT[1] * (p_Pa[2] - p_Pa[0]))
        A = (p_Pa[0] * p_LUT[0] - p_Pa[1] * p_LUT[1] - (p_Pa[1] - p_Pa[0]) * C) / (p_LUT[0] - p_LUT[1])
        B = (p_Pa[0] - A) * (p_LUT[0] + C)

        return A, B, C

    def crc8(self, data, polynomial=0x31):
        result = 0xFF
        for byte in data:
            result ^= byte
            for bit in range(8):
                if result & 0x80:
                    result <<= 1
                    result ^= polynomial
                else:
                    result <<= 1
        return result & 0xFF
