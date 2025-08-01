import os
import io
import secrets
import pyotp
import qrcode
from flask import Flask, redirect, url_for, request, session, flash, render_template, send_file
from pam import pam
from routes_setup import setup_bp, is_configured
from user_mfa import load_mfa_data, save_mfa_data
from routes_dashboard import dashboard_bp  # Import your dashboard blueprint

USER_MFA = load_mfa_data()  # Persistent MFA data

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = secrets.token_hex(32)

app.register_blueprint(setup_bp)
app.register_blueprint(dashboard_bp)

@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if pam().authenticate(username, password):
            session['username'] = username
            session['logged_in'] = True
            session['mfa_authenticated'] = False
            if username not in USER_MFA or not USER_MFA[username].get("enabled"):
                flash("Please set up MFA.", "warning")
                return redirect(url_for("mfa_setup"))
            else:
                return redirect(url_for("verify_mfa"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("login"))

@app.route("/mfa_setup", methods=["GET", "POST"])
def mfa_setup():
    username = session.get("username")
    if not username:
        return redirect(url_for("login"))
    if username not in USER_MFA:
        secret = pyotp.random_base32()
        USER_MFA[username] = {"secret": secret, "enabled": False}
        save_mfa_data(USER_MFA)
    else:
        secret = USER_MFA[username]["secret"]
    totp = pyotp.TOTP(secret)
    if request.method == "POST":
        code = request.form.get("mfa_code")
        if totp.verify(code):
            USER_MFA[username]["enabled"] = True
            save_mfa_data(USER_MFA)
            session['mfa_authenticated'] = True
            flash("MFA setup complete!", "success")
            return redirect(url_for("setup.setup") if not is_configured() else url_for("index"))
        else:
            flash("Invalid MFA code.", "danger")
    return render_template("mfa_setup.html", secret=secret)

@app.route('/mfa_qr')
def mfa_qr():
    username = session.get("username")
    if not username or username not in USER_MFA:
        buf = io.BytesIO()
        qr = qrcode.make("Invalid")
        qr.save(buf, format='PNG')
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    totp = pyotp.TOTP(USER_MFA[username]["secret"])
    provisioning_uri = totp.provisioning_uri(name=username, issuer_name="AzureDNSSync2")
    qr = qrcode.make(provisioning_uri)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route("/verify_mfa", methods=["GET", "POST"])
def verify_mfa():
    username = session.get("username")
    if not username or username not in USER_MFA or not USER_MFA[username]['enabled']:
        return redirect(url_for("login"))
    totp = pyotp.TOTP(USER_MFA[username]["secret"])
    if request.method == "POST":
        code = request.form.get("mfa_code")
        if totp.verify(code):
            session['mfa_authenticated'] = True
            flash("MFA authenticated!", "success")
            return redirect(url_for("setup.setup") if not is_configured() else url_for("index"))
        else:
            flash("Invalid MFA code.", "danger")
    return render_template("verify_mfa.html")

@app.route('/download_cert')
def download_cert():
    cert_path = '/var/lib/azurednssync2/certs/cert.pem'
    if not os.path.isfile(cert_path):
        flash("Certificate file not found.", "danger")
        return redirect(url_for("setup.setup"))
    # Download as .cer for better compatibility
    return send_file(cert_path, as_attachment=True, download_name='cert.cer')

@app.before_request
def enforce_user_flow():
    allowed_endpoints = {
        "login", "static", "favicon"
    }
    endpoint = (request.endpoint or "").split('.')[-1]
    if endpoint in allowed_endpoints:
        return
    if not session.get("logged_in"):
        if endpoint not in allowed_endpoints:
            return redirect(url_for("login"))
        return
    username = session.get("username")
    mfa_enabled = username in USER_MFA and USER_MFA[username].get("enabled")
    if session.get("logged_in") and not mfa_enabled:
        if endpoint not in {"mfa_setup", "mfa_qr", "static", "favicon"}:
            return redirect(url_for("mfa_setup"))
        return
    if session.get("logged_in") and mfa_enabled and not session.get("mfa_authenticated"):
        if endpoint not in {"verify_mfa", "static", "favicon"}:
            return redirect(url_for("verify_mfa"))
        return
    if session.get("logged_in") and session.get("mfa_authenticated") and not is_configured():
        if endpoint not in {"setup", "static", "favicon", "download_cert"}:
            return redirect(url_for("setup.setup"))
        return

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8443,
        ssl_context=(
            "/var/lib/azurednssync2/certs/cert.pem",
            "/var/lib/azurednssync2/certs/cert.key"
        )
    )
