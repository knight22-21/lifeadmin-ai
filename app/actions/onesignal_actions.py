# app/actions/onesignal_actions.py

def send_push_notification(title: str, message: str):
    print(f"[OneSignal] Push sent → {title}: {message}")
