import json
from typing import AsyncGenerator, List, Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from smartcareerpro.config import config
from smartcareerpro.core.glm_client import glm_client
from smartcareerpro.core.prompts import (
    CAREER_ADVISOR_PROMPT,
    INTERVIEW_COACH_PROMPT,
    JD_MATCHER_PROMPT,
    RESUME_ANALYZER_PROMPT,
    RESUME_IMPROVER_PROMPT,
    SKILLS_GAP_PROMPT,
)

router = APIRouter(prefix="/api")

_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}


# ── request models ────────────────────────────────────────────────────────────

class ResumeRequest(BaseModel):
    resume: str
    target_role: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    feature: str  # "interview" | "career"


class SkillsGapRequest(BaseModel):
    current_skills: str
    target_role: str
    experience_level: Optional[str] = None


class JDMatchRequest(BaseModel):
    resume: str
    job_description: str


# ── SSE helper ────────────────────────────────────────────────────────────────

async def sse(messages: list) -> AsyncGenerator[str, None]:
    async for chunk in glm_client.stream(messages):
        yield f"data: {json.dumps({'text': chunk})}\n\n"
    yield "data: [DONE]\n\n"


def stream(messages: list) -> StreamingResponse:
    return StreamingResponse(sse(messages), media_type="text/event-stream", headers=_SSE_HEADERS)


# ── resume endpoints ──────────────────────────────────────────────────────────

@router.post("/resume/analyze")
async def analyze_resume(req: ResumeRequest):
    user_msg = f"Please analyze this resume:\n\n{req.resume}"
    if req.target_role:
        user_msg += f"\n\nTarget role: {req.target_role}"
    return stream([
        {"role": "system", "content": RESUME_ANALYZER_PROMPT},
        {"role": "user", "content": user_msg},
    ])


@router.post("/resume/improve")
async def improve_resume(req: ResumeRequest):
    user_msg = f"Please improve this resume"
    if req.target_role:
        user_msg += f" for the role: {req.target_role}"
    user_msg += f":\n\n{req.resume}"
    return stream([
        {"role": "system", "content": RESUME_IMPROVER_PROMPT},
        {"role": "user", "content": user_msg},
    ])


# ── chat endpoint (interview + career) ───────────────────────────────────────

@router.post("/chat")
async def chat(req: ChatRequest):
    system = INTERVIEW_COACH_PROMPT if req.feature == "interview" else CAREER_ADVISOR_PROMPT
    messages = [{"role": "system", "content": system}]
    messages.extend({"role": m.role, "content": m.content} for m in req.messages)
    return stream(messages)


# ── skills gap endpoint ───────────────────────────────────────────────────────

@router.post("/skills/gap")
async def skills_gap(req: SkillsGapRequest):
    user_msg = f"Target role: {req.target_role}\n\nMy current skills and experience:\n{req.current_skills}"
    if req.experience_level:
        user_msg += f"\n\nMy experience level: {req.experience_level}"
    return stream([
        {"role": "system", "content": SKILLS_GAP_PROMPT},
        {"role": "user", "content": user_msg},
    ])


# ── JD matcher endpoint ───────────────────────────────────────────────────────

@router.post("/jd/match")
async def jd_match(req: JDMatchRequest):
    user_msg = f"Resume:\n{req.resume}\n\n---\n\nJob Description:\n{req.job_description}"
    return stream([
        {"role": "system", "content": JD_MATCHER_PROMPT},
        {"role": "user", "content": user_msg},
    ])


# ── health endpoint ───────────────────────────────────────────────────────────

@router.get("/health")
async def health():
    return {"status": "ok", "model": config.model}
