import network
import socket
import time
import json
from machine import Pin
import dht

# --- CONFIG ---
SSID="COSMOTE-494184"
PASSWORD="8eht2fmbasa2s6r9xp6s"

DHT_PIN = 15  # GP15


wlan = network.WLAN(network.STA_IF)  # <-- global
sensor = dht.DHT22(Pin(DHT_PIN, Pin.IN, Pin.PULL_UP))


def connect_wifi():
    """Connect (or reconnect) to WiFi and return IP."""
    if not wlan.active():
        wlan.active(True)
        # Disable power-save mode (Pico W specific)
        try:
            wlan.config(pm=0xa11140)
        except:
            pass

    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)

    ip = wlan.ifconfig()[0]
    print("Connected. IP:", ip)
    return ip


def make_server_socket(ip):
    addr = (ip, 80)
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    print("Server listening on http://%s/" % ip)
    return s


def read_dht_avg(samples=10, delay=2):
    temps = []
    hums = []
    for i in range(samples):
        try:
            print("Reading DHT, sample", i+1)
            sensor.measure()
            t = sensor.temperature()
            h = sensor.humidity()
            print(t, h)
            temps.append(t)
            hums.append(h)
        except OSError as e:
            print("Sensor error during measurement:", e)
        time.sleep(delay)

    if not temps or not hums:
        print("No Valid DHT readings")
        return None, None

    return sum(temps) / len(temps), sum(hums) / len(hums)


def get_datetime_str():
    t = time.localtime()
    date_str = "%04d-%02d-%02d" % (t[0], t[1], t[2])
    time_str = "%02d:%02d" % (t[3], t[4])
    return date_str + " " + time_str


def start_server():
    ip = connect_wifi()
    s = make_server_socket(ip)

    while True:
        # If WiFi dropped while idle, reconnect & recreate socket
        if not wlan.isconnected():
            print("WiFi lost, reconnecting...")
            try:
                s.close()
            except:
                pass
            ip = connect_wifi()
            s = make_server_socket(ip)
            continue

        try:
            client, client_addr = s.accept()
            print("Client connected:", client_addr)
            client.settimeout(5)

            request = client.recv(1024)  # you can ignore contents

            temp, hum = read_dht_avg(samples=3, delay=1)

            data = {
                "temp": temp,
                "humidity": hum,
                "datetime": get_datetime_str()
            }
            body = json.dumps(data)

            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "Content-Length: " + str(len(body)) + "\r\n"
                "Connection: close\r\n"
                "\r\n" +
                body
            )
            client.send(response)
            client.close()

        except OSError as e:
            # Any socket error -> close & recreate socket
            print("Socket error:", e)
            try:
                client.close()
            except:
                pass
            try:
                s.close()
            except:
                pass
            ip = connect_wifi()
            s = make_server_socket(ip)

# --- MAIN ---
ip = connect_wifi()
start_server()