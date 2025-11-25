# app/integrations/todoist_client.py

import requests
import os
from app.utils.retry import retry

TODOIST_API_BASE = "https://api.todoist.com/rest/v2/tasks"


class TodoistClient:
    def __init__(self):
        self.api_key = os.getenv("TODOIST_API_KEY")
        if not self.api_key:
            raise ValueError("TODOIST_API_KEY not found in environment variables.")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @retry(max_attempts=3, delay=2, backoff=2)
    def create_task(self, title: str, due_date: str, description: str = None, priority: int = 1):
        """
        Create a task in Todoist with retry and error handling.
        priority: 1=low, 2=medium, 3=high, 4=urgent
        """
        data = {
            "content": title,
            "due_date": due_date,
            "priority": priority,
        }

        if description:
            data["description"] = description

        try:
            response = requests.post(
                TODOIST_API_BASE, 
                json=data, 
                headers=self.headers,
                timeout=15
            )

            if response.status_code not in [200, 201]:
                raise RuntimeError(f"Todoist API Error: {response.text}")

            return response.json()

        except Exception as e:
            raise RuntimeError(f"Todoist task creation failed: {e}")
