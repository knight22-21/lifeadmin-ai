# app/graph/nodes.py

from typing import Dict, Any
from app.ocr.ocr_space import extract_text_from_image
from app.parsers.llm_parser import parse_document_with_llm
from app.actions.todoist_actions import create_todoist_task
from app.actions.sendgrid_actions import send_email_notification
from app.actions.onesignal_actions import send_push_notification
from app.actions.supabase_logging import log_to_supabase


# ---------------------------
# Input Node
# ---------------------------
def input_node(state: Dict[str, Any]) -> Dict[str, Any]:
    return state  # simply passes input forward


# ---------------------------
# OCR Node
# ---------------------------
def ocr_node(state: Dict[str, Any]) -> Dict[str, Any]:
    image_path = state["image"]
    extracted_text = extract_text_from_image(image_path)
    state["ocr_text"] = extracted_text
    return state


# ---------------------------
# Parse Node
# ---------------------------
def parse_node(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = parse_document_with_llm(state["ocr_text"])
    state["parsed"] = parsed
    return state


# ---------------------------
# Decision Node
# ---------------------------
def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = state["parsed"]

    if parsed.get("action") == "create_task":
        state["next_action"] = "TASK"
    elif parsed.get("action") == "email_reminder":
        state["next_action"] = "EMAIL"
    elif parsed.get("action") == "push_notification":
        state["next_action"] = "PUSH"
    else:
        state["next_action"] = "NONE"

    return state


# ---------------------------
# Action Nodes
# ---------------------------

def task_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = state["parsed"]
    create_todoist_task(parsed)
    return state


def email_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = state["parsed"]
    send_email_notification(parsed["email"], parsed["message"])
    return state


def push_action_node(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = state["parsed"]
    send_push_notification(parsed["title"], parsed["message"])
    return state


# ---------------------------
# Log Node
# ---------------------------

def log_node(state: Dict[str, Any]) -> Dict[str, Any]:
    log_to_supabase(state)
    return state
