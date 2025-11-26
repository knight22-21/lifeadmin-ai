

# LifeAdmin AI

LifeAdmin AI is a web application built using **FastAPI** and **Frontend (HTML, CSS, JS)**. It allows users to upload documents (bills, receipts, etc.), from which the AI system extracts relevant tasks, reminders, subscriptions, and more. These extracted tasks can then be further processed to send notifications, create Todoist tasks, or generate emails.

## Features

* **OCR Processing**: Uses OCR to extract text from uploaded documents (bills, receipts).
* **Task Parsing**: The extracted text is parsed into actionable tasks using AI models.
* **Integration with Todoist**: Automatically creates tasks in Todoist based on parsed data.
* **Email Notifications**: Sends email notifications using SendGrid if certain conditions are met.
* **Push Notifications**: Support for push notifications (currently disabled).
* **Logging**: Logs the entire processing workflow into Supabase.

---

## Project Structure

```
lifeadmin-ai
├── app
│   ├── actions
│   │   ├── onesignal_actions.py
│   │   ├── sendgrid_actions.py
│   │   ├── supabase_logging.py
│   │   └── todoist_actions.py
│   │
│   ├── core
│   │   └── config.py
│   │
│   ├── frontend
│   │   ├── index.html
│   │   ├── script.js
│   │   └── styles.css
│   │
│   ├── graph
│   │   ├── __init__.py
│   │   ├── nodes.py
│   │   └── workflow.py
│   │
│   ├── integrations
│   │   ├── sendgrid_client.py
│   │   ├── supabase_client.py
│   │   ├── supabase_logger.py
│   │   └── todoist_client.py
│   │
│   ├── ocr
│   │   └── ocr_space.py
│   │
│   ├── parsers
│   │   ├── groq_generate.py
│   │   └── llm_parser.py
│   │
│   ├── schemas
│   │   ├── email.py
│   │   ├── log.py
│   │   ├── ocr.py
│   │   └── task.py
│   │
│   ├── utils
│   │   ├── retry.py
│   │   └── validators.py
│   │
│   └── main.py
│
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/lifeadmin-ai.git
   cd lifeadmin-ai
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables. You need API keys for OCR, Todoist, SendGrid, and Supabase. You can create a `.env` file for local development or configure them in your hosting platform.

---

## Usage

1. **Run the backend**:

   You can start the FastAPI backend with the following command:

   ```bash
   uvicorn app.main:app --reload
   ```

   By default, the backend runs on `http://127.0.0.1:8000`. You can access the UI at `http://127.0.0.1:8000` in your browser.

2. **Access the frontend**:

   The frontend is served directly from the FastAPI app. It provides a simple file upload interface. You can drag and drop files to the upload area or select them manually using the file picker.

---

## Endpoints

* **GET /**: Serves the frontend UI.
* **POST /ocr-test**: Test OCR functionality by uploading an image (using OCR.Space).
* **POST /parse-test**: Test the LLM-based task parser by sending OCR text.
* **POST /process**: Upload a file, process it, and trigger the workflow that:

  * Extracts text using OCR.
  * Parses the text to identify tasks.
  * Creates Todoist tasks, sends emails, or logs results based on the parsed task.

---

## Workflow

The core logic is implemented in the **workflow** (`app/graph/workflow.py`). The workflow is built using a series of nodes, each performing specific tasks:

1. **Input Node**: Receives the uploaded file.
2. **OCR Node**: Extracts text from the uploaded document.
3. **Parse Node**: Parses the OCR text into structured tasks.
4. **Decision Node**: Decides what action should be taken (e.g., create Todoist task, send email).
5. **Action Nodes**: Performs actions like creating tasks in Todoist or sending emails.
6. **Log Node**: Logs the entire process to Supabase.

---

## Frontend

The frontend is a simple HTML5-based UI, providing a file upload interface and displaying the results of the processing. It has:

* **Drag-and-drop file upload**: Users can drag their files into the upload area.
* **Loading indicator**: Shows a loading spinner while the file is being processed.
* **Result summary**: Displays a summary of the actions performed (e.g., task creation, email notification).

---

## Testing

### Retry Logic

Certain steps in the workflow, like API calls, can fail temporarily. The `retry` utility in `app/utils/retry.py` can be used to automatically retry failed operations.

Example usage in code:

```python
@retry(max_attempts=3, delay=2, backoff=2)
def some_api_call():
    # logic to make API call
```

### Task Validation

The `validators.py` file provides a method for validating parsed tasks to ensure required fields (e.g., `task_type`, `due_date`, `provider`) are present.

Example usage:

```python
validate_parsed_task(parsed_task)
```

---


## Deployment

This application is deployed on **Render**. To deploy it on Render, follow these steps:

1. Connect your GitHub repository to Render.
2. Choose the **FastAPI** deployment type.
3. Set up your environment variables, including API keys for **SendGrid**, **Todoist**, **Supabase**, and **OCR.Space**.
4. Deploy the application.

Once deployed, your application will be accessible through the link provided by Render.

### Deployed app:

[**Visit your deployed app here**](https://lifeadmin-ai.onrender.com)

---
 

## Dependencies

* **FastAPI**: Framework for building APIs.
* **Uvicorn**: ASGI server to run the FastAPI app.
* **requests**: Library for making HTTP requests.
* **langgraph**: Used for creating the state machine for workflow.
* **sendgrid**: To send emails via SendGrid.
* **todoist-python**: To integrate with Todoist for task management.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

