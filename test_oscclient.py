from pythonosc.udp_client import SimpleUDPClient
import time, random

ip = "127.0.0.1"
port = 9001

client = SimpleUDPClient(ip, port)

for _ in range(30):
    client.send_message("/avatar/parameters/ShockB2/some/param", [random.random(),])
    time.sleep(0.05)
for _ in range(200):
    client.send_message("/avatar/parameters/pcs/sps/pussy", [random.random(),])
    time.sleep(0.05)
for _ in range(3):
    client.send_message("/avatar/parameters/ShockB2/some/param", [random.random(),])
    time.sleep(0.05)
