#!/bin/bash

set -e

echo "Updating system packages..."
sudo apt update

echo "Installing required system packages..."
sudo apt install -y python3 python3-pip python3-venv libpam0g-dev gcc libssl-dev libffi-dev

echo "Creating Python virtual environment..."
cd /opt/azurednssync2
python3 -m venv venv

echo "Activating virtual environment and installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up folder permissions..."
sudo chmod -R 755 /opt/azurednssync2/app
sudo chmod -R 755 /opt/azurednssync2

echo "Install complete!"
echo "To run the app:"
echo "cd /opt/azurednssync2"
echo "source venv/bin/activate"
echo "sudo python3 run.py"
