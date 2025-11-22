# app/actions/sendgrid_actions.py

def send_email_notification(email: str, message: str):
    print(f"[SendGrid] Email sent → {email}: {message}")
