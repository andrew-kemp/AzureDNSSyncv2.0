import pyotp

def generate_secret():
    return pyotp.random_base32()

def get_qr_url(user, secret):
    return pyotp.totp.TOTP(secret).provisioning_uri(name=user, issuer_name="AzureDNSSync2")

def verify_token(secret, token):
    totp = pyotp.TOTP(secret)
    return totp.verify(token)
