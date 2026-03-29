from typing import Optional
from pydantic import BaseModel, field_validator


class GenerateReplyRequest(BaseModel):
    incoming_email: str
    reply_notes: Optional[str] = None
    regeneration_context: Optional[str] = None

    @field_validator("incoming_email")
    @classmethod
    def incoming_email_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("incoming_email cannot be empty")
        return v


class RegenerateReplyRequest(BaseModel):
    incoming_email: str
    reply_notes: Optional[str] = None
    previous_reply: Optional[str] = None
    regeneration_feedback: Optional[str] = None

    @field_validator("incoming_email")
    @classmethod
    def incoming_email_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("incoming_email cannot be empty")
        return v


class ReplyResponse(BaseModel):
    intent: str
    missing_info: str
    subject: str
    draft_reply: str
    style_note: str
