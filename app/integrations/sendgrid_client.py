from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings
from app.schemas.email import EmailPayload

from app.utils.retry import retry


class SendGridClient:
    def __init__(self):
        if not settings.SENDGRID_API_KEY:
            raise ValueError("SENDGRID_API_KEY is missing in environment variables.")
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)

    @retry(max_attempts=3, delay=2, backoff=2)
    def send_email(self, payload: EmailPayload):
        """
        Sends an email with retry + error handling.
        """

        try:
            message = Mail(
                from_email=payload.sender,
                to_emails=payload.to,
                subject=payload.subject,
                plain_text_content=payload.body,
            )

            response = self.client.send(message)

            # According to SendGrid docs, success = 200 or 202
            if response.status_code not in [200, 202]:
                raise RuntimeError(f"SendGrid Error: {response.body}")

            return {
                "status_code": response.status_code,
                "message_id": response.headers.get("X-Message-ID"),
            }

        except Exception as e:
            raise RuntimeError(f"Email failed: {e}")
