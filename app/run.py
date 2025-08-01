import os
import io
import pyotp
import qrcode
from flask import Flask, redirect, url_for, request, session, flash, render_template, send_file
from pam import pam
from routes_setup import setup_bp, is_configured

# In-memory store for MFA secrets & status (replace with DB for production)
USER_MFA = {}

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change_this_in_production')

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
            # Enforce MFA setup/verification
            if username not in USER_MFA or not USER_MFA[username].get("enabled"):
                session['mfa_authenticated'] = False
                flash("Please set up MFA.", "warning")
                return redirect(url_for("mfa_setup"))
            else:
                session['mfa_authenticated'] = False
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

    # Create secret if not present
    if username not in USER_MFA:
        secret = pyotp.random_base32()
        USER_MFA[username] = {"secret": secret, "enabled": False}
    else:
        secret = USER_MFA[username]["secret"]

    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=username, issuer_name="AzureDNSSync2")

    # Generate QR code image
    qr = qrcode.make(provisioning_uri)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    buf.seek(0)

    if request.method == "POST":
        code = request.form.get("mfa_code")
        if totp.verify(code):
            USER_MFA[username]["enabled"] = True
            session['mfa_authenticated'] = True
            flash("MFA setup complete!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid MFA code.", "danger")

    return render_template("mfa_setup.html", secret=secret)

@app.route('/mfa_qr')
def mfa_qr():
    username = session.get("username")
    if not username or username not in USER_MFA:
        return "", 404
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
            return redirect(url_for("index"))
        else:
            flash("Invalid MFA code.", "danger")
    return render_template("verify_mfa.html")

@app.before_request
def enforce_login_and_setup():
    allowed_endpoints = {"login", "setup", "static", "mfa_setup", "verify_mfa", "mfa_qr", "favicon"}
    endpoint = (request.endpoint or "").split('.')[-1]
    # Allow access to static files and login/setup related pages
    if not session.get("logged_in") and endpoint not in allowed_endpoints:
        return redirect(url_for("login"))
    username = session.get('username')
    if session.get("logged_in"):
        if not is_configured() and not (request.endpoint or "").startswith("setup."):
            return redirect(url_for("setup.setup"))
        if username in USER_MFA and USER_MFA[username].get("enabled") and not session.get("mfa_authenticated") and endpoint not in allowed_endpoints:
            return redirect(url_for("verify_mfa"))

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8443,
        ssl_context=(
            "/etc/azurednssync2/certs/cert.pem",
            "/etc/azurednssync2/certs/key.pem"
        )
    )
