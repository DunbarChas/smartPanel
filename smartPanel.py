
#!/usr/bin/env python
# Display a runtext with double-buffering.
import logging
import os
from dotenv import load_dotenv
import sys
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
from paho.mqtt import client as mqtt_client
from random import random
import time
from concurrent.futures import ThreadPoolExecutor
import threading
import signal

options = RGBMatrixOptions()
options.rows = 16
options.cols = 32

load_dotenv()
broker = os.getenv('MQTT_BROKER', 'localhost')
port = int(os.getenv('MQTT_PORT', 1883))
topic = os.getenv('MQTT_TOPIC', 'test/topic')
client_id = os.getenv('MQTT_CLIENT_ID', f'client-{random()}')
username = os.getenv('MQTT_USERNAME', None)
password = os.getenv('MQTT_PASSWORD', None)

if not broker or not topic:
    logging.error("MQTT_BROKER and MQTT_TOPIC must be set in the .env file!")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RunText():
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.matrix = RGBMatrix(options=options)
        self.text = "Booting .... Hello World!"
    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("fonts/7x13.bdf")
        textColor = graphics.Color(255, 255, 0)
        pos = offscreen_canvas.width
       
        while True:
            offscreen_canvas.Clear()
            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, self.text)
            pos -= 1
            if (pos + len < 0):
                pos = offscreen_canvas.width

            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

def connect_mqtt(run_text):
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            run_text.text = "Connect to MQTT Broker!"
            logging.info("Connected to MQTT Broker!")
        else:
            run_text.text = "Failed to connect to Broker!"
            logging.error("Failed to connect, return code %d\n", rc)
    def on_message(client, userdata, msg):
        message = msg.payload.decode('utf-8')
        logging.info(f"Received message: {message}")
        run_text.text = message
    try:
        client = mqtt_client.Client(client_id=client_id)
        client.username_pw_set(username=username,password=password)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker,port)
        client.on_disconnect = on_disconnect
        return client
    except Exception as e:
        logging.error(f"Failed to connect to MQTT Broker: {e}")
        sys.exit(1)
    
    

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

def on_disconnect(client, userdata, rc):
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            return
        except Exception as err:
             logging.error(err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1



def start_mqtt(client):
    client.loop_forever()

def start_display(run_text):
    try:
        run_text.run()
    except Exception as e:
        logging.error(f"Failed to initialize RGB Matrix: {e}")
        sys.exit(1)

haltCalled = False
def stop():
    global haltCalled
    haltCalled = True
    client.disconnect()
    run_text.matrix.Clear()

mqtt_thread = None
display_thread = None

def handle_exit(signum, frame):
    global mqtt_thread, display_thread
    if mqtt_thread:
        mqtt_thread.join()
    if display_thread:
        display_thread.join()
    stop()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# Main function
if __name__ == "__main__":
    run_text = RunText()
    
    client = connect_mqtt(run_text)
    client.subscribe(topic)
        
    mqtt_thread = threading.Thread(target=start_mqtt, args=(client,))
    display_thread = threading.Thread(target=start_display, args=(run_text,))
        
    mqtt_thread.start()
    display_thread.start()
    try:
        while True:
            if haltCalled:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        handle_exit(None, None)
