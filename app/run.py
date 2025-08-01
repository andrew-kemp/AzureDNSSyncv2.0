import os
from flask import Flask, redirect, url_for, request, session, flash, render_template
from pam import pam
from routes_setup import setup_bp, is_configured

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'change_this_in_production')

# Register setup blueprint
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
        # Authenticate using Ubuntu system accounts via PAM
        if pam().authenticate(username, password):
            session['logged_in'] = True
            session['username'] = username
            flash("Successfully logged in.", "success")
            # Redirect to setup if not configured
            if not is_configured():
                return redirect(url_for("setup.setup"))
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("login"))

@app.before_request
def enforce_login_and_setup():
    allowed_endpoints = {"login", "static"}
    endpoint = (request.endpoint or "").split('.')[-1]
    if not session.get("logged_in") and endpoint not in allowed_endpoints:
        return redirect(url_for("login"))
    if session.get("logged_in") and not is_configured() and not (request.endpoint or "").startswith("setup."):
        return redirect(url_for("setup.setup"))

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8443,
        ssl_context=(
            "/etc/azurednssync2/certs/cert.pem",
            "/etc/azurednssync2/certs/key.pem"
        )
    )
