# app/graph/workflow.py

from langgraph.graph import StateGraph, END

from app.graph.nodes import (
    input_node,
    ocr_node,
    parse_node,
    decision_node,
    task_action_node,
    email_action_node,
    push_action_node,
    log_node
)


def build_graph():
    graph = StateGraph(dict)

    # Define nodes
    graph.add_node("input", input_node)
    graph.add_node("ocr", ocr_node)
    graph.add_node("parse", parse_node)
    graph.add_node("decision", decision_node)
    graph.add_node("task", task_action_node)
    graph.add_node("email", email_action_node)
    graph.add_node("push", push_action_node)
    graph.add_node("log", log_node)

    # Flow
    graph.set_entry_point("input")

    graph.add_edge("input", "ocr")
    graph.add_edge("ocr", "parse")
    graph.add_edge("parse", "decision")

    graph.add_conditional_edges(
        "decision",
        lambda state: state["next_action"],
        {
            "TASK": "task",
            "EMAIL": "email",
            "PUSH": "push",
            "NONE": "log"
        }
    )

    # All action paths lead to logging
    graph.add_edge("task", "log")
    graph.add_edge("email", "log")
    graph.add_edge("push", "log")

    graph.add_edge("log", END)

    return graph.compile()
