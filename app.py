from pythonping import ping
from twilio.rest import Client
import time
from dotenv import load_dotenv
import os

# Load environment file
load_dotenv()
# Assign all loaded .env variables
network_host = os.environ.get("network_host")
from_num = os.environ.get("from_num")
to_num = os.environ.get("to_num")
account_sid = os.environ.get("twil_sid")
auth_token = os.environ.get("twil_token")


# Create Network object
class Network:
    def __init__(self, host_ip):
        self.host_ip = host_ip

    def ping_host(self):
        status = str(ping(self.host_ip, count=1)).lower()
        if "host unreachable" in status or "100% packet loss" in status or "timed out" in status:
            return "OFFLINE"
        return "ONLINE"

    def notification(self, message):
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            to=to_num,
            from_=from_num,
            body=f"{message}")

        print(f"SMS notification has been sent to: {message.to}\n")

    def monitor(self):
        fail_counter = 0
        while fail_counter < 3:
            if Network.ping_host(self) == "ONLINE":
                print("Network is online.")
                print("Checking again in one minute...\n")
                time.sleep(60)
            if Network.ping_host(self) == "OFFLINE":
                print("Network is unreachable.")
                print("Checking again in 30 seconds...\n")
                time.sleep(30)
                fail_counter += 1
        if fail_counter == 3:
            print("Network is offline.")
            print(f"Sending notification SMS.")
            return "OFFLINE"


network = Network(network_host)

# Start application loop
while True:
    if network.monitor() == "OFFLINE":
        # Send SMS that network is offline after 3 missed ping requests.
        network.notification("Home network is offline.")
        # Mark network as offline
        offline = True
    # If network is offline, perform this loop until restored.
    while offline is True:
        if network.ping_host() == "ONLINE":
            print('Network is back online')
            print(f"Sending restore notification SMS.")
            network.notification("Home network is back online.")
            offline = False
            time.sleep(5)
        else:
            offline = True
            print("Network is still offline...")
            print("Checking again in 30 seconds...\n")
            time.sleep(30)
