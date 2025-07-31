from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    CERT_PATH = app.config['CERT_PATH']
    ADMIN_EMAIL = app.config['ADMIN_EMAIL']

    # Import and start scheduler
    from app.scheduler import schedule_notifications
    schedule_notifications(CERT_PATH, ADMIN_EMAIL)

    # Run Flask with HTTPS
    app.run(
        host='0.0.0.0',
        port=8443,
        ssl_context=(CERT_PATH, app.config['CERT_KEY_PATH'])
    )
