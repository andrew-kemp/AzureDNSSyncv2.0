from apscheduler.schedulers.background import BackgroundScheduler
from .certificates import get_cert_expiry
from .emailer import send_notification
from flask import current_app
from datetime import datetime, timedelta

def schedule_notifications(cert_path, admin_email):
    expiry = get_cert_expiry(cert_path)
    now = datetime.now()
    milestones = [
        (expiry - timedelta(days=180), "6 months"),
        (expiry - timedelta(days=90), "3 months"),
        (expiry - timedelta(days=30), "1 month"),
        (expiry - timedelta(days=7), "1 week"),
        (expiry - timedelta(days=1), "1 day"),
        (now, "created")
    ]
    scheduler = BackgroundScheduler()
    for notify_time, label in milestones:
        if notify_time > now:
            scheduler.add_job(
                send_notification,
                'date',
                run_date=notify_time,
                args=(
                    "[AzureDNSSync] Certificate Expiry Notification",
                    f"Your certificate will expire on {expiry:%Y-%m-%d}. This is your {label} reminder.",
                    admin_email
                )
            )
    scheduler.start()
    return scheduler
