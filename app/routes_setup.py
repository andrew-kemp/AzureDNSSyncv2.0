from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import yaml

setup_bp = Blueprint('setup', __name__, template_folder='templates')

CONFIG_PATH = "/etc/azurednssync2/config.yaml"
SMTP_KEY_PATH = "/etc/azurednssync2/smtp_auth.key"

def is_configured():
    return os.path.exists(CONFIG_PATH)

@setup_bp.route("/setup", methods=["GET", "POST"])
def setup():
    if is_configured():
        return redirect(url_for("main.index"))
    if request.method == "POST":
        # Get all values from the form
        tenant_id = request.form.get("tenant_id", "").strip()
        client_id = request.form.get("client_id", "").strip()
        client_secret = request.form.get("client_secret", "").strip()  # Store in YAML or ignore as per your security model
        subscription_id = request.form.get("subscription_id", "").strip()
        certificate_path = request.form.get("certificate_path", "").strip()
        resource_group = request.form.get("resource_group", "").strip()
        zone_name = request.form.get("zone_name", "").strip()
        record_set_name = request.form.get("record_set_name", "").strip()
        ttl = request.form.get("ttl", "").strip()
        email_from = request.form.get("email_from", "").strip()
        email_to = request.form.get("email_to", "").strip()
        smtp_server = request.form.get("smtp_server", "").strip()
        smtp_port = request.form.get("smtp_port", "").strip()
        cert_password = request.form.get("certificate_password", "").strip()
        smtp_username = request.form.get("smtp_username", "").strip()
        smtp_password = request.form.get("smtp_password", "").strip()

        # Validate required fields (add more as needed)
        required_fields = [
            tenant_id, client_id, subscription_id, certificate_path,
            resource_group, zone_name, record_set_name, ttl,
            email_from, email_to, smtp_server, smtp_port,
            cert_password, smtp_username, smtp_password
        ]
        if not all(required_fields):
            flash("All fields are required.", "danger")
            return render_template("setup.html")

        # Prepare config.yaml data
        config = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "subscription_id": subscription_id,
            "certificate_path": certificate_path,
            "resource_group": resource_group,
            "zone_name": zone_name,
            "record_set_name": record_set_name,
            "ttl": ttl,
            "email_from": email_from,
            "email_to": email_to,
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "certificate_password": cert_password,
        }

        # Save config.yaml
        try:
            with open(CONFIG_PATH, "w") as f:
                yaml.safe_dump(config, f, default_flow_style=False)
            os.chmod(CONFIG_PATH, 0o600)
        except Exception as e:
            flash(f"Failed to write config.yaml: {e}", "danger")
            return render_template("setup.html")

        # Save smtp_auth.key
        try:
            with open(SMTP_KEY_PATH, "w") as f:
                f.write(f"username:{smtp_username}\npassword:{smtp_password}\n")
            os.chmod(SMTP_KEY_PATH, 0o600)
        except Exception as e:
            flash(f"Failed to write SMTP credentials: {e}", "danger")
            return render_template("setup.html")

        flash("Configuration saved! Please log in.", "success")
        return redirect(url_for("main.index"))
    return render_template("setup.html")
