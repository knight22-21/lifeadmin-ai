from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import SENDGRID_API_KEY
from app.schemas.email import EmailPayload

class SendGridClient:
    def __init__(self):
        if not SENDGRID_API_KEY:
            raise ValueError("SENDGRID_API_KEY is missing in environment variables.")
        self.client = SendGridAPIClient(SENDGRID_API_KEY)

    def send_email(self, payload: EmailPayload):
        message = Mail(
            from_email=payload.sender,
            to_emails=payload.to,
            subject=payload.subject,
            plain_text_content=payload.body,
        )

        response = self.client.send(message)
        return {
            "status_code": response.status_code,
            "message_id": response.headers.get("X-Message-ID"),
        }
