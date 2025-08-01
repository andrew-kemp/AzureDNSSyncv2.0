import os
import io
import secrets
import pyotp
import qrcode
from flask import Flask, redirect, url_for, request, session, flash, render_template, send_file
from pam import pam
from routes_setup import setup_bp, is_configured

USER_MFA = {}

app = Flask(__name__)
# Generate a new secret key each startup to invalidate all sessions after restart
app.secret_key = secrets.token_hex(32)

app.register_blueprint(setup_bp)

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
            # MFA setup or verification
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
    # Generate secret if not present
    if username not in USER_MFA:
        secret = pyotp.random_base32()
        USER_MFA[username] = {"secret": secret, "enabled": False}
    else:
        secret = USER_MFA[username]["secret"]
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=username, issuer_name="AzureDNSSync2")
    if request.method == "POST":
        code = request.form.get("mfa_code")
        if totp.verify(code):
            USER_MFA[username]["enabled"] = True
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
        # Return a blank image if not logged in or no secret
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

@app.before_request
def enforce_user_flow():
    allowed_endpoints = {
        "login", "static", "favicon"
    }
    endpoint = (request.endpoint or "").split('.')[-1]

    # Always allow login/static/favicons
    if endpoint in allowed_endpoints:
        return

    # 1. Not logged in? Only allow login/static/favicons
    if not session.get("logged_in"):
        if endpoint not in allowed_endpoints:
            return redirect(url_for("login"))
        return

    username = session.get("username")
    mfa_enabled = username in USER_MFA and USER_MFA[username].get("enabled")

    # 2. Logged in but MFA not setup? Only allow MFA setup page and QR code
    if session.get("logged_in") and not mfa_enabled:
        if endpoint not in {"mfa_setup", "mfa_qr", "static", "favicon"}:
            return redirect(url_for("mfa_setup"))
        return

    # 3. MFA enabled but not verified? Only allow verify page
    if session.get("logged_in") and mfa_enabled and not session.get("mfa_authenticated"):
        if endpoint not in {"verify_mfa", "static", "favicon"}:
            return redirect(url_for("verify_mfa"))
        return

    # 4. MFA verified but not configured? Only allow setup page
    if session.get("logged_in") and session.get("mfa_authenticated") and not is_configured():
        if endpoint != "setup":
            return redirect(url_for("setup.setup"))
        return

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8443,
        ssl_context=(
            "/etc/azurednssync2/certs/cert.pem",
            "/etc/azurednssync2/certs/key.pem"
        )
    )
