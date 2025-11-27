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
from app.parsers.groq_generate import generate_email_with_groq

from app.integrations.supabase_logger import SupabaseLogger
from app.schemas.log import LogEntry


def log_stage(state: Dict[str, Any]):
    """Log any pipeline stage to Supabase."""
    entry = LogEntry(
        stage=state.get("stage"),
        input_data=state.get("input"),
        output_data=state.get("output"),
        error=state.get("error"),
    )
    SupabaseLogger.log(entry)


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
    state["stage"] = "decision"

    if "parsed" not in state:
        state["error"] = "parsed data missing"
        state["output"] = None
        log_stage(state)
        return state

    parsed = state["parsed"]

    try:
        next_action = "NONE"

        if parsed.task_type in ["invoice", "bill"]:
            next_action = "TASK"

        elif parsed.task_type == "subscription":
            next_action = "TASK"

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
        if not parsed.email:
            parsed.email = "americaitalybelgium111@gmail.com"

        context = {
            "ocr_text": state.get("ocr_text"),
            "parsed": parsed.dict(),
            "previous_state": {k: v for k, v in state.items() if k not in ["ocr_text", "parsed"]}
        }

        email_content = generate_email_with_groq(context)

        subject = email_content.get("subject", "No Subject")
        body = email_content.get("body", "There was an issue generating the body.")

        payload = EmailPayload(
            to=parsed.email,
            subject=subject,
            body=body
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
    state["output"] = {"push_sent": False, "message": "Push notifications disabled"}
    log_stage(state)
    return state


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
