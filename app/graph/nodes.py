import json
from typing import Dict, Any

from app.ocr.ocr_space import extract_text_from_file
from app.parsers.llm_parser import parse_ocr_with_llm
from app.actions.todoist_actions import create_todoist_task
from app.actions.sendgrid_actions import send_email_notification
from app.actions.onesignal_actions import send_push_notification
from app.actions.supabase_logging import log_to_supabase
from app.integrations.todoist_client import TodoistClient


# ==================================================================
# NODES (NO LOGGING)
# ==================================================================

def input_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return state


def ocr_node(state: Dict[str, Any]) -> Dict[str, Any]:
    image_path = state["image"]
    extracted_text = extract_text_from_file(image_path)

    # Convert OCR JSON string → dict if needed
    try:
        state["ocr_text"] = json.loads(extracted_text)
    except Exception:
        state["ocr_text"] = extracted_text

    return state


def parse_node(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = parse_ocr_with_llm(state["ocr_text"])
    state["parsed"] = parsed
    return state


def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = state["parsed"]

    if parsed.task_type in ["invoice", "bill", "receipt"]:
        state["next_action"] = "TASK"
    else:
        state["next_action"] = "NONE"

    return state


# Todoist client
todoist = TodoistClient()

def task_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    task = state["parsed"]

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
    return state


def email_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = state["parsed"]
    send_email_notification(parsed.email, parsed.message)
    return state


def push_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = state["parsed"]
    send_push_notification(parsed.title, parsed.message)
    return state


def log_node(state: Dict[str, Any]) -> Dict[str, Any]:
    log_to_supabase(state)
    return state
