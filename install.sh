#!/bin/bash

set -e

REPO_URL="https://github.com/andrew-kemp/AzureDNSSyncv2.0.git"
TMP_DIR=~/azurednssync_tmp
INSTALL_DIR="/opt/azurednssync2"
APP_DIR="$INSTALL_DIR/app"
SERVICE_NAME="azurednssync2"
GROUP="azurednssync"
USER_SERVICE="$USER"
DATA_DIR="/var/lib/$SERVICE_NAME"
CERT_DIR="$DATA_DIR/certs"
CERT_NAME="cert"
CERT_PATH="$CERT_DIR/${CERT_NAME}.pem"
KEY_PATH="$CERT_DIR/${CERT_NAME}.key"
MFA_FILE="$DATA_DIR/user_mfa.json"
LOG_DIR="/var/log/$SERVICE_NAME"
CONFIG_DIR="/etc/azurednssync2"
CONFIG_FILE="$CONFIG_DIR/config.yaml"

echo "Updating system packages..."
sudo apt-get update

# Determine Python version for venv package
PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
VENV_PKG="python${PYTHON_VERSION}-venv"

echo "Installing required system packages..."
sudo apt-get install -y python3 python3-pip "$VENV_PKG" git libpam0g-dev gcc libssl-dev libffi-dev openssl

echo "Cloning the repository to $TMP_DIR..."
rm -rf "$TMP_DIR"
git clone "$REPO_URL" "$TMP_DIR"

echo "Creating target directories..."
sudo mkdir -p $APP_DIR/static
sudo mkdir -p $APP_DIR/templates
sudo mkdir -p $APP_DIR/utils
sudo mkdir -p $APP_DIR/tests
sudo mkdir -p $INSTALL_DIR/docs
sudo mkdir -p $INSTALL_DIR/scripts
sudo mkdir -p $CERT_DIR
sudo mkdir -p $LOG_DIR
sudo mkdir -p $CONFIG_DIR

echo "Copying application files to $APP_DIR..."
sudo rsync -a "$TMP_DIR/app/" "$APP_DIR/"
sudo cp "$TMP_DIR/app/run.py" "$APP_DIR/run.py"
sudo cp "$TMP_DIR/requirements.txt" "$INSTALL_DIR/requirements.txt"
[ -d "$TMP_DIR/docs" ] && sudo rsync -a "$TMP_DIR/docs/" "$INSTALL_DIR/docs/"
[ -d "$TMP_DIR/scripts" ] && sudo rsync -a "$TMP_DIR/scripts/" "$INSTALL_DIR/scripts/"

echo "Setting permissions for system-owned directories..."
sudo chown -R root:$GROUP $DATA_DIR $LOG_DIR $CONFIG_DIR
sudo chmod 755 $DATA_DIR $LOG_DIR $CONFIG_DIR
sudo chmod 750 $CERT_DIR

# --- Create self-signed certificate and key if missing ---
echo "Generating self-signed certificate (if needed)"
cd "$CERT_DIR"
if [ ! -f "$KEY_PATH" ] || [ ! -f "$CERT_PATH" ]; then
    sudo openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
        -keyout "$KEY_PATH" \
        -out "$CERT_PATH" \
        -subj "/CN=azurednssync2"
    sudo chmod 600 "$KEY_PATH" "$CERT_PATH"
else
    echo "Certificate files already exist: $KEY_PATH, $CERT_PATH"
fi

# --- Show public certificate block for Azure AD registration ---
echo "Azure App Registration Certificate Block"
awk '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/ {print}' "$CERT_PATH"
echo

# --- Group setup for cert access ---
if getent group $GROUP >/dev/null; then
    echo "Group $GROUP exists, removing and recreating it to ensure fresh membership..."
    sudo gpasswd -d $USER $GROUP || true
    sudo groupdel $GROUP
fi

sudo groupadd $GROUP
sudo usermod -a -G $GROUP $USER

sudo chown root:$GROUP $CERT_DIR
sudo chmod 750 $CERT_DIR
sudo chown root:$GROUP "$CERT_PATH" "$KEY_PATH"
sudo chmod 640 "$CERT_PATH" "$KEY_PATH"

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

if ! python -c "import six" &>/dev/null; then
    echo "'six' module not found after requirements install, installing via pip..."
    pip install six
fi

echo "Cleaning up temporary directory..."
rm -rf "$TMP_DIR"

# --- Create persistent MFA data file if it doesn't exist ---
if [ ! -f "$MFA_FILE" ]; then
    echo "{}" | sudo tee "$MFA_FILE" > /dev/null
fi

sudo chown root:$GROUP "$MFA_FILE"
sudo chmod 660 "$MFA_FILE"
sudo chown root:$GROUP "$DATA_DIR"
sudo chmod 770 "$DATA_DIR"

# --- Ensure config.yaml exists and is writable by group ---
if [ ! -f "$CONFIG_FILE" ]; then
    echo "# AzureDNSSync2 config" | sudo tee "$CONFIG_FILE" > /dev/null
fi
sudo chown root:$GROUP "$CONFIG_FILE"
sudo chmod 660 "$CONFIG_FILE"

echo "Creating systemd service file..."

SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Azure DNS Sync 2.0 Flask App
After=network.target

[Service]
User=$USER_SERVICE
Group=$GROUP
WorkingDirectory=$APP_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python3 run.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd, enabling $SERVICE_NAME service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME

echo ""
echo "=========================================================================="
echo "INSTALL COMPLETE"
echo "=========================================================================="
echo ""
echo "IMPORTANT:"
echo " - You must start a new shell with the correct group membership before starting the service."
echo " - Either log out and log in, or run:  sudo newgrp $GROUP"
echo ""
echo "Once you have done that, start the service with:"
echo "  sudo systemctl start $SERVICE_NAME"
echo ""
echo "To check status: sudo systemctl status $SERVICE_NAME"
echo "To see logs:    sudo journalctl -u $SERVICE_NAME -f"
echo "=========================================================================="
echo ""
