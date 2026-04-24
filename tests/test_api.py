from typing import Any, Dict

import requests

from src.models.models import NotificationStatus


def test_create_note_with_both_fields(tasks_url: str) -> None:
    payload = {"name": "Learn Python", "description": "more"}
    response = requests.post(tasks_url, json=payload)
    assert response.status_code == 201
    assert response.headers["Content-Type"] == "application/json"
    data = response.json()
    assert data["name"] == "Learn Python"
    assert data["description"] == "more"


def test_create_note_with_only_name_field(tasks_url: str) -> None:
    payload = {"name": "Learn Python"}
    response = requests.post(tasks_url, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Learn Python"


def test_create_note_empty_name(tasks_url: str) -> None:
    response = requests.post(tasks_url, json={"name": ""})
    assert response.status_code == 422


def test_create_note_extra_field(tasks_url: str) -> None:
    response = requests.post(
        tasks_url, json={"name": "Extra", "extra": "extra"}
    )
    assert response.status_code == 201
    assert "extra" not in response.json()


def test_create_note_null_body(tasks_url: str) -> None:
    response = requests.post(tasks_url, json=None)
    assert response.status_code == 422


def test_get_notes(tasks_url: str, created_note: Dict[str, Any]) -> None:
    response = requests.get(tasks_url)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_update_note(
        tasks_url: str,
        created_note: Dict[str, Any]
) -> None:
    note_id = created_note["id"]
    update = {"name": "New", "description": "New desc"}
    response = requests.patch(f"{tasks_url}/{note_id}", json=update)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.json()["name"] == "New"
    assert response.json()["description"] == "New desc"


def test_update_note_no_fields(
        tasks_url: str,
        created_note: Dict[str, Any]) -> None:
    note_id = created_note["id"]
    resp = requests.patch(f"{tasks_url}/{note_id}", json={})
    assert resp.status_code == 200
    assert resp.json()["name"] == created_note["name"]


def test_update_not_existing_note(tasks_url: str) -> None:
    non_existent_id = 9999
    get_resp = requests.get(tasks_url)
    assert get_resp.status_code == 200
    existing_ids = [note["id"] for note in get_resp.json()]
    assert non_existent_id not in existing_ids
    update_resp = requests.patch(
        f"{tasks_url}/{non_existent_id}",
        json={"name": "New"}
    )
    assert update_resp.status_code == 404
    assert "detail" in update_resp.json()


def test_delete_note(
        tasks_url: str,
        created_note: Dict[str, Any]
) -> None:
    note_id = created_note["id"]
    del_resp = requests.delete(f"{tasks_url}/{note_id}")
    assert del_resp.status_code == 204
    get_resp = requests.get(tasks_url)
    ids = [n["id"] for n in get_resp.json()]
    assert note_id not in ids


def test_delete_not_existing_note(tasks_url: str) -> None:
    resp = requests.delete(f"{tasks_url}/9999")
    assert resp.status_code == 404
    assert "detail" in resp.json()


def test_note_status_IN_PROGRESS(tasks_url: str) -> None:
    payload = {"name": "StatusTest", 'remind_after_minutes': 10}
    response = requests.post(tasks_url, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["remind_after_minutes"] == 10
    assert data['status'] == NotificationStatus.IN_PROGRESS.value


def test_note_status_NO_TIMER(tasks_url: str) -> None:
    payload = {"name": "Test_no_timer", "remind_after_minutes": None}
    response = requests.post(tasks_url, json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data['status'] == NotificationStatus.NO_TIMER.value


def test_patch_can_swap_status_to_note(
        tasks_url: str,
        created_note: Dict[str, Any]
) -> None:
    note_id = created_note["id"]
    update = {"name": "patch_note_can_swap_status", "remind_after_minutes": 10}
    resp = requests.patch(f"{tasks_url}/{note_id}", json=update)
    data = resp.json()
    assert data['status'] == NotificationStatus.IN_PROGRESS.value
