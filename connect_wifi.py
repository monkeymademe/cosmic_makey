import network
import time

def connect_wifi(ssid, password, timeout=10):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"Connecting to Wi-Fi '{ssid}'...")
        wlan.connect(ssid, password)

        # Wait until connected or timeout
        start_time = time.time()
        while not wlan.isconnected():
            if time.time() - start_time > timeout:
                raise RuntimeError("Wi-Fi connection timed out")
            time.sleep(0.5)

    print("✅ Connected:", wlan.ifconfig())
    return wlan