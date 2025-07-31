#!/bin/bash

set -e

REPO_URL="https://github.com/andrew-kemp/AzureDNSSyncv2.0.git"
TMP_DIR=~/azurednssync_tmp

echo "Cloning the repository to $TMP_DIR..."
rm -rf "$TMP_DIR"
git clone "$REPO_URL" "$TMP_DIR"

echo "Creating target directories..."
sudo mkdir -p /opt/azurednssync2/app/static
sudo mkdir -p /opt/azurednssync2/app/templates
sudo mkdir -p /opt/azurednssync2/app/utils
sudo mkdir -p /opt/azurednssync2/app/tests
sudo mkdir -p /opt/azurednssync2/docs
sudo mkdir -p /opt/azurednssync2/scripts
sudo mkdir -p /etc/azurednssync2/certs
sudo mkdir -p /var/log/azurednssync2
sudo mkdir -p /var/lib/azurednssync2

echo "Copying application files to /opt/azurednssync2..."
sudo rsync -a "$TMP_DIR/app/" /opt/azurednssync2/app/
sudo cp "$TMP_DIR/run.py" /opt/azurednssync2/
sudo cp "$TMP_DIR/requirements.txt" /opt/azurednssync2/
[ -d "$TMP_DIR/docs" ] && sudo rsync -a "$TMP_DIR/docs/" /opt/azurednssync2/docs/
[ -d "$TMP_DIR/scripts" ] && sudo rsync -a "$TMP_DIR/scripts/" /opt/azurednssync2/scripts/

echo "Setting permissions..."
sudo chown -R root:root /opt/azurednssync2
sudo chown -R root:root /etc/azurednssync2 /var/log/azurednssync2 /var/lib/azurednssync2
sudo chmod -R 755 /opt/azurednssync2
sudo chmod 755 /etc/azurednssync2 /var/log/azurednssync2 /var/lib/azurednssync2
sudo chmod 700 /etc/azurednssync2/certs

echo "Setting up Python virtual environment..."
cd /opt/azurednssync2
sudo python3 -m venv venv
sudo chown -R $USER:$USER venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Cleaning up temporary directory..."
rm -rf "$TMP_DIR"

echo "Install complete!"
echo "To run the app:"
echo "cd /opt/azurednssync2"
echo "source venv/bin/activate"
echo "sudo python3 run.py"
