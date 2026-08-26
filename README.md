# W4R Dr1v3R

W4R Dr1v3R is a portable ESP32-S3-based Wi-Fi mapping and GPS logging device. It scans for nearby Wi-Fi networks, associates discovered access points with GPS coordinates, and saves the collected information in a WiGLE-compatible CSV format to an SD card.

The project is built around an ESP32-S3 and uses an OLED display for status information and a GPS module for location data.

## Features

- Wi-Fi access point discovery
- BSSID, SSID, channel, frequency, RSSI, and security information
- GPS location tracking
- Latitude, longitude, altitude, timestamp, and satellite information
- WiGLE-compatible CSV output
- SD card storage
- SSD1306 OLED status display
- Automatic SD card detection
- Automatic reboot/retry when an SD card is not present
- Displays GPS lock status before beginning Wi-Fi scanning

## Hardware

- ESP32-S3
- SSD1306 128x64 OLED
- GPS module
- MicroSD card module
- MicroSD card
- Wi-Fi-enabled ESP32-S3 board

### Pin Configuration

| Component | ESP32-S3 Pin |
|---|---:|
| SD CS | GPIO 2 |
| SD SCK/CLK | GPIO 18 |
| SD MOSI | GPIO 8 |
| SD MISO | GPIO 5 |
| OLED SDA | GPIO 7 |
| OLED SCL | GPIO 6 |
| GPS TX | GPIO 43 (RX) |
| GPS RX | GPIO 44 (TX) |

## Software

W4R Dr1v3R is written in MicroPython.

The project uses:

- [`ssd1306`](https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html) — OLED display driver
- [`micropyGPS`](https://raw.githubusercontent.com/RuiSantosdotme/Random-Nerd-Tutorials/master/Projects/ESP-MicroPython/micropyGPS.py) — GPS/NMEA parsing
- [`sdcard`](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/storage/sdcard/sdcard.py) — MicroSD card driver
- This project is based in [MicroPython](https://micropython.org/) - ESP32 networking APIs

- Disclaimer - I did not create the above modules, they are borrowed from their corresponding projects. 


## How It Works

On startup, W4R Dr1v3R initializes the OLED, Wi-Fi interface, GPS, and SD card.

The SD card is required for logging. If no card is detected, the device displays an SD card error and waits before restarting and attempting initialization again.

Once the SD card is available, the device waits for a valid GPS lock.

After obtaining a GPS lock, the ESP32 scans for nearby Wi-Fi networks and records information about each discovered access point.

Collected data is written to a timestamped CSV file on the SD card.

The CSV format follows the Wigle Wifi Project's [CSV standard](https://api.wigle.net/csvFormat.html)

## Installation

1. Install MicroPython on the ESP32-S3.
2. Copy the required .py libraries to the device.
3. Copy main.py to the ESP32-S3.
4. Insert a FAT-formatted MicroSD card.
5. Connect the GPS module and OLED.
6. Power on the device.
7. Wait for GPS lock.
8. Wi-Fi observations will be saved to the SD card.


## Project Status

This project is currently under development.

Hardware configurations, GPS lock requirements, display layouts, and logging functionality may change as development continues.

## Disclaimer

This project is intended for educational purposes, wireless-network research, and use on networks and devices for which you have authorization.

Only collect and store wireless-network information where you have appropriate permission to do so.