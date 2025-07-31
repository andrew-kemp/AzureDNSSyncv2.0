import os
from flask import Flask, redirect, url_for, request
from app.routes_setup import setup_bp, is_configured

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change_this_in_production")

# Register setup blueprint
app.register_blueprint(setup_bp)

# Example of main blueprint (replace with your real main app logic)
from flask import Blueprint, render_template
main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

app.register_blueprint(main_bp)

@app.before_request
def enforce_setup():
    if not is_configured() and not (request.endpoint or "").startswith("setup."):
        return redirect(url_for("setup.setup"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, ssl_context=("/etc/azurednssync2/certs/cert.pem", "/etc/azurednssync2/certs/key.pem"))
