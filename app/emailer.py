from flask_mail import Message
from . import mail
from flask import current_app

def send_notification(subject, body, recipient):
    msg = Message(subject, sender=current_app.config['MAIL_USERNAME'], recipients=[recipient])
    msg.body = body
    mail.send(msg)
