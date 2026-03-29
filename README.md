# Email Reply Assistant — Backend

FastAPI backend that generates human-sounding email replies using Claude.

## Requirements

- Python 3.11+
- An Anthropic API key

## Setup

1. Navigate to the project folder:

   cd email_assistant

2. Create a virtual environment and install dependencies:

   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

3. Copy .env.example to .env and fill in your API key:

   ANTHROPIC_API_KEY=sk-ant-...
   MODEL=claude-sonnet-4-6

4. Run the server:

   python main.py

   Or with uvicorn directly:

   uvicorn main:app --reload --host 0.0.0.0 --port 8000

The API will be available at http://localhost:8000.
Interactive docs at http://localhost:8000/docs.

---

## Endpoints

### GET /health

Returns a simple health check.

Response:
{
  "status": "ok"
}

---

### POST /generate-reply

Generate a first reply draft for an incoming email.

Request body:
{
  "incoming_email": "string (required)",
  "reply_notes": "string (optional) — how you want to respond, tone, specific points to cover",
  "regeneration_context": "string (optional) — additional context about the situation"
}

curl example:

curl -X POST http://localhost:8000/generate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "incoming_email": "Hi, I wanted to follow up on my maintenance request from last week. The leak in the bathroom has not been fixed yet. Can you provide an update?",
    "reply_notes": "The plumber is scheduled for Thursday. Apologize for the delay."
  }'

---

### POST /regenerate-reply

Regenerate a reply using feedback on a previous draft.

Request body:
{
  "incoming_email": "string (required)",
  "reply_notes": "string (optional)",
  "previous_reply": "string (optional) — the draft the user wants to improve",
  "regeneration_feedback": "string (optional) — specific instructions for what to change"
}

curl example:

curl -X POST http://localhost:8000/regenerate-reply \
  -H "Content-Type: application/json" \
  -d '{
    "incoming_email": "Hi, I wanted to follow up on my maintenance request from last week. The leak in the bathroom has not been fixed yet. Can you provide an update?",
    "previous_reply": "Hi,\n\nThank you for following up. The plumber is scheduled for Thursday.\n\nPlease let me know if you need anything further.\n\nBest regards,",
    "regeneration_feedback": "Make it warmer and apologize more clearly for the delay."
  }'

---

## Response (both endpoints)

{
  "intent": "Resident is following up on an unresolved maintenance request and wants an update.",
  "missing_info": "None",
  "subject": "Re: Maintenance Request - Bathroom Leak",
  "draft_reply": "Hi,\n\nI apologize for the delay in getting this resolved. The plumber is scheduled to attend on Thursday and will take care of the leak at that time.\n\nPlease let me know if you need anything further.\n\nBest regards,",
  "style_note": "Direct, apologetic without over-explaining, closes the loop with a specific date."
}

---

## Project structure

  main.py                        FastAPI app, CORS, startup, routes
  config.py                      Settings loaded from .env
  models/schemas.py              Request and response Pydantic models
  services/reply_generator.py    Prompt building and Claude API call
  workflows/reply_to_email.md    Loaded at startup into the system prompt
  style_guide.md                 Loaded at startup into the system prompt

---

## Lovable integration

Point your Lovable frontend at:

  Base URL: http://localhost:8000  (local)
             https://your-app.railway.app  (deployed)

Call POST /generate-reply on first submit.
Call POST /regenerate-reply when the user clicks "Regenerate", passing back the
previous draft and any feedback they typed.

All responses are plain JSON. The draft_reply field uses \n for line breaks.
Render it in a <textarea> or a <pre> block, or split on \n to display paragraphs.

---

## Deploying to Railway

1. Push the project to a GitHub repo.
2. Create a new Railway project and connect the repo.
3. Set environment variables in Railway dashboard:
   - ANTHROPIC_API_KEY
   - MODEL (optional, defaults to claude-sonnet-4-6)
4. Railway will detect the Python app and run it automatically.
   Set the start command to: uvicorn main:app --host 0.0.0.0 --port $PORT
