import os
import subprocess
from flask import Blueprint, render_template, redirect, url_for, flash, request

dashboard_bp = Blueprint('dashboard', __name__)

CONFIG_PATH = "/etc/azurednssync/config.yaml"
CERT_PATH = "/etc/azurednssync/certs/cert.pem"
LOG_PATH = "/etc/azurednssync/update.log"
SERVICE_NAME = "azurednssync2"
SYNC_SCRIPT = "/etc/azurednssync/azurednssync.py"
PYTHON_BIN = "/etc/azurednssync/venv/bin/python"

@dashboard_bp.route("/")
def index():
    # Service status
    try:
        status_output = subprocess.check_output(
            ["systemctl", "status", SERVICE_NAME],
            universal_newlines=True
        )
    except Exception as e:
        status_output = f"Error retrieving service status: {e}"

    # Last sync log
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            sync_log = f.read()[-2048:]  # show last 2k chars
    else:
        sync_log = ""

    return render_template(
        "index.html",
        service_status=status_output,
        sync_log=sync_log
    )

@dashboard_bp.route("/view_config")
def view_config():
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = f.read()
        return render_template("view_config.html", config=config)
    else:
        flash("Config file not found.", "danger")
        return redirect(url_for("dashboard.index"))

@dashboard_bp.route("/download_cert")
def download_cert():
    if os.path.isfile(CERT_PATH):
        return send_file(CERT_PATH, as_attachment=True)
    else:
        flash("Certificate file not found.", "danger")
        return redirect(url_for("dashboard.index"))

@dashboard_bp.route("/service_status")
def service_status():
    try:
        status_output = subprocess.check_output(
            ["systemctl", "status", SERVICE_NAME],
            universal_newlines=True
        )
    except Exception as e:
        status_output = f"Error retrieving service status: {e}"
    return render_template(
        "index.html",
        service_status=status_output,
        sync_log=get_sync_log()
    )

def get_sync_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            return f.read()[-2048:]
    return ""

@dashboard_bp.route("/run_sync_now", methods=["POST"])
def run_sync_now():
    try:
        result = subprocess.check_output(
            [PYTHON_BIN, SYNC_SCRIPT],
            universal_newlines=True,
            stderr=subprocess.STDOUT
        )
        flash("Sync script executed. See log below.", "success")
    except subprocess.CalledProcessError as e:
        result = e.output
        flash("Error running sync script.", "danger")
    return render_template(
        "index.html",
        service_status=get_service_status(),
        sync_log=get_sync_log() + "\n\n--- Run Sync Output ---\n" + result
    )

def get_service_status():
    try:
        return subprocess.check_output(
            ["systemctl", "status", SERVICE_NAME],
            universal_newlines=True
        )
    except Exception as e:
        return f"Error retrieving service status: {e}"

@dashboard_bp.route("/restart_service", methods=["POST"])
def restart_service():
    try:
        subprocess.check_output(["systemctl", "restart", SERVICE_NAME])
        flash("Service restarted.", "success")
    except Exception as e:
        flash(f"Error restarting service: {e}", "danger")
    return redirect(url_for("dashboard.index"))
