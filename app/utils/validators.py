def validate_parsed_task(data: dict):
    required_fields = ["task_type", "due_date", "provider"]

    missing = [f for f in required_fields if f not in data]

    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    return True
