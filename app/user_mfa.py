import json
import os

MFA_FILE = "/etc/azurednssync2/user_mfa.json"

def load_mfa_data():
    if os.path.exists(MFA_FILE):
        with open(MFA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_mfa_data(data):
    with open(MFA_FILE, "w") as f:
        json.dump(data, f)
    os.chmod(MFA_FILE, 0o600)
