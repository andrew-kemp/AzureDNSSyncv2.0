from flask import Flask
from flask_mail import Mail
from .config import Config

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mail.init_app(app)

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    # Register setup blueprint
    from .routes_setup import setup_bp
    app.register_blueprint(setup_bp)

    # Register certificate download blueprint
    from .routes_cert import cert_bp
    app.register_blueprint(cert_bp)

    # Register MFA blueprint (if used)
    # from .routes_mfa import mfa_bp
    # app.register_blueprint(mfa_bp)

    return app
