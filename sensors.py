"""
AeroCore — Sensor drivers
Provides a unified interface for reading temperature, humidity, and pressure
from various sensor types. Set "sensor" in config.json to choose your sensor.

Supported: bme280, bmp280, dht22, dht11, ds18b20, sht31, mock
"""

import time
import random


class SensorReading:
    """Container for sensor data."""
    def __init__(self, temperature=0.0, humidity=0.0, pressure=0.0):
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure


def create_sensor(config):
    """Factory: create the right sensor based on config."""
    sensor_type = config.get("sensor", "bme280").lower()

    if sensor_type == "mock":
        return MockSensor()
    elif sensor_type == "bme280":
        return BME280Sensor(config)
    elif sensor_type == "bmp280":
        return BMP280Sensor(config)
    elif sensor_type == "dht22":
        return DHT22Sensor(config)
    elif sensor_type == "dht11":
        return DHT11Sensor(config)
    elif sensor_type == "ds18b20":
        return DS18B20Sensor(config)
    elif sensor_type == "sht31":
        return SHT31Sensor(config)
    else:
        print(f"Unknown sensor type '{sensor_type}' — falling back to mock")
        return MockSensor()


class MockSensor:
    """Simulated sensor for testing without hardware."""
    def __init__(self):
        self._base_temp = 35.0
        self._base_humidity = 50.0
        self._base_pressure = 1013.25
        print("Using mock sensor (simulated data)")

    def read(self):
        return SensorReading(
            temperature=round(self._base_temp + random.uniform(-3, 3), 1),
            humidity=round(self._base_humidity + random.uniform(-10, 10), 1),
            pressure=round(self._base_pressure + random.uniform(-2, 2), 1)
        )


class BME280Sensor:
    """Bosch BME280 — temp, humidity, pressure via I2C."""
    def __init__(self, config):
        import board
        import adafruit_bme280.basic as adafruit_bme280

        addr_str = config.get("bme280_address", "0x76")
        try:
            address = int(addr_str, 16)
        except ValueError:
            print(f"Invalid bme280_address '{addr_str}' — using default 0x76")
            address = 0x76

        try:
            i2c = board.I2C()
            self._sensor = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=address)
        except Exception as e:
            raise RuntimeError(
                f"BME280 init failed at {hex(address)}: {e}\n"
                "Check that I2C is enabled (sudo raspi-config) and the sensor is connected.\n"
                "Verify address with: i2cdetect -y 1"
            )
        print(f"BME280 sensor initialized at {hex(address)}")

    def read(self):
        return SensorReading(
            temperature=round(self._sensor.temperature, 1),
            humidity=round(self._sensor.humidity, 1),
            pressure=round(self._sensor.pressure, 1)
        )


class BMP280Sensor:
    """Bosch BMP280 — temp, pressure via I2C (no humidity)."""
    def __init__(self, config):
        import board
        from adafruit_bmp280 import Adafruit_BMP280_I2C

        addr_str = config.get("bme280_address", "0x76")
        try:
            address = int(addr_str, 16)
        except ValueError:
            address = 0x76

        try:
            i2c = board.I2C()
            self._sensor = Adafruit_BMP280_I2C(i2c, address=address)
        except Exception as e:
            raise RuntimeError(
                f"BMP280 init failed at {hex(address)}: {e}\n"
                "Check I2C and sensor connection. Verify with: i2cdetect -y 1"
            )
        print(f"BMP280 sensor initialized at {hex(address)}")

    def read(self):
        return SensorReading(
            temperature=round(self._sensor.temperature, 1),
            humidity=0.0,
            pressure=round(self._sensor.pressure, 1)
        )


class DHT22Sensor:
    """DHT22/AM2302 — temp, humidity via GPIO."""
    def __init__(self, config):
        import board
        import adafruit_dht

        pin_num = config.get("sensor_pin", 4)
        pin_map = {4: board.D4, 17: board.D17, 27: board.D27, 22: board.D22,
                   5: board.D5, 6: board.D6, 13: board.D13, 19: board.D19,
                   26: board.D26}
        pin = pin_map.get(pin_num, board.D4)

        try:
            self._sensor = adafruit_dht.DHT22(pin)
        except Exception as e:
            raise RuntimeError(f"DHT22 init failed on GPIO {pin_num}: {e}")
        print(f"DHT22 sensor initialized on GPIO {pin_num}")

    def read(self):
        try:
            return SensorReading(
                temperature=round(self._sensor.temperature, 1),
                humidity=round(self._sensor.humidity, 1),
                pressure=0.0
            )
        except RuntimeError:
            # DHT sensors occasionally fail reads — return last known or zeros
            return SensorReading()


class DHT11Sensor:
    """DHT11 — temp, humidity via GPIO (lower accuracy than DHT22)."""
    def __init__(self, config):
        import board
        import adafruit_dht

        pin_num = config.get("sensor_pin", 4)
        pin_map = {4: board.D4, 17: board.D17, 27: board.D27, 22: board.D22,
                   5: board.D5, 6: board.D6, 13: board.D13, 19: board.D19,
                   26: board.D26}
        pin = pin_map.get(pin_num, board.D4)

        try:
            self._sensor = adafruit_dht.DHT11(pin)
        except Exception as e:
            raise RuntimeError(f"DHT11 init failed on GPIO {pin_num}: {e}")
        print(f"DHT11 sensor initialized on GPIO {pin_num}")

    def read(self):
        try:
            return SensorReading(
                temperature=round(self._sensor.temperature, 1),
                humidity=round(self._sensor.humidity, 1),
                pressure=0.0
            )
        except RuntimeError:
            return SensorReading()


class DS18B20Sensor:
    """DS18B20 — temp only via 1-Wire."""
    def __init__(self, config):
        self._device_path = None
        base_dir = "/sys/bus/w1/devices/"

        try:
            import glob
            devices = glob.glob(base_dir + "28-*")
            if not devices:
                raise RuntimeError(
                    "No DS18B20 found. Enable 1-Wire: sudo raspi-config → "
                    "Interface Options → 1-Wire → Enable. Then reboot."
                )
            self._device_path = devices[0] + "/w1_slave"
        except Exception as e:
            raise RuntimeError(f"DS18B20 init failed: {e}")
        print(f"DS18B20 sensor initialized at {self._device_path}")

    def read(self):
        try:
            with open(self._device_path, "r") as f:
                lines = f.readlines()
            if "YES" not in lines[0]:
                return SensorReading()
            pos = lines[1].find("t=")
            if pos == -1:
                return SensorReading()
            temp = round(int(lines[1][pos + 2:]) / 1000.0, 1)
            return SensorReading(temperature=temp)
        except Exception:
            return SensorReading()


class SHT31Sensor:
    """Sensirion SHT31 — temp, humidity via I2C."""
    def __init__(self, config):
        import board
        import adafruit_sht31d

        try:
            i2c = board.I2C()
            self._sensor = adafruit_sht31d.SHT31D(i2c)
        except Exception as e:
            raise RuntimeError(
                f"SHT31 init failed: {e}\n"
                "Check I2C and sensor connection. Default address is 0x44."
            )
        print("SHT31 sensor initialized")

    def read(self):
        return SensorReading(
            temperature=round(self._sensor.temperature, 1),
            humidity=round(self._sensor.relative_humidity, 1),
            pressure=0.0
        )
