#!/bin/bash

# Base install directories
BASE_APP_DIR="/opt/azurednssync2"
BASE_CONFIG_DIR="/etc/azurednssync2"
BASE_CERTS_DIR="$BASE_CONFIG_DIR/certs"
BASE_LOG_DIR="/var/log/azurednssync2"
BASE_LIB_DIR="/var/lib/azurednssync2"

# Create directories
sudo mkdir -p "$BASE_APP_DIR"
sudo mkdir -p "$BASE_CONFIG_DIR"
sudo mkdir -p "$BASE_CERTS_DIR"
sudo mkdir -p "$BASE_LOG_DIR"
sudo mkdir -p "$BASE_LIB_DIR"

# Set permissions
sudo chown root:root "$BASE_CONFIG_DIR" "$BASE_CERTS_DIR"
sudo chmod 700 "$BASE_CERTS_DIR"
sudo chmod 755 "$BASE_CONFIG_DIR"
sudo chmod 755 "$BASE_APP_DIR"
sudo chmod 755 "$BASE_LOG_DIR"
sudo chmod 755 "$BASE_LIB_DIR"

echo "Directory structure for AzureDNSSync2 has been created:"
echo "  Application code:   $BASE_APP_DIR"
echo "  Config:             $BASE_CONFIG_DIR"
echo "  Certificates:       $BASE_CERTS_DIR (root only)"
echo "  Logs:               $BASE_LOG_DIR"
echo "  Runtime data:       $BASE_LIB_DIR"
