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

# NEW logging imports
from app.integrations.supabase_logger import SupabaseLogger
from app.schemas.log import LogEntry


# ==================================================================
# NODES with STAGE TAGS + INPUT/OUTPUT tracking
# ==================================================================

def input_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "input"
    state["input"] = {"image": state.get("image")}
    state["output"] = {"received": True}
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

    return state


def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "decision"
    parsed = state["parsed"]

    try:
        if parsed.task_type in ["invoice", "bill", "receipt"]:
            next_action = "TASK"
        else:
            next_action = "NONE"

        state["next_action"] = next_action
        state["output"] = {"next_action": next_action}

    except Exception as e:
        state["error"] = str(e)

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

    return state



def email_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "email_action"
    parsed = state["parsed"]

    try:
        payload = EmailPayload(
            to=parsed.email,
            subject="Notification from LifeAdmin",
            body=parsed.message
        )

        client = SendGridClient()
        result = client.send_email(payload)

        state["email_result"] = result
        state["output"] = {"email_result": result}

    except Exception as e:
        state["error"] = str(e)

    return state


def push_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    state["stage"] = "push_action"
    parsed = state["parsed"]

    try:
        send_push_notification(parsed.title, parsed.message)
        state["output"] = {"push_sent": True}
    except Exception as e:
        state["error"] = str(e)

    return state


def log_node(state: Dict[str, Any]) -> Dict[str, Any]:
    log_entry = LogEntry(
        stage=state.get("stage", "unknown"),
        input_data=state.get("input"),
        output_data=state.get("output"),
        error=state.get("error"),
    )

    SupabaseLogger.log(log_entry)
    return {"logged": True}
