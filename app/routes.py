from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .pam_auth import authenticate
from .mfa import generate_secret, get_qr_url, verify_token

bp = Blueprint('main', __name__)

# Example in-memory store for demonstration (use DB or secure storage in production)
user_mfa_secrets = {}

@bp.route('/', methods=['GET'])
def home():
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate(username, password):
            session['user'] = username
            if username not in user_mfa_secrets:
                return redirect(url_for('main.mfa_setup'))
            else:
                return redirect(url_for('main.mfa_verify'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@bp.route('/mfa/setup', methods=['GET', 'POST'])
def mfa_setup():
    username = session.get('user')
    if not username:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        token = request.form['token']
        secret = session['mfa_secret']
        if verify_token(secret, token):
            user_mfa_secrets[username] = secret
            flash("MFA setup complete. Please log in with your token next time.")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid token. Try again.")
    else:
        secret = generate_secret()
        session['mfa_secret'] = secret
        qr_url = get_qr_url(username, secret)
        return render_template('mfa_setup.html', qr_url=qr_url, secret=secret)
    qr_url = get_qr_url(username, session['mfa_secret'])
    return render_template('mfa_setup.html', qr_url=qr_url, secret=session['mfa_secret'])

@bp.route('/mfa/verify', methods=['GET', 'POST'])
def mfa_verify():
    username = session.get('user')
    if not username or username not in user_mfa_secrets:
        return redirect(url_for('main.login'))
    if request.method == 'POST':
        token = request.form['token']
        if verify_token(user_mfa_secrets[username], token):
            session['mfa_authenticated'] = True
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid MFA token.")
    return render_template('mfa_setup.html', verify_only=True)

@bp.route('/dashboard')
def dashboard():
    if 'user' not in session or not session.get('mfa_authenticated'):
        return redirect(url_for('main.login'))
    return render_template('dashboard.html')

@bp.route('/settings')
def settings():
    if 'user' not in session or not session.get('mfa_authenticated'):
        return redirect(url_for('main.login'))
    return render_template('settings.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
