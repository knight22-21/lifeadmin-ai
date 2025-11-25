import os
import requests
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_email_with_groq(context: dict) -> dict:
    """
    Generate an email subject and body using Groq's free LLM API.
    context: a dictionary that contains parsed OCR, previous states, etc.
    """
    
    # Define the prompt for Groq to generate subject and body without markdown
    prompt = f"""
    You are LifeAdmin AI. Please generate the following in JSON format (no markdown, asterisks, or hashes):
    - 'subject' (A clear, concise subject line for the email and should contain at least 'LifeAdmin AI')
    - 'body' (The body of the email, written in a friendly and professional tone)

    The email should always begin with the salutation: "Dear User,"  
    The email body should also include information about any actions taken, such as creating a Todoist task or setting a reminder.

    Here is the extracted workflow context:
    {json.dumps(context, indent=2)}

    Example output should look like this:
    {{
        "subject": "Upcoming Netflix Subscription Renewal Details by LifeAdmin AI",
        "body": "Dear User,\\n\\nWe have analyzed your Netflix subscription and extracted the details. Here's a summary of what we found...\\n\\nPlease let us know if you need further assistance.\\n\\nBest regards,\\nLifeAdmin AI"
    }}

    Please ensure the 'body' is free of any markdown or special characters such as asterisks (*) or hashes (#). Also, ensure the language is professional, clear, and helpful.
    """

    # Send the prompt to Groq's API
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            json={
                "model": "llama-3.1-8b-instant",  # Using the free LLM model
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )

        # Check if the response status code is successful (200)
        if response.status_code != 200:
            return {"subject": "Error", "body": "Failed to generate email content. Please try again later."}
        
        # Parse the response JSON
        data = response.json()
        
        # Check if the response contains expected keys
        if "choices" not in data or len(data["choices"]) == 0:
            return {"subject": "Error", "body": "Unexpected response structure from Groq API."}
        
        result = data["choices"][0]["message"]["content"]

        # Attempt to parse the result as JSON
        try:
            result_json = json.loads(result)
            return result_json  # Will return a dictionary with 'subject' and 'body'
        except json.JSONDecodeError:
            return {"subject": "Error", "body": "Failed to decode response from Groq."}

    except requests.exceptions.RequestException:
        return {"subject": "Error", "body": "Failed to connect to Groq API. Please try again later."}
    except Exception:
        return {"subject": "Error", "body": "An unexpected error occurred while generating email content."}
