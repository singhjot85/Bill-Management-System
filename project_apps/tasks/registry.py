from enum import Enum

def get_task_id(task_name: str, idempotency_key: str):
    return f"{task_name}-{idempotency_key}"

class TaskNames(Enum):

    # PDF_GENERATION = 'bma.invoice.generate_pdf'
    PDF_GENERATION = "generate_pdf"