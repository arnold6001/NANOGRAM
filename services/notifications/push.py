# services/notifications/push.py
import firebase_admin
from firebase_admin import messaging
from apple_push import APNsClient   # hypothetical wrapper

firebase_admin.initialize_app(...)

def send_fcm(token, title, body, data=None):
    message = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data=data or {},
    )
    messaging.send(message)

def send_apns(device_token, alert):
    # similar wrapper...
    pass