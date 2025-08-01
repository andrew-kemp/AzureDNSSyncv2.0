import json
MFA_PATH = "/opt/azurednssync2/user_mfa.json"

def load_mfa_data():
    try:
        with open(MFA_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading MFA data: {e}")
        return {}

def save_mfa_data(data):
    with open(MFA_PATH, "w") as f:
        json.dump(data, f)
