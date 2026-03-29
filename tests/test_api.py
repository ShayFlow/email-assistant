"""
Tests for the Email Reply Assistant API.

All tests mock call_claude so no real API calls are made.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from main import app

MOCK_REPLY = {
    "intent": "The sender is requesting a meeting to discuss Q1 results.",
    "missing_info": "None",
    "subject": "Re: Q1 Results Meeting",
    "draft_reply": "Hi,\n\nThanks for reaching out. I'd be happy to connect.\n\nBest,\nShots",
    "style_note": "The draft is direct and concise, matching the style guide.",
}

CALL_CLAUDE_PATH = "main.call_claude"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# POST /generate-reply — happy path
# ---------------------------------------------------------------------------

def test_generate_reply_returns_all_five_fields(client):
    with patch(CALL_CLAUDE_PATH, return_value=MOCK_REPLY):
        response = client.post(
            "/generate-reply",
            json={"incoming_email": "Can we meet to discuss Q1?"},
        )
    assert response.status_code == 200
    data = response.json()
    for field in ("intent", "missing_info", "subject", "draft_reply", "style_note"):
        assert field in data, f"Missing field: {field}"


def test_generate_reply_with_reply_notes_and_regeneration_context(client):
    with patch(CALL_CLAUDE_PATH, return_value=MOCK_REPLY):
        response = client.post(
            "/generate-reply",
            json={
                "incoming_email": "Can we meet to discuss Q1?",
                "reply_notes": "Keep it brief, I'm busy this week.",
                "regeneration_context": "Previous draft was too formal.",
            },
        )
    assert response.status_code == 200
    data = response.json()
    for field in ("intent", "missing_info", "subject", "draft_reply", "style_note"):
        assert field in data


# ---------------------------------------------------------------------------
# POST /generate-reply — validation errors
# ---------------------------------------------------------------------------

def test_generate_reply_empty_incoming_email_returns_422(client):
    response = client.post(
        "/generate-reply",
        json={"incoming_email": ""},
    )
    assert response.status_code == 422


def test_generate_reply_whitespace_only_incoming_email_returns_422(client):
    response = client.post(
        "/generate-reply",
        json={"incoming_email": "   "},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /generate-reply — Claude API failure
# ---------------------------------------------------------------------------

def test_generate_reply_claude_failure_returns_502(client):
    with patch(CALL_CLAUDE_PATH, side_effect=ValueError("Claude returned non-JSON output.")):
        response = client.post(
            "/generate-reply",
            json={"incoming_email": "Can we meet to discuss Q1?"},
        )
    assert response.status_code == 502


# ---------------------------------------------------------------------------
# POST /regenerate-reply — happy path
# ---------------------------------------------------------------------------

def test_regenerate_reply_with_all_fields(client):
    with patch(CALL_CLAUDE_PATH, return_value=MOCK_REPLY):
        response = client.post(
            "/regenerate-reply",
            json={
                "incoming_email": "Can we meet to discuss Q1?",
                "previous_reply": "Sure, let me know a time.",
                "regeneration_feedback": "Too short, add more warmth.",
            },
        )
    assert response.status_code == 200
    data = response.json()
    for field in ("intent", "missing_info", "subject", "draft_reply", "style_note"):
        assert field in data


def test_regenerate_reply_with_only_incoming_email(client):
    with patch(CALL_CLAUDE_PATH, return_value=MOCK_REPLY):
        response = client.post(
            "/regenerate-reply",
            json={"incoming_email": "Can we meet to discuss Q1?"},
        )
    assert response.status_code == 200
    data = response.json()
    for field in ("intent", "missing_info", "subject", "draft_reply", "style_note"):
        assert field in data


# ---------------------------------------------------------------------------
# POST /regenerate-reply — Claude API failure
# ---------------------------------------------------------------------------

def test_regenerate_reply_claude_failure_returns_502(client):
    with patch(CALL_CLAUDE_PATH, side_effect=ValueError("Claude response missing keys.")):
        response = client.post(
            "/regenerate-reply",
            json={
                "incoming_email": "Can we meet to discuss Q1?",
                "previous_reply": "Sure.",
                "regeneration_feedback": "Expand this.",
            },
        )
    assert response.status_code == 502
