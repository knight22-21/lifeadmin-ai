import json
from typing import Dict, Any

from app.ocr.ocr_space import extract_text_from_file
from app.parsers.llm_parser import parse_ocr_with_llm
from app.actions.todoist_actions import create_todoist_task
from app.actions.sendgrid_actions import send_email_notification
from app.actions.onesignal_actions import send_push_notification
from app.integrations.todoist_client import TodoistClient
from app.integrations.sendgrid_client import SendGridClient
from app.schemas.email import EmailPayload

# Logging imports
from app.integrations.supabase_logger import SupabaseLogger
from app.schemas.log import LogEntry


# ==============================================================
# Helper: Log state to Supabase
# ==============================================================

def log_stage(state: Dict[str, Any]):
    """Helper to log any pipeline stage to Supabase."""
    entry = LogEntry(
        stage=state.get("stage"),
        input_data=state.get("input"),
        output_data=state.get("output"),
        error=state.get("error"),
    )
    SupabaseLogger.log(entry)



# ==============================================================
# NODES WITH BUILT-IN LOGGING
# ==============================================================

def input_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "input"
    state["input"] = {"image": state.get("image")}
    state["output"] = {"received": True}

    log_stage(state)
    return state



def ocr_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "ocr"
    state["input"] = {"image_path": state["image"]}

    try:
        extracted_text = extract_text_from_file(state["image"])

        try:
            ocr_text = json.loads(extracted_text)
        except Exception:
            ocr_text = extracted_text

        state["ocr_text"] = ocr_text
        state["output"] = {"ocr_text": ocr_text}

    except Exception as e:
        state["error"] = str(e)

    log_stage(state)
    return state



def parse_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "parse"
    state["input"] = {"ocr_text": state.get("ocr_text")}

    try:
        parsed = parse_ocr_with_llm(state["ocr_text"])
        state["parsed"] = parsed
        state["output"] = {"parsed": parsed.dict()}

    except Exception as e:
        state["error"] = str(e)

    log_stage(state)
    return state



def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("\n==============================")
    print("🧪 DEBUG — DECISION NODE INPUT")
    print("Keys:", list(state.keys()))
    print("State:", state)
    print("==============================\n")

    state["stage"] = "decision"

    if "parsed" not in state:
        state["error"] = "❌ ERROR: parsed data missing — parse_node did not produce output."
        state["output"] = None
        log_stage(state)
        return state

    parsed = state["parsed"]

    try:
        next_action = "NONE"

        # Decision based on task_type
        if parsed.task_type in ["invoice", "bill"]:
            next_action = "TASK"
        
        elif parsed.task_type == "subscription":
            next_action = "TASK"

        # Set next_action for subscription_screenshot with reminder_days_before
        if parsed.task_type == "subscription" and parsed.reminder_days_before:
            next_action = "EMAIL"

        if parsed.task_type == "receipt":
            next_action = "NONE"

        state["next_action"] = next_action
        state["output"] = {"next_action": next_action}

    except Exception as e:
        state["error"] = str(e)

    log_stage(state)
    return state




todoist = TodoistClient()

def task_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "todoist_action"
    task = state["parsed"]

    try:
        title = f"{task.task_type.title()} - {task.provider}"
        description = (
            f"Task Type: {task.task_type}\n"
            f"Provider: {task.provider}\n"
            f"Amount: {task.amount}\n"
            f"Due Date: {task.due_date}\n"
            f"Reminder: {task.reminder_days_before} days before"
        )

        todoist_response = todoist.create_task(
            title=title,
            due_date=task.due_date,
            description=description,
            priority=3
        )

        state["todoist_task"] = todoist_response
        state["output"] = {"todoist_task": todoist_response}

    except Exception as e:
        state["error"] = str(e)

    log_stage(state)
    return state



def email_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "email_action"
    parsed = state["parsed"]

    try:
        # Default email if not provided
        if not parsed.email:
            parsed.email = "americaitalybelgium111@gmail.com"

        payload = EmailPayload(
            to=parsed.email,
            subject="Notification from LifeAdmin",
            body="Your notification message."
        )

        client = SendGridClient()
        result = client.send_email(payload)

        state["email_result"] = result
        state["output"] = {"email_result": result}

    except Exception as e:
        state["error"] = str(e)

    log_stage(state)
    return state



def push_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "push_action"
    # Push notifications are disabled, so just log and continue
    state["output"] = {"push_sent": False, "message": "Push notifications disabled"}
    log_stage(state)
    return state




# ==============================================================
# FINAL LOG NODE — unchanged
# ==============================================================

def log_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "log"

    log_entry = LogEntry(
        stage=state.get("stage", "log"),
        input_data=state.get("input"),
        output_data=state.get("output"),
        error=state.get("error"),
    )

    SupabaseLogger.log(log_entry)
    state["logged"] = True

    return state
