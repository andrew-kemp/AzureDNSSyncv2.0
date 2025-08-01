from flask import Blueprint, render_template, request, redirect, flash, url_for
import yaml
import os

config_bp = Blueprint('config', __name__)

CONFIG_PATH = "/etc/azurednssync2/config.yaml"

@config_bp.route("/view-config")
def view_config():
    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)
    return render_template("view_config.html", config=config)

@config_bp.route("/update-config", methods=["GET", "POST"])
def update_config():
    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)
    if request.method == "POST":
        for key in config.keys():
            config[key] = request.form.get(key, config[key])
        try:
            with open(CONFIG_PATH, "w") as f:
                yaml.safe_dump(config, f)
            flash("Config updated.", "success")
            return redirect(url_for("config.view_config"))
        except Exception as e:
            flash(f"Failed to update config: {e}", "danger")
    return render_template("update_config.html", config=config)
