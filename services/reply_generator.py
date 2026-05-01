import json
from typing import Optional

import anthropic

from config import settings

try:
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        TextBlock,
        query,
    )
    _HAS_AGENT_SDK = True
except ImportError:
    _HAS_AGENT_SDK = False


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


REQUIRED_KEYS = {"intent", "missing_info", "subject", "draft_reply", "style_note"}


def _parse_response(raw: str) -> dict:
    raw = raw.strip()
    # Some models wrap JSON in ```json fences despite instructions; strip them.
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        if raw.endswith("```"):
            raw = raw[: -3]
        raw = raw.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Claude returned non-JSON output.\n\nRaw response:\n{raw}") from exc
    missing = REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"Claude response missing keys: {missing}.\n\nRaw response:\n{raw}")
    return data


async def _call_via_subscription(system_prompt: str, user_prompt: str) -> dict:
    if not _HAS_AGENT_SDK:
        raise ValueError(
            "claude-agent-sdk is not installed. Run `pip install claude-agent-sdk` "
            "or set USE_SUBSCRIPTION=false to fall back to the API key."
        )
    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        model=settings.model,
        max_turns=1,
    )
    chunks: list[str] = []
    async for message in query(prompt=user_prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    chunks.append(block.text)
    raw = "".join(chunks)
    if not raw.strip():
        raise ValueError("Claude (subscription) returned an empty response.")
    return _parse_response(raw)


def _call_via_api_key(system_prompt: str, user_prompt: str) -> dict:
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is not configured on this server.")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    message = client.messages.create(
        model=settings.model,
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    raw = message.content[0].text
    return _parse_response(raw)


async def call_claude(system_prompt: str, user_prompt: str) -> dict:
    if settings.use_subscription:
        return await _call_via_subscription(system_prompt, user_prompt)
    return _call_via_api_key(system_prompt, user_prompt)
