# AeroCore

A Raspberry Pi-powered smart fan controller with a live web dashboard. AeroCore reads temperature, humidity, and pressure from a BME280 sensor and automatically adjusts PWM fan speed using a configurable fan curve — all managed through a clean, dark-themed web UI.

## Features

- **Automatic fan control** — PWM fan speed scales linearly between configurable low/high temperature thresholds
- **Fan profiles** — Switch between Silent, Default, and Performance presets with one click
- **Manual override** — Lock the fan to any speed, bypassing the automatic curve
- **Humidity trigger** — Optionally ramp fans when humidity exceeds a configurable threshold
- **Live dashboard** — Real-time temperature, humidity, pressure, and fan speed readings
- **12-hour history chart** — Visualizes temperature and fan speed trends (Chart.js)
- **System stats** — CPU temperature, uptime, and memory usage at a glance
- **Dark / Light theme** — Toggle between themes; preference saved in browser
- **Configurable fan curve** — Set low/high temp thresholds, minimum duty cycle, and sensor poll interval from the UI
- **User settings modal** — Gear icon in the header opens a settings panel for every user
  - **Change password** — Update your password with current-password verification
  - **Temperature unit** — Switch between °C and °F; all displayed values convert instantly
  - **Dashboard refresh rate** — Choose 2s / 5s / 10s / 30s polling interval
  - **Temperature alert** — Browser notifications when temperature exceeds a configurable threshold
- **User authentication** — Secure login with bcrypt-hashed passwords
- **User management** — Add and remove users from the admin panel
- **First-run setup** — Guided admin account creation on first launch
- **Self-update** — Update from the dashboard, command line, or a remote one-liner
- **Multi-sensor support** — BME280, BMP280, DHT22, DHT11, DS18B20, SHT31 — set `"sensor"` in `config.json`
- **Platform auto-detection** — Runs on Raspberry Pi with GPIO, or any machine in mock mode
- **Mock mode** — Full dashboard with simulated data — no hardware needed for testing or demos
- **Configurable hardware** — GPIO pin, PWM frequency, sensor address all stored in `config.json` (survives updates)

## Hardware

| Component | Details |
|-----------|---------|
| **Board** | Raspberry Pi (any model with GPIO + I2C) — or any machine in mock mode |
| **Sensor** | BME280 (default), BMP280, DHT22, DHT11, DS18B20, SHT31 — configurable |
| **Fan** | 4-pin PWM fan on GPIO 18 (configurable) |

### Wiring

```
BME280          Raspberry Pi
───────         ────────────
VIN  ────────── 3.3V
GND  ────────── GND
SCL  ────────── GPIO 3 (SCL)
SDA  ────────── GPIO 2 (SDA)

PWM Fan         Raspberry Pi / Power
───────         ────────────────────
PWM  ────────── GPIO 18
GND  ────────── GND (shared with Pi)
+12V/+5V ───── External power supply (match your fan's voltage)
```

> **Note:** Most 4-pin PWM fans require 12V power. Do **not** power the fan from the Pi's GPIO pins — use an external supply and share a common ground with the Pi.

## Requirements

- **Raspberry Pi** running Raspberry Pi OS (Bookworm or later recommended)
- **Python 3.7+**
- I2C enabled (`sudo raspi-config` → Interface Options → I2C → Enable)

## Installation

**One-liner (recommended):**

```bash
curl -sSL https://raw.githubusercontent.com/Guajardian/AeroCore/main/install.sh | bash
```

This automatically clones the repo, creates a virtual environment, installs dependencies, checks I2C, and optionally sets up a systemd service to start on boot.

Open `http://<pi-ip>:5000` in your browser. On first launch you'll be prompted to create an admin account.

<details>
<summary><strong>Manual installation</strong></summary>

```bash
# Clone the repo
git clone https://github.com/Guajardian/AeroCore.git
cd AeroCore

# Create a virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Enable I2C on your Pi (if not already)
sudo raspi-config  # Interface Options → I2C → Enable

# Run
python app.py
```

