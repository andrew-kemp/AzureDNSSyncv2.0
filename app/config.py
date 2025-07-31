import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'changeme-please')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'your@email.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'yourpassword')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    CERT_PATH = os.environ.get('CERT_PATH', '/etc/azurednssync2/certs/cert.pem')
    CERT_KEY_PATH = os.environ.get('CERT_KEY_PATH', '/etc/azurednssync2/certs/key.pem')
