#!/bin/bash

sudo apt-get update
sudo apt-get install -y git-core cmake build-essential libssl-dev python3-pip

if [ ! -d "rpi-rgb-led-matrix" ]; then
    git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
    cd rpi-rgb-led-matrix
    make build-python
    sudo make install-python
    cd ..
else
    echo "RGB Matrix library already cloned and installed."
fi

pip3 install -r requirements.txt

PROJECT_DIR=$(pwd)
USER=$(whoami)

if [ ! -f "/etc/systemd/system/smartPanel.service" ]; then
    echo "[Unit]
Description=Smart Panel MQTT to RGB Matrix
After=network.target

[Service]
ExecStart=/usr/bin/python3 $PROJECT_DIR/smartPanel.py
WorkingDirectory=$PROJECT_DIR
Restart=always
User=root

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/smartPanel.service > /dev/null

    # Enable and start the service
    sudo systemctl enable smartPanel.service
    sudo systemctl start smartPanel.service

    # Verify if the service is running
    if systemctl is-active --quiet smartPanel.service; then
        echo "Setup complete! The RGB Matrix display service is now running."
    else
        echo "Setup failed! The RGB Matrix display service is not running."
    fi
else
    echo "smartPanel service already exists."
fi
