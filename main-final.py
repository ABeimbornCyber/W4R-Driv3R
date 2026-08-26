import network
import binascii
from machine import Pin, I2C
import ssd1306
import time
import machine
from micropyGPS import MicropyGPS
import uos
from machine import Pin, SoftSPI
from sdcard import SDCard
import os
import sys


cs = 2
sck = 18
mosi = 8
miso = 5

WIGLE_HEADER = (
    "WigleWifi-1.6,"
    "appRelease=1.0,"
    "model=ESP32S3,"
    "release=1.28.0,"
    "device=W4R-Dr1v3R,"
    "display=SSD1306,"
    "board=ESP32S3,"
    "brand=DIY,"
    "star=Sol,"
    "body=3,"
    "subBody=0\n"
    "MAC,SSID,AuthMode,FirstSeen,Channel,Frequency,RSSI,"
    "CurrentLatitude,CurrentLongitude,AltitudeMeters,"
    "AccuracyMeters,RCOIs,MfgrId,Type\n"
)




sta_if = network.WLAN(network.WLAN.IF_STA)
ap_if = network.WLAN(network.WLAN.IF_AP)

i2c = I2C(sda=Pin(7), scl=Pin(6))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

#Activate Station
sta_if.active(True)

display.fill(0)



spisd = SoftSPI(
    -1,
    miso=Pin(miso),
    mosi=Pin(mosi),
    sck=Pin(sck),
)

sd_available = False




try:
    sd = SDCard(spisd, Pin(cs))
    print(f'Root dir: {uos.listdir()}')
    try:
        uos.umount('/sd')
    except:
        pass
    vfs = uos.VfsFat(sd)
    uos.mount(vfs, '/sd')
    print(f'Root dir: {uos.listdir()}')
    sd_available = True
except Exception as e:
    print("SD card error:", e)
    display.fill(0)
    display.text("W4R Dr1v3R", 24, 0)
    display.text("SD CARD ERROR", 16, 20)
    display.text("NO SD CARD", 24, 32)
    display.text("INSERT CARD", 20, 44)
    display.show()
    time.sleep(10)
    machine.reset()
    raise SystemExit

try:
    os.mkdir("/sd/captures")
except OSError:
    pass

# Instantiate the micropyGPS object
my_gps = MicropyGPS()
gps_serial = machine.UART(2, baudrate=9600, tx=43, rx=44)

def capture_filename(gps):
    return "/sd/captures/capture_{:04d}-{:02d}-{:02d}_{:02d}{:02d}{:02d}.csv".format(
        2000 + int(gps.date[2]),
        int(gps.date[1]),
        int(gps.date[0]),
        int(gps.timestamp[0]),
        int(gps.timestamp[1]),
        int(gps.timestamp[2])
    )

def gps_timestamp(gps):
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        2000+int(gps.date[2]),       # year
        int(gps.date[1]),       # month
        int(gps.date[0]),       # day
        int(gps.timestamp[0]),  # hour
        int(gps.timestamp[1]),  # minute
        int(gps.timestamp[2])   # second
    )



def format_bssid(bssid):
    raw = binascii.hexlify(bssid).decode()

    return ":".join(
        raw[i:i+2]
        for i in range(0, 12, 2)
    )

def wifi_frequency(channel):
    if channel == 14:
        return 2484
    elif 1 <= channel <= 13:
        return 2407 + (channel * 5)
    else:
        return 0


def gps_decimal(coord):
    degrees = coord[0]
    minutes = coord[1]
    direction = coord[2]

    decimal = degrees + (minutes / 60)

    if direction == "S" or direction == "W":
        decimal = -decimal

    return decimal

def gps_lock(data):
    for byte in data:
        stat = my_gps.update(chr(byte))
        if stat is not None and my_gps.satellites_in_use >=10 and my_gps.hdop < 1.0 and my_gps.date[0] != 0:
            
            return True
        else:
            
            return False
    
gps_locked = False

