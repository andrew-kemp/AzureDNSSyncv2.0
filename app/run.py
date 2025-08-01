import os
from flask import Flask, redirect, url_for, request, session
from app.routes_setup import setup_bp, is_configured

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change_this_in_production")

# Register setup blueprint
app.register_blueprint(setup_bp)

# Main dashboard blueprint
from flask import Blueprint, render_template, flash

main_bp = Blueprint('main', __name__, template_folder='templates')

@main_bp.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

app.register_blueprint(main_bp)

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Replace this with your actual authentication logic
        if username == "admin" and password == "password":  # Replace with PAM or real check
            session["logged_in"] = True
            session["username"] = username
            flash("Successfully logged in.", "success")
            return redirect(url_for("main.index"))
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
    allowed = {"login", "static"}
    endpoint = (request.endpoint or "")
    if not session.get("logged_in") and endpoint not in allowed:
        return redirect(url_for("login"))
    # Setup enforcement after login
    if session.get("logged_in") and not is_configured() and not endpoint.startswith("setup."):
        return redirect(url_for("setup.setup"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8443, ssl_context=("/etc/azurednssync2/certs/cert.pem", "/etc/azurednssync2/certs/key.pem"))