> **Note:** Always activate the virtual environment (`source venv/bin/activate`) before running AeroCore. The systemd service example below handles this automatically.

</details>

## Configuration

Fan curve and hardware settings are stored in `config.json`. Fan curve settings can be changed from the dashboard; hardware settings are edited in `config.json` directly:

| Setting | Default | Description |
|---------|---------|-------------|
| `sensor` | `"bme280"` | Sensor type: `bme280`, `bmp280`, `dht22`, `dht11`, `ds18b20`, `sht31`, or `mock` |
| `platform` | `"auto"` | Fan control: `auto` (detect GPIO), `rpi`, or `mock` (no hardware) |
| `gpio_pin` | 18 | GPIO pin for the PWM fan signal (BCM numbering) |
| `pwm_freq` | 25000 | PWM frequency in Hz (25 kHz is standard for 4-pin fans) |
| `bme280_address` | `"0x76"` | I2C address for BME280/BMP280 (`"0x76"` or `"0x77"`) |
| `sensor_pin` | 4 | GPIO pin for DHT11/DHT22 sensors |
| `temp_low` | 25.0 °C | Fans off below this temperature |
| `temp_high` | 45.0 °C | 100% fan speed at this temperature |
| `min_duty` | 20% | Minimum duty cycle when fans are active |
| `poll_interval` | 5s | Sensor polling frequency |
| `humidity_trigger` | off | Enable humidity-based fan activation |
| `humidity_high` | 70% | Humidity threshold for fan trigger |
| `active_profile` | default | Currently active fan profile |

> **Note:** Changes to `sensor`, `platform`, `gpio_pin`, `pwm_freq`, `bme280_address`, and `sensor_pin` require a service restart to take effect. All other settings apply immediately.

## Supported Sensors

| Sensor | `"sensor"` value | Measures | Pip package |
|--------|-------------------|----------|-------------|
| BME280 | `"bme280"` | Temp, humidity, pressure | `adafruit-circuitpython-bme280` (included) |
| BMP280 | `"bmp280"` | Temp, pressure | `adafruit-circuitpython-bmp280` |
| DHT22 / AM2302 | `"dht22"` | Temp, humidity | `adafruit-circuitpython-dht` |
| DHT11 | `"dht11"` | Temp, humidity | `adafruit-circuitpython-dht` |
| DS18B20 | `"ds18b20"` | Temp only | None (uses 1-Wire kernel driver) |
| SHT31 | `"sht31"` | Temp, humidity | `adafruit-circuitpython-sht31d` |
| Mock | `"mock"` | Simulated data | None |

To switch sensors, update `config.json` and install the required pip package:

```bash
source ~/AeroCore/venv/bin/activate
pip install adafruit-circuitpython-dht    # example for DHT22
```

Then set `"sensor": "dht22"` in `config.json` and restart.

### Mock Mode

To run AeroCore without any hardware (for testing, demos, or development on any machine):

```json
"sensor": "mock",
"platform": "mock"
```

This generates realistic simulated data and skips all GPIO access.

## Customization

### BME280 I2C Address

The default I2C address is `0x76`. If your sensor uses `0x77`, update `config.json`:

```json
"bme280_address": "0x77"
```

You can verify your sensor's address with `i2cdetect -y 1`.

### PWM GPIO Pin

The fan PWM signal defaults to **GPIO 18**. To use a different pin, update `config.json`:

```json
"gpio_pin": 12
```

### PWM Frequency

The PWM frequency controls how fast the GPIO pin switches on and off to regulate fan speed. The default is **25,000 Hz (25 kHz)**, which is the industry standard defined by Intel's 4-pin PWM fan specification. At this frequency, the fan runs silently with no audible whine.

