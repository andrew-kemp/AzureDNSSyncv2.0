from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import yaml

setup_bp = Blueprint('setup', __name__, template_folder='templates')

CONFIG_PATH = "/etc/azurednssync2/config.yaml"

def is_configured():
    return os.path.exists(CONFIG_PATH)

@setup_bp.route("/setup", methods=["GET", "POST"])
def setup():
    if is_configured():
        return redirect(url_for("main.index"))
    if request.method == "POST":
        tenant_id = request.form.get("tenant_id", "").strip()
        client_id = request.form.get("client_id", "").strip()
        client_secret = request.form.get("client_secret", "").strip()
        subscription_id = request.form.get("subscription_id", "").strip()

        if not all([tenant_id, client_id, client_secret, subscription_id]):
            flash("All fields are required.", "danger")
            return render_template("setup.html")

        config = {
            "tenant_id": tenant_id,
            "client_id": client_id,
            "client_secret": client_secret,
            "subscription_id": subscription_id,
        }
        with open(CONFIG_PATH, "w") as f:
            yaml.safe_dump(config, f)
        os.chmod(CONFIG_PATH, 0o600)
        flash("Configuration saved! Please log in.", "success")
        return redirect(url_for("main.index"))
    return render_template("setup.html")
