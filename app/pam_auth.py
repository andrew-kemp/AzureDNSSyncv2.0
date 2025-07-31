import pam

def authenticate(username, password):
    p = pam.pam()
    return p.authenticate(username, password)
