
#!/usr/bin/env python
# Display a runtext with double-buffering.
import logging
import os
from dotenv import load_dotenv
import sys
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions
from paho.mqtt import client as mqtt_client
from datetime import datetime, timedelta
from random import random
import json
import ast
import asyncio

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
class HomeAssistantMessage:
    def __init__(self, message: str = "", brightness: int = 100, timestamp: str = "", status: str = "", color: str = "", font: str = ""):
        self.message = message
        self.brightness = brightness
        self.timestamp = datetime.fromisoformat(timestamp) if timestamp else datetime.now()  # Convert string to datetime object
        self.status = status
        self.color = color
        self.font = font
    def __repr__(self):
        return (f"HomeAssistantMessage(message={self.message}, brightness={self.brightness}, "
                f"timestamp={self.timestamp}, status={self.status}, color={self.color}, font={self.font})")


class RunText():
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.matrix = RGBMatrix(options=options)
        self.text = "Booting .... Hello World!"
        self.ham = HomeAssistantMessage()
        self.currentFont = "fonts/7x13.bdf"
        self.currentColor = [255, 255, 0]
        self.font_changed = False
        self.color_changed = False

    async def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        textColor = graphics.Color(*self.currentColor)
        pos = offscreen_canvas.width

        while True:
            if datetime.now().replace(tzinfo=None) > self.ham.timestamp.replace(tzinfo=None) + timedelta(hours=2):
                self.text = ""
            offscreen_canvas.Clear()

            # Reload the font if it changed
            if self.font_changed:
                font.LoadFont(self.currentFont)
                self.font_changed = False

            # Update color if it changed
            if self.color_changed:
                textColor = graphics.Color(*self.currentColor)
                self.color_changed = False

            len = graphics.DrawText(offscreen_canvas, font, pos, 10, textColor, self.text)
            pos -= 1
            if (pos + len < 0):
                pos = offscreen_canvas.width
            await asyncio.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

    async def update_text(self, ham):
        self.ham = ham
        self.text = ham.message

        if ham.font and ham.font != self.currentFont:
            self.currentFont = ham.font
            self.font_changed = True

        if ham.color and ham.color != self.currentColor:
            try:
                self.currentColor = ast.literal_eval(ham.color)
                self.color_changed = True
            except (ValueError, SyntaxError) as e:
                logging.error(f"Failed to parse color: {ham.color}. Error: {e}")


async def connect_mqtt(run_text):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            run_text.text = "Connected to MQTT Broker!"
            logging.info("Connected to MQTT Broker!")
        else:
            run_text.text = "Failed to connect to Broker!"
            logging.error("Failed to connect, return code %d\n", rc)
    def on_message(client, userdata, msg):
        message = msg.payload.decode('utf-8')
        try:
            ham = HomeAssistantMessage(**json.loads(message))
            run_text.update_text(ham)
            logging.info(f"Ham data is: {ham}")
        except json.JSONDecodeError as e:
        
            logging.error(f"Attempting to decode the message caused a json Decoding error the following error: {e} \n the message received was: {message} \n check to make sure the syntax of the payload is correct!")
        
        except Exception as e:
            logging.error(f"Attempting to decode the message caused a generic exception the error was: {e} \n the message received was: {message}")

    try:
        client = mqtt_client.Client(client_id=client_id)
        client.username_pw_set(username=username,password=password)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker,port)
        client.on_disconnect = on_disconnect
        client.loop_start()
        return client
    except Exception as e:
        logging.error(f"Failed to connect to MQTT Broker: {e}")
        sys.exit(1)
    
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

async def on_disconnect(client, userdata, rc):
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        await asyncio.sleep(reconnect_delay)
        try:
            client.reconnect()
            return
        except Exception as err:
             logging.error(err)
        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1

def handle_exit(sig, frame):
    logging.warning("Shutting down gracefully...")
    asyncio.get_event_loop().stop()

async def main():

    run_text = RunText()
    client = await connect_mqtt(run_text)
    client.subscribe(topic)
    
    display_task = asyncio.create_task(await run_text.run())
    await display_task

# Main function
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
