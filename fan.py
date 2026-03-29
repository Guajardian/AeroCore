"""
AeroCore — Fan/PWM controller
Provides a unified interface for PWM fan control across platforms.
Set "platform" in config.json: "auto", "rpi", or "mock".
"""


def create_fan(config):
    """Factory: create the right fan controller based on config."""
    platform = config.get("platform", "auto").lower()

    if platform == "mock":
        return MockFan()
    elif platform == "rpi":
        return RPiFan(config)
    elif platform == "auto":
        return _auto_detect(config)
    else:
        print(f"Unknown platform '{platform}' — falling back to mock")
        return MockFan()


def _auto_detect(config):
    """Try RPi.GPIO, fall back to mock."""
    try:
        return RPiFan(config)
    except Exception as e:
        print(f"GPIO not available ({e}) — using mock fan controller")
        return MockFan()


class RPiFan:
    """PWM fan control via RPi.GPIO."""
    def __init__(self, config):
        import RPi.GPIO as GPIO

        self._GPIO = GPIO
        self._pin = config.get("gpio_pin", 18)
        freq = config.get("pwm_freq", 25000)

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.OUT)
            self._pwm = GPIO.PWM(self._pin, freq)
            self._pwm.start(0)
        except Exception as e:
            raise RuntimeError(
                f"GPIO/PWM init failed on pin {self._pin}: {e}\n"
                "Check that the pin is valid and not in use. You may need to run with sudo\n"
                "or add your user to the gpio group: sudo usermod -aG gpio $USER"
            )
        print(f"PWM fan initialized on GPIO {self._pin} at {freq} Hz")

    def set_speed(self, duty_cycle):
        self._pwm.ChangeDutyCycle(duty_cycle)

    def cleanup(self):
        self._pwm.ChangeDutyCycle(0)
        self._pwm.stop()
        self._GPIO.cleanup()


class MockFan:
    """Simulated fan for testing without hardware."""
    def __init__(self):
        self._speed = 0
        print("Using mock fan controller (no GPIO)")

    def set_speed(self, duty_cycle):
        self._speed = duty_cycle

    def cleanup(self):
        pass
