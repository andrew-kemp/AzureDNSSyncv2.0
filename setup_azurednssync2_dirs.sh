#!/bin/bash

# Application directories
BASE_APP_DIR="/opt/azurednssync2"
APP_SUBDIRS=(
  "app"
  "app/static"
  "app/templates"
  "app/utils"
  "app/tests"
)
# Optional directories for documentation and scripts
DOCS_DIR="/opt/azurednssync2/docs"
SCRIPTS_DIR="/opt/azurednssync2/scripts"

# Configuration, certificate, log, and runtime data directories
CONFIG_DIR="/etc/azurednssync2"
CERTS_DIR="$CONFIG_DIR/certs"
LOG_DIR="/var/log/azurednssync2"
LIB_DIR="/var/lib/azurednssync2"

# Create application codebase and subdirectories
sudo mkdir -p "$BASE_APP_DIR"
for subdir in "${APP_SUBDIRS[@]}"; do
  sudo mkdir -p "$BASE_APP_DIR/$subdir"
done

# Optional: documentation and scripts
sudo mkdir -p "$DOCS_DIR"
sudo mkdir -p "$SCRIPTS_DIR"

# Create config, certs, logs, runtime data
sudo mkdir -p "$CONFIG_DIR"
sudo mkdir -p "$CERTS_DIR"
sudo mkdir -p "$LOG_DIR"
sudo mkdir -p "$LIB_DIR"

# Set permissions (tighten certs)
sudo chown root:root "$CONFIG_DIR" "$CERTS_DIR"
sudo chmod 700 "$CERTS_DIR"
sudo chmod 755 "$CONFIG_DIR"
sudo chmod 755 "$BASE_APP_DIR"
sudo chmod 755 "$LOG_DIR"
sudo chmod 755 "$LIB_DIR"

echo "AzureDNSSync2 directory structure created:"
echo "  Application code:   $BASE_APP_DIR"
echo "  Static files:       $BASE_APP_DIR/app/static"
echo "  Templates:          $BASE_APP_DIR/app/templates"
echo "  Python utils:       $BASE_APP_DIR/app/utils"
echo "  Unit tests:         $BASE_APP_DIR/app/tests"
echo "  Documentation:      $DOCS_DIR"
echo "  Scripts:            $SCRIPTS_DIR"
echo "  Config:             $CONFIG_DIR"
echo "  Certificates:       $CERTS_DIR (root only)"
echo "  Logs:               $LOG_DIR"
echo "  Runtime data:       $LIB_DIR"
