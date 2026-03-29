import json
from typing import Optional

import anthropic

from config import settings


SYSTEM_TEMPLATE = """\
You are an email reply assistant. Your job is to draft email replies that sound \
personally written, not AI-generated.

You have two mandatory reference documents loaded below.

=== WORKFLOW (reply_to_email.md) ===
{workflow}

=== STYLE GUIDE (style_guide.md) ===
{style_guide}

=== OUTPUT RULES ===
You MUST return ONLY a single valid JSON object. No markdown fences. No extra text. \
No explanation before or after the JSON. The JSON must have exactly these five keys:

{{
  "intent": "one or two sentences describing what the sender wants",
  "missing_info": "any facts or confirmations needed before sending, or 'None' if none",
  "subject": "suggested reply subject line",
  "draft_reply": "the full email reply body, paste-ready, newlines preserved as \\n",
  "style_note": "one sentence explaining why this draft fits the style guide"
}}

If you include anything outside this JSON object your response will be rejected.
"""

USER_TEMPLATE_GENERATE = """\
Incoming email:
{incoming_email}
{extra_blocks}"""

USER_TEMPLATE_REGENERATE = """\
Incoming email:
{incoming_email}
{extra_blocks}"""


def _block(label: str, value: Optional[str]) -> str:
    if not value or not value.strip():
        return ""
    return f"\n{label}:\n{value.strip()}\n"


def build_system_prompt(workflow: str, style_guide: str) -> str:
    return SYSTEM_TEMPLATE.format(workflow=workflow, style_guide=style_guide)


def build_generate_user_prompt(
    incoming_email: str,
    reply_notes: Optional[str],
    regeneration_context: Optional[str],
) -> str:
    extra = _block("Reply notes", reply_notes) + _block("Additional context", regeneration_context)
    return USER_TEMPLATE_GENERATE.format(
        incoming_email=incoming_email.strip(),
        extra_blocks=extra,
    )


def build_regenerate_user_prompt(
    incoming_email: str,
    reply_notes: Optional[str],
    previous_reply: Optional[str],
    regeneration_feedback: Optional[str],
) -> str:
    extra = (
        _block("Reply notes", reply_notes)
        + _block("Previous draft (improve upon this)", previous_reply)
        + _block("Feedback on previous draft", regeneration_feedback)
    )
    return USER_TEMPLATE_REGENERATE.format(
        incoming_email=incoming_email.strip(),
        extra_blocks=extra,
    )


def call_claude(system_prompt: str, user_prompt: str) -> dict:
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is not configured on this server.")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    message = client.messages.create(
        model=settings.model,
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Claude returned non-JSON output.\n\nRaw response:\n{raw}") from exc

    required_keys = {"intent", "missing_info", "subject", "draft_reply", "style_note"}
    missing = required_keys - data.keys()
    if missing:
        raise ValueError(f"Claude response missing keys: {missing}.\n\nRaw response:\n{raw}")

    return data
