#!/bin/bash

set -e

# Variables
REPO_URL="https://github.com/andrew-kemp/AzureDNSSyncv2.0.git"
TMP_DIR=~/azurednssync_tmp
INSTALL_DIR="/opt/azurednssync2"
PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
VENV_PKG="python${PYTHON_VERSION}-venv"

echo "Updating system packages..."
sudo apt-get update

echo "Installing required system packages..."
sudo apt-get install -y python3 python3-pip "$VENV_PKG" git libpam0g-dev gcc libssl-dev libffi-dev

echo "Cloning the repository to $TMP_DIR..."
rm -rf "$TMP_DIR"
git clone "$REPO_URL" "$TMP_DIR"

echo "Creating target directories..."
sudo mkdir -p $INSTALL_DIR/app/static
sudo mkdir -p $INSTALL_DIR/app/templates
sudo mkdir -p $INSTALL_DIR/app/utils
sudo mkdir -p $INSTALL_DIR/app/tests
sudo mkdir -p $INSTALL_DIR/docs
sudo mkdir -p $INSTALL_DIR/scripts
sudo mkdir -p /etc/azurednssync2/certs
sudo mkdir -p /var/log/azurednssync2
sudo mkdir -p /var/lib/azurednssync2

echo "Copying application files to $INSTALL_DIR..."
sudo rsync -a "$TMP_DIR/app/" $INSTALL_DIR/app/
sudo cp "$TMP_DIR/run.py" $INSTALL_DIR/
sudo cp "$TMP_DIR/requirements.txt" $INSTALL_DIR/
[ -d "$TMP_DIR/docs" ] && sudo rsync -a "$TMP_DIR/docs/" $INSTALL_DIR/docs/
[ -d "$TMP_DIR/scripts" ] && sudo rsync -a "$TMP_DIR/scripts/" $INSTALL_DIR/scripts/

echo "Setting permissions for system-owned directories..."
sudo chown -R root:root /etc/azurednssync2 /var/log/azurednssync2 /var/lib/azurednssync2
sudo chmod 755 /etc/azurednssync2 /var/log/azurednssync2 /var/lib/azurednssync2
sudo chmod 700 /etc/azurednssync2/certs

echo "Changing ownership of $INSTALL_DIR to current user for venv setup and file edits..."
sudo chown -R $USER:$USER $INSTALL_DIR

echo "Ensuring 'six' is in requirements.txt..."
if ! grep -q '^six' "$INSTALL_DIR/requirements.txt"; then
    echo "six" >> "$INSTALL_DIR/requirements.txt"
fi

echo "Setting up Python virtual environment..."
cd $INSTALL_DIR
python3 -m venv venv
source venv/bin/activate

echo "Upgrading pip and installing Python requirements (including six)..."
pip install --upgrade pip
pip install -r requirements.txt

# Double-check 'six' installation in case of pip issues
if ! python -c "import six" &>/dev/null; then
    echo "'six' module not found after requirements install, installing via pip..."
    pip install six
fi

echo "Cleaning up temporary directory..."
rm -rf "$TMP_DIR"

echo "Install complete!"
echo ""
echo "To run the app, use:"
echo "  cd $INSTALL_DIR"
echo "  source venv/bin/activate"
echo "  python3 run.py"
echo ""
echo "Do NOT use 'sudo' to run the app unless you specifically need root privileges."
echo "If you must use sudo, run:"
echo "  sudo env \"PATH=\$PATH\" \"VIRTUAL_ENV=\$VIRTUAL_ENV\" python3 run.py"