Most users should **never need to change this**. However, if you're using a non-standard fan (e.g., a 2-wire or 3-wire fan driven through a MOSFET), a lower frequency may work better. Lower values like 1,000 Hz can cause an audible buzzing noise.

To change it, update `config.json`:

```json
"pwm_freq": 25000
```

> **Note:** Requires a service restart to take effect.

### Running on Boot (systemd)

To start AeroCore automatically on boot, create a systemd service:

```bash
sudo nano /etc/systemd/system/aerocore.service
```

```ini
[Unit]
Description=AeroCore Fan Controller
After=network.target

[Service]
ExecStart=/home/pi/AeroCore/venv/bin/python3 /home/pi/AeroCore/app.py
WorkingDirectory=/home/pi/AeroCore
User=pi
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable aerocore
sudo systemctl start aerocore
```

> **Note:** Adjust the paths above if you cloned the repo to a different location or use a different username.

## Updating

AeroCore can be updated three ways:

**From the dashboard (easiest):**

Admins will see a **System update** panel at the bottom of the dashboard. Click **Check for updates** to pull the latest version from GitHub, then **Restart to apply**.

**From the command line:**

```bash
cd ~/AeroCore
./update.sh
```

**Remote one-liner:**

```bash
curl -sSL https://raw.githubusercontent.com/Guajardian/AeroCore/main/update.sh | bash
```

All methods pull the latest code, update dependencies, and restart the service if running.

## Project Structure

```
AeroCore/
├── app.py              # Flask server, sensor loop, API routes
├── sensors.py          # Sensor driver abstraction layer
├── fan.py              # Fan/PWM control abstraction layer
├── install.sh          # One-command installer
├── update.sh           # Self-update script
├── requirements.txt    # Python dependencies
├── .gitignore          # Excludes config, credentials, and secrets from git
├── LICENSE             # GPL v3 license
├── config.json         # Hardware + fan curve settings (auto-generated, not tracked)
├── users.json          # User credentials (auto-generated, not tracked)
├── .secret_key         # Session signing key (auto-generated, not tracked)
├── dashboard.html      # Main dashboard template
├── login.html          # Login page template
├── setup.html          # First-run setup template
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/data` | Current sensor readings + fan speed + override state |
| `GET` | `/api/history` | Last 12 hours of readings |
| `GET/POST` | `/api/config` | Get or update fan curve & humidity settings |
| `GET/POST` | `/api/override` | Get or set manual override (speed + enabled) |
| `POST` | `/api/profiles/<name>` | Apply a fan profile (silent, default, performance) |
| `GET` | `/api/system` | Pi system stats (CPU temp, uptime, memory) |
| `GET` | `/api/me` | Current user's username and role |
| `GET` | `/api/users` | List all users (admin only) |
| `POST` | `/api/users` | Add a new user (admin only) |
| `DELETE` | `/api/users/<username>` | Delete a user (admin only) |
| `POST` | `/api/change-password` | Change current user's password |
| `POST` | `/api/update` | Pull latest updates from GitHub (admin only) |
| `POST` | `/api/restart` | Restart the aerocore systemd service (admin only) |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'board'` | Install the Adafruit Blinka library: `pip install adafruit-blinka` |
| `ModuleNotFoundError: No module named 'RPi'` | Install RPi.GPIO: `pip install RPi.GPIO` |
| `error: externally-managed-environment` | Use a virtual environment — see the Installation section above |
| `TemplateNotFound` error | Make sure you're running `python app.py` from the AeroCore directory |
| BME280 not detected | Run `i2cdetect -y 1` to verify the sensor address; ensure I2C is enabled |
| Fan not spinning | Check that the fan has external power (12V/5V) and shares a ground with the Pi |
| Permission denied on GPIO | Run with `sudo` or add your user to the `gpio` group: `sudo usermod -aG gpio $USER` |

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE). You are free to use, modify, and distribute this software, but any derivative work must also be released under the GPL v3 with full source code.
