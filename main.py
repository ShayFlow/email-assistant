from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models.schemas import (
    GenerateReplyRequest,
    RegenerateReplyRequest,
    ReplyResponse,
)
from services.reply_generator import (
    build_system_prompt,
    build_generate_user_prompt,
    build_regenerate_user_prompt,
    call_claude,
)


BASE_DIR = Path(__file__).parent
WORKFLOW_PATH = BASE_DIR / "workflows" / "reply_to_email.md"
STYLE_GUIDE_PATH = BASE_DIR / "style_guide.md"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        app.state.style_guide = STYLE_GUIDE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required file not found at startup: {exc.filename}") from exc
    yield


app = FastAPI(
    title="Email Reply Assistant",
    description="Generates human-sounding email replies using Claude.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/generate-reply", response_model=ReplyResponse)
async def generate_reply(request: GenerateReplyRequest):
    system_prompt = build_system_prompt(
        workflow=app.state.workflow,
        style_guide=app.state.style_guide,
    )
    user_prompt = build_generate_user_prompt(
        incoming_email=request.incoming_email,
        reply_notes=request.reply_notes,
        regeneration_context=request.regeneration_context,
    )
    try:
        data = call_claude(system_prompt, user_prompt)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return ReplyResponse(**data)


@app.post("/regenerate-reply", response_model=ReplyResponse)
async def regenerate_reply(request: RegenerateReplyRequest):
    system_prompt = build_system_prompt(
        workflow=app.state.workflow,
        style_guide=app.state.style_guide,
    )
    user_prompt = build_regenerate_user_prompt(
        incoming_email=request.incoming_email,
        reply_notes=request.reply_notes,
        previous_reply=request.previous_reply,
        regeneration_feedback=request.regeneration_feedback,
    )
    try:
        data = call_claude(system_prompt, user_prompt)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return ReplyResponse(**data)


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