if not gps_locked:

    display.fill(0)
    display.text("W4R Dr1v3R", 24, 0, 1)
    display.text("Waiting for GPS", 0, 25, 1)
    display.text("Lock...", 0, 38, 1)
    display.show()





known_networks = set()
first_run = True
while True:
    #time.sleep(3)
    
    try:
        
        while gps_serial.any():
            data = gps_serial.read()
            if gps_lock(data):
                gps_locked = True
                if (first_run) and sd_available:
                    filename = capture_filename(my_gps)
                    try:
                        os.stat(filename)
                    except OSError:
                        with open(filename, "w") as f:
                            f.write(WIGLE_HEADER)
                            f.flush()
                first_run = False
                display.fill(0)
                #print("Satellite Lock Achieved!")
                networks = sta_if.scan()
                for wifi_network in networks:
                    SSID=str(wifi_network[0])[2:-1]
                    print("-----")
                    print(SSID)
                    BSSID = format_bssid(wifi_network[1])
                    if BSSID not in known_networks:
                        known_networks.add(BSSID)
                    print(BSSID)
                    CHANNEL=str(wifi_network[2])
                    print(CHANNEL)
                    FREQUENCY=wifi_frequency(int(CHANNEL))
                    RSSI=str(wifi_network[3])
                    print(RSSI)
                    security_protocols = ["OPEN", "WEP", "WPA-PSK", "WPA2-PSK", "WPA/WPA2-PSK", "EAP", "EAP", "WPA3-PSK", "WPA2/WPA3-PSK", "WAPI-PSK", "OWE", "WPA3-ENT-SUITE-B-192-BIT", "DUMMY", "DUMMY", "DPP", "WPA3-ENTERPRISE-ONLY", "WPA2-ENTERPRISE-TRANSITION-MODE", "WPA3-ENTERPRISE", "UNKNOWN"]
                    SECURITY=security_protocols[int(wifi_network[4])]
                    print(SECURITY)
                    if wifi_network[5] == 0:
                        STATUS="VISIBLE"
                        print("Status: Visible")
                    elif wifi_network[5] == 1:
                        STATUS="HIDDEN"
                        print("Status: Hidden")
                    TIMESTAMP = TIMESTAMP = gps_timestamp(my_gps)
                    with open(filename, "a") as f:
                        f.write((f'{BSSID},{SSID},[{SECURITY}],{TIMESTAMP},{CHANNEL},{FREQUENCY},{RSSI},{gps_decimal(my_gps.latitude)},{gps_decimal(my_gps.longitude)},{my_gps.altitude},{5.00},,,WIFI') + "\n")
                        f.flush()
                    
                # Print parsed GPS data
                print('UTC Timestamp:', my_gps.timestamp)
                print('Date:', my_gps.date_string('long'))
                print('Latitude:', my_gps.latitude_string())
                print('Longitude:', my_gps.longitude_string())
                print('Altitude:', my_gps.altitude)
                print('Satellites in use:', my_gps.satellites_in_use)
                print('Horizontal Dilution of Precision:', my_gps.hdop)
                print()
                
                display.text("W4R Dr1v3R", int(64-(len("W4R Dr1v3R")*8)/2.0), 0, 1)
                display.text(my_gps.date_string('short'), int(64-(len(my_gps.date_string('short'))*8)/2.0), 9, 1)

                LAT="LAT:" + str(my_gps.latitude[0]) + " " + str(my_gps.latitude[1])[:6] + "'" + str(my_gps.latitude[2])
                LON="LON:" + str(my_gps.longitude[0]) + " " + str(my_gps.longitude[1])[:6] + "'" + str(my_gps.longitude[2])
                display.text(LAT, 0, 18, 1)
                display.text(LON, 0, 27, 1)
                display.text("ALT:" + str(my_gps.altitude) + "M", 0, 36, 1)
                display.text("SATS IN USE: " + str(my_gps.satellites_in_use), 0, 45, 1)
                display.text("# of APs " + str(len(known_networks)), 0, 54, 1)
                display.show()
            
                
            
    except Exception as e:
        print(f"An error occurred: {e}")