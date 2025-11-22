# app/integrations/onesignal_client.py

import requests
import os
import json

class OneSignalClient:
    def __init__(self):
        self.app_id = os.getenv("ONESIGNAL_APP_ID")
        self.api_key = os.getenv("ONESIGNAL_API_KEY")

        if not self.app_id or not self.api_key:
            raise ValueError("ONESIGNAL_APP_ID or ONESIGNAL_API_KEY missing in .env")

        self.url = "https://api.onesignal.com/notifications"
        self.headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Basic {self.api_key}"
        }

    def send_push(self, heading: str, message: str, external_id: str = "user_1"):
        """
        Sends push notification to a specific user.
        external_id represents the OneSignal external_user_id.
        """

        payload = {
            "app_id": self.app_id,
            "include_external_user_ids": [external_id],
            "headings": {"en": heading},
            "contents": {"en": message}
        }

        response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))

        # For debugging
        if response.status_code not in [200, 201]:
            print("OneSignal Error:", response.text)

        return response.json()
