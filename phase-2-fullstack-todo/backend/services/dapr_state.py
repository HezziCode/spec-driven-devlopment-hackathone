import httpx
import json
from typing import Dict, Any, List, Optional
from uuid import UUID
from models import Task
from sqlalchemy import create_engine
from sqlmodel import Session

DAPR_URL = "http://localhost:3500"
STATE_STORE = "statestore"

class DaprStateManager:
    \"\"\"
    Dapr State Management for tasks.
    Hybrid approach: Use Dapr for single task CRUD, DB for list/query/index.
    \"\"\"

    def __init__(self):
        self.client = httpx.Client()

    def save_task(self, user_id: str, task: Task) -> bool:
        key = f"user:{user_id}:task:{task.id}"
        state = [{"key": key, "value": task.model_dump()}]
        try:
            response = self.client.post(
                f"{DAPR_URL}/v1.0/state/{STATE_STORE}",
                json=state
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    def get_task(self, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        key = f"user:{user_id}:task:{task_id}"
        try:
            response = self.client.get(
                f"{DAPR_URL}/v1.0/state/{STATE_STORE}/{key}"
            )
            response.raise_for_status()
            data = response.json()
            return data if data else None
        except Exception:
            return None

    def delete_task(self, user_id: str, task_id: str) -> bool:
        key = f"user:{user_id}:task:{task_id}"
        try:
            response = self.client.delete(
                f"{DAPR_URL}/v1.0/state/{STATE_STORE}/{key}"
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    def query_tasks(self, user_id: str, query: str = "*") -> List[Dict[str, Any]]:
        esql = f"SELECT * FROM '{STATE_STORE}' WHERE key LIKE 'user:{user_id}:task:%' AND {query}"
        try:
            response = self.client.post(
                f"{DAPR_URL}/v1.0/state/{STATE_STORE}/query",
                json={"query": esql}
            )
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception:
            return []

dapr_manager = DaprStateManager()