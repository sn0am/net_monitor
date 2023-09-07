from pythonping import ping
from twilio.rest import Client
import time
from dotenv import load_dotenv
import os
import socket
from datetime import datetime

# Load environment file
load_dotenv()
# Assign all loaded .env variables
network_host = os.environ.get("network_host")
from_num = os.environ.get("from_num")
to_num = os.environ.get("to_num")
account_sid = os.environ.get("twil_sid")
auth_token = os.environ.get("twil_token")

text_fail_counter = 0


def set_text_counter(value):
    global text_fail_counter
    text_fail_counter = value
    return text_fail_counter


# Create Network object
class Network:
    def __init__(self, host_ip):
        self.host_ip = host_ip

    def ping_host(self):
        try:
            status = str(ping(self.host_ip, count=1)).lower()
            if "host unreachable" in status or "100% packet loss" in status or "timed out" in status:
                return "OFFLINE"
            return "ONLINE"
        except:
            return "ERROR"

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
                if text_fail_counter != 0:
                    network.notification("DO (net_monitor):\n\nApplication has recovered.")
                    set_text_counter(0)
                time.sleep(60)
            elif Network.ping_host(self) == "OFFLINE":
                print("Network is unreachable.")
                print("Checking again in 30 seconds...\n")
                time.sleep(30)
                fail_counter += 1
            elif Network.ping_host(self) == "ERROR":
                return "ERROR"
        if fail_counter == 3:
            print("Network is offline.")
            print(f"Sending notification SMS.")
            return "OFFLINE"


# Start application loop
while True:
    try:
        network = Network(socket.gethostbyname(network_host))
        if network.monitor() == "OFFLINE":
            # Send SMS that network is offline after 3 missed ping requests.
            network.notification("DO (net_monitor):\n\nHome network is offline.")
            # Mark network as offline
            offline = True
            start_time = datetime.now()

        if network.ping_host() == "ERROR":
            offline = True
            print("Error occurred while pinging host.")

        # If network is offline, perform this loop until restored.
        while offline is True:
            if network.ping_host() == "ONLINE":
                if start_time:
                    print('Network is back online')
                    print(f"Sending restore notification SMS.")
                    end_time = datetime.now()
                    duration = end_time - start_time
                    duration = str(duration).split('.')[0]
                    network.notification("DO (net_monitor):\n\nHome network is back online.\n"
                                         f"(Downtime: {duration})")
                else:
                    network.notification("DO (net_monitor):\n\nApplication has recovered.")
                offline = False
                time.sleep(5)
            else:
                offline = True
                print("Unable to ping network...")
                print("Trying again in 30 seconds...\n")
                time.sleep(30)
                network = Network(socket.gethostbyname(network_host))

    except:
        if text_fail_counter == 0:
            network = Network('1.1.1.1')
            network.notification("DO (net_monitor):\n\nError occurred while resolving host."
                                 "\n\nCheck application for errors.\n\nMonitoring is down.")
            print("Error occurred while resolving host. Check application for errors. Retrying...\n")
            set_text_counter(1)
        print('Error occurred in loop, retrying...\n')
        time.sleep(5)
