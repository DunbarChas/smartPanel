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
    ./setup.sh
 ```
### Step 3. Configure the Environment Variables
 - Modify the '.env' file in the project directory and set the following variables:
 - MQTT_BROKER=your_broker_address
 - MQTT_PORT=1883
 - MQTT_TOPIC=your/topic
 - MQTT_CLIENT_ID=your_client_id
 - MQTT_USERNAME=your_username
 - MQTT_PASSWORD=your_password

### Step 4. Start the Service
 ```bash
    sudo systemctl start smartPanel.service
 ```

## Troubleshooting
  - IF the service fails to start, you can check the logs:
    - journalctl -u smartPanel.service

## License 
 - This project is licensed under the MIT License - see the [LICENSE](https://github.com/DunbarChas/smartPanel/blob/main/LICENSE) fiel for details
