import os
import subprocess
from flask import Blueprint, render_template, send_file, flash, redirect, url_for

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

SERVICE_NAME = "azurednssync2"
SYSTEMCTL_PATH = "/usr/bin/systemctl"
CERT_PATH = "/var/lib/azurednssync2/certs/cert.pem"
CONFIG_PATH = "/etc/azurednssync2/config.yaml"
SYNC_LOG_PATH = "/var/log/azurednssync2/sync.log"

def get_service_status():
    try:
        output = subprocess.check_output([SYSTEMCTL_PATH, "status", SERVICE_NAME], stderr=subprocess.STDOUT)
        return output.decode()
    except FileNotFoundError:
        return "Error: systemctl not found on this system."
    except subprocess.CalledProcessError as e:
        return f"Service status error: {e.output.decode()}"
    except Exception as e:
        return f"Unexpected error retrieving service status: {str(e)}"

def run_sync():
    # Example: Replace with your actual sync command or logic
    # Could be a Python function or a subprocess call
    try:
        # Simulate sync
        with open(SYNC_LOG_PATH, "a") as f:
            f.write("Sync run at {}\n".format(str(datetime.datetime.now())))
        return True, "Sync executed."
    except Exception as e:
        return False, f"Error running sync: {str(e)}"

def restart_service():
    try:
        output = subprocess.check_output([SYSTEMCTL_PATH, "restart", SERVICE_NAME], stderr=subprocess.STDOUT)
        return True, "Service restarted successfully."
    except FileNotFoundError:
        return False, "Error: systemctl not found on this system."
    except subprocess.CalledProcessError as e:
        return False, f"Restart error: {e.output.decode()}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

@dashboard_bp.route("/", methods=["GET", "POST"])
def dashboard():
    service_status = get_service_status()
    sync_message = None

    if os.path.isfile(SYNC_LOG_PATH):
        with open(SYNC_LOG_PATH, "r") as f:
            last_sync_log = f.read()
    else:
        last_sync_log = "No log found."

    if "run_sync" in (getattr(flash, 'messages', []) or []):
        success, sync_message = run_sync()
        flash(sync_message, "success" if success else "danger")

    if "restart_service" in (getattr(flash, 'messages', []) or []):
        success, restart_message = restart_service()
        flash(restart_message, "success" if success else "danger")

    return render_template(
        "dashboard.html",
        service_status=service_status,
        last_sync_log=last_sync_log
    )

@dashboard_bp.route("/download_cert")
def download_cert():
    if not os.path.isfile(CERT_PATH):
        flash("Certificate file not found.", "danger")
        return redirect(url_for("dashboard.dashboard"))
    return send_file(CERT_PATH, as_attachment=True, download_name="cert.cer")

@dashboard_bp.route("/view_config")
def view_config():
    if not os.path.isfile(CONFIG_PATH):
        flash("Config file not found.", "danger")
        return redirect(url_for("dashboard.dashboard"))
    with open(CONFIG_PATH, "r") as f:
        config_content = f.read()
    return render_template("view_config.html", config_content=config_content)

@dashboard_bp.route("/view_service_status")
def view_service_status():
    status = get_service_status()
    return render_template("view_service_status.html", status=status)

@dashboard_bp.route("/run_sync", methods=["POST"])
def run_sync_route():
    success, message = run_sync()
    flash(message, "success" if success else "danger")
    return redirect(url_for("dashboard.dashboard"))

@dashboard_bp.route("/restart_service", methods=["POST"])
def restart_service_route():
    success, message = restart_service()
    flash(message, "success" if success else "danger")
    return redirect(url_for("dashboard.dashboard"))
