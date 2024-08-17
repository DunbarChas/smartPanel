#!/usr/bin/env python
import logging
import os
from dotenv import load_dotenv
import sys
from paho.mqtt import client as mqtt_client
from random import random
from datetime import datetime
import time
import threading
import signal
import json

# Load environment variables
load_dotenv()
broker = os.getenv('MQTT_BROKER', 'localhost')
port = int(os.getenv('MQTT_PORT', 1883))
topic = os.getenv('MQTT_TOPIC', 'test/topic')
client_id = os.getenv('MQTT_CLIENT_ID', f'client-{random()}')
username = os.getenv('MQTT_USERNAME', None)
password = os.getenv('MQTT_PASSWORD', None)

if not broker or not topic:
    print("MQTT_BROKER and MQTT_TOPIC must be set in the .env file!")
    logging.error("MQTT_BROKER and MQTT_TOPIC must be set in the .env file!")
    sys.exit(1)
class HomeAssistantMessage:
    def __init__(self, message: str, brightness: int, timestamp: str, status: str):
        self.message = message
        self.brightness = brightness
        self.timestamp = datetime.fromisoformat(timestamp)  # Convert string to datetime object
        self.status = status

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to connect to MQTT broker
def connect_mqtt():
    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Connected to MQTT Broker!")
            logging.info("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {reason_code}")
            logging.error(f"Failed to connect, return code {reason_code}")

    def on_message(client, userdata, msg):
        message = msg.payload.decode('utf-8')
        print(f"The message was: {message}")
        try:
            payload = HomeAssistantMessage(**json.loads(message))
            print(f"Received message: {payload.message}")
        except Exception as e:
            print(f"Error was: {e}")
        logging.info(f"Received message: {message}")

    try:
        print("Connecting to MQTT Broker...")
        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2,client_id=client_id)
        if username and password:
            client.username_pw_set(username=username, password=password)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker, port)
        client.on_disconnect = on_disconnect
        return client
    except Exception as e:
        print(f"Failed to connect to MQTT Broker: {e}")
        logging.error(f"Failed to connect to MQTT Broker: {e}")
        sys.exit(1)
class MessagePayload:
    def __init__(self, message, brightness, timestamp, status):
        self.message = message
        self.brightness = brightness
        self.timestamp = timestamp
        self.status = status


def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT Broker")
    logging.warning("Disconnected from MQTT Broker")
    if rc != 0:
        print("Unexpected disconnection.")
        logging.warning("Unexpected disconnection.")

def start_mqtt(client):
    client.loop_forever()

# Main function
if __name__ == "__main__":
    print("Starting the MQTT test script...")
    client = connect_mqtt()
    print(f"Subscribing to topic: {topic}")
    client.subscribe(topic)

    mqtt_thread = threading.Thread(target=start_mqtt, args=(client,))
    mqtt_thread.start()

    def handle_exit(signum, frame):
        print("Exiting...")
        logging.info("Exiting...")
        client.disconnect()
        mqtt_thread.join()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        handle_exit(None, None)

