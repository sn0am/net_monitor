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
text_delay = 0
app_down_time = datetime.now()


def set_text_counter(value):
    global text_fail_counter
    text_fail_counter = value
    return text_fail_counter


def set_text_delay(value):
    global text_delay
    text_delay = value
    return text_delay


def set_app_downtime(value):
    global app_down_time
    app_down_time = value
    return app_down_time


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

    # --- [PING] ERROR OCCURS HERE
    def monitor(self):
        fail_counter = 0
        run_count = 0
        while fail_counter < 3 and run_count < 50:
            if Network.ping_host(self) == "ONLINE":
                print("Network is online.")
                print("Checking again in one minute...\n")
                time.sleep(60)
            elif Network.ping_host(self) == "OFFLINE":
                print("Network is unreachable.")
                print("Checking again in 30 seconds...\n")
                time.sleep(30)
                fail_counter += 1
            elif Network.ping_host(self) == "ERROR":
                return "ERROR"
            run_count += 1
        if fail_counter == 3:
            print("Network is offline.")
            print(f"Sending notification SMS.")
            return "OFFLINE"


# Start application loop
while True:
    try:
        # --- [DNS] ERROR OCCURS HERE
        network = Network(socket.gethostbyname(network_host))

        set_text_delay(0)

        if text_fail_counter != 0:
            app_return_time = datetime.now()
            app_down_duration = app_return_time - app_down_time
            app_down_duration = str(app_down_duration).split('.')[0]
            network.notification("DO (net_monitor):\n\n[DNS] has recovered.\n"
                                 f"(Downtime: {app_down_duration})")
            set_text_counter(0)

        # --- [PING] ERROR OCCURS HERE
        if network.monitor() == "OFFLINE":
            # Send SMS that network is offline after 3 missed ping requests.
            network.notification("DO (net_monitor):\n\nHome network is offline.")
            # Mark network as offline
            offline = True
            start_time = datetime.now()

            # If network is offline, perform this loop until restored.
            while offline is True:
                if network.ping_host() == "ONLINE":
                    print('Network is back online')
                    print(f"Sending restore notification SMS.")
                    end_time = datetime.now()
                    duration = end_time - start_time
                    duration = str(duration).split('.')[0]
                    network.notification("DO (net_monitor):\n\nHome network is back online.\n"
                                         f"(Downtime: {duration})")
                    offline = False
                    time.sleep(5)
                else:
                    offline = True
                    print("Unable to ping network...")
                    print("Trying again in 30 seconds...\n")
                    time.sleep(30)
                    # --- [DNS] ERROR OCCURS HERE
                    network = Network(socket.gethostbyname(network_host))

        # --- RUNS IF [PING] ERROR OCCURS
        elif network.monitor() == "ERROR":
            status_code = "ERROR"
            ping_down_start = datetime.now()
            print("Error occurred while pinging host.")
            network.notification("DO (net_monitor):\n\nAn error occurred during [PING]"
                                 "\nMonitoring is down.")
            while status_code == "ERROR":
                status_code = network.ping_host()
                time.sleep(15)
                network = Network(socket.gethostbyname(network_host))
            ping_restore_time = datetime.now()
            ping_down_time = ping_restore_time - ping_down_start
            ping_down_time = str(ping_down_time).split('.')[0]
            network.notification("DO (net_monitor):\n\n[PING] has recovered.\n"
                                 f"(Downtime: {ping_down_time})")

    except:
        # --- RUNS IF [DNS] ERROR OCCURS
        if text_delay > 2:
            # Send SMS that error occurred after 3 failed DNS attempts.
            if text_fail_counter == 0:
                network = Network('1.1.1.1')
                network.notification("DO (net_monitor):\n\nAn error occurred during [DNS]"
                                     "\nMonitoring is down.")
                print("Error occurred while resolving host. Check application for errors. Retrying...\n")
                set_text_counter(1)
                set_app_downtime(datetime.now())
        text_delay += 1
        print('Error occurred in loop, retrying...\n')
        time.sleep(30)
