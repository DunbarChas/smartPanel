# RGB LED Matrix MQTT Display
## Description
This project allows you to send messages to an RGB LED matrix via MQTT. The messages are displayed on the matrix, making it a great tool for notifications, alerts, or just for fun!

## Installation

### Prerequisites
- Raspberry Pi with Python 3 installed
- Internet connection

## Overview
This project allows you to display scrolling text on an RGB LED matrix connected to a Raspberry Pi, controlled via MQTT messages. The display is double-buffered for smooth scrolling and uses Python with the `rgbmatrix` and `paho-mqtt` libraries.

## Features
- Scrolls text on an RGB LED matrix.
- Receives text messages via MQTT to dynamically update the display.
- Configurable through environment variables using a `.env` file.

## Requirements
- Raspberry Pi with an RGB LED Matrix (e.g., 16x32).
- Python 3.x.
- `paho-mqtt` and `python-dotenv` libraries.
- Fonts located in the `fonts/` directory.

## Setup

### Step 1. Clone the Repository
 ```bash
    git clone https://github.com/DunbarChas/smartPanel.git
    cd smartPanel
 ```
### Step 2. Run the Setup Script
 ```bash
     chmod +x setup.sh
    sudo ./setup.sh
 ```
### Step 3. Configure the Environment Variables
- Modify the '.env' file in the project directory and set the following variables:
``` ini
  MQTT_BROKER=your_broker_address
  MQTT_PORT=1883
  MQTT_TOPIC=your/topic
  MQTT_CLIENT_ID=your_client_id
  MQTT_USERNAME=your_username
  MQTT_PASSWORD=your_password
```
### Step 4. Start the Service
 ```bash
    sudo systemctl start smartPanel.service
 ```
### Step 5. Create Entries in HomeAssistant
- configuration.yaml
- create / update the input_text section to add:
``` yaml
input_text: 
    mqtt_message:
        name: MQTT Message
        initial: ""
        max: 256
    mqtt_color:
        name: MQTT Color
        initial: "[0, 255, 0]"
        max: 256
    mqtt_font:
        name: MQTT Font
        initial: ""
        max: 256
```
- scripts.yaml
- create a send_mqtt_message (or similarly named section)
``` yaml
 send_mqtt_message:
    alias: Send MQTT Message
    sequence:
      - service: mqtt.publish
        data:
            topic: "YOUR/TOPIC"
            payload: >
             { 
                "message": "{{states('input_text.mqtt_message')}}" , 
                "brightness": 1,
                "timestamp": "{{ now().isoformat() }}",
                "status": "online",
                "color": "{{states('input_text.mqtt_color')}}",
                "font": "{{states('input_text.mqtt_font')}}"
                
             }
            qos: 1
            retain: true

```
### Step 6. Create a custom card in love lance (Main Home Assistant dashboard)
 While this is highly dependent on how you would like your Home Assistant dasboard to look here is a simple one to get you started! 
 ``` yaml
type: vertical-stack
cards:
  - type: entities
    entities:
      - entity: input_text.mqtt_message
        name: Enter SmartPanel Message
  - type: button
    name: Send!
    show_state: false
    tap_action:
      action: call-service
      service: script.send_mqtt_message

```
## Troubleshooting
  - IF the service fails to start, you can check the logs:
    - journalctl -u smartPanel.service

## License 
 - This project is licensed under the MIT License - see the [LICENSE](https://github.com/DunbarChas/smartPanel/blob/main/LICENSE) fiel for details
