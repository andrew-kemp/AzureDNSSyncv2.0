from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.user_mfa import load_mfa_data, save_mfa_data
import pyotp  # You must have pyotp installed!

mfa_bp = Blueprint('mfa', __name__, template_folder='templates')

user_mfa = load_mfa_data()

@mfa_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        # Replace with your own authentication logic
        if username == "admin" and password == "your_admin_pw":
            session["username"] = username
            if username not in user_mfa or not user_mfa[username].get("enabled"):
                # Prompt for MFA setup
                secret = pyotp.random_base32()
                user_mfa[username] = {"secret": secret, "enabled": False}
                save_mfa_data(user_mfa)
                return render_template("mfa_setup.html", secret=secret)
            else:
                # Prompt for MFA code
                return redirect(url_for("mfa.mfa_verify"))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

@mfa_bp.route("/mfa-setup", methods=["POST"])
def mfa_setup():
    username = session.get("username")
    token = request.form.get("token", "")
    secret = user_mfa[username]["secret"]
    totp = pyotp.TOTP(secret)
    if totp.verify(token):
        user_mfa[username]["enabled"] = True
        save_mfa_data(user_mfa)
        flash("MFA setup complete!", "success")
        return redirect(url_for("index"))
    else:
        flash("Invalid MFA token, try again.", "danger")
        return render_template("mfa_setup.html", secret=secret)

@mfa_bp.route("/mfa-verify", methods=["GET", "POST"])
def mfa_verify():
    username = session.get("username")
    if request.method == "POST":
        token = request.form.get("token", "")
        secret = user_mfa[username]["secret"]
        totp = pyotp.TOTP(secret)
        if totp.verify(token):
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid MFA token", "danger")
    return render_template("mfa_verify.html")
