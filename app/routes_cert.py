from flask import Blueprint, send_file, flash, redirect, url_for
import os

cert_bp = Blueprint('cert', __name__, template_folder='templates')

CERT_PATH = "/etc/azurednssync2/certs/cert.pem"  # Update this path if needed

@cert_bp.route("/download-cert")
def download_cert():
    if not os.path.exists(CERT_PATH):
        flash("Certificate file not found.", "danger")
        return redirect(url_for("index"))
    return send_file(CERT_PATH, as_attachment=True, download_name="cert.pem")
