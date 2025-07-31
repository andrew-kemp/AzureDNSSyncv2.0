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

    return app
