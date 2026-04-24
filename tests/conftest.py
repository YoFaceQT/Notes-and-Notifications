from typing import Any

import pytest
import requests


@pytest.fixture
def tasks_url() -> str:
    return "http://localhost:8000/tasks"


@pytest.fixture
def created_note(tasks_url: str) -> Any:
    resp = requests.post(tasks_url, json={"name": "Default note"})
    assert resp.status_code == 201
    return resp.json()
