from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.config import API_KEY
from app.db import init_db
from app.supervisor.graph import format_sse, iter_task_events, run_task

app = FastAPI(
    title="Multi-Agent Ops Harness API",
    description="Demo B: Supervisor + Research/Analyst/Reporter",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task: str = Field(min_length=4, max_length=4000)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "api_key_configured": bool(API_KEY and not API_KEY.startswith("sk-your")),
    }


@app.post("/tasks/run")
def tasks_run(body: TaskRequest):
    if not API_KEY or API_KEY.startswith("sk-your"):
        raise HTTPException(status_code=500, detail="请配置 OPENAI_API_KEY")
    return run_task(body.task.strip())


@app.post("/tasks/stream")
def tasks_stream(body: TaskRequest):
    if not API_KEY or API_KEY.startswith("sk-your"):
        raise HTTPException(status_code=500, detail="请配置 OPENAI_API_KEY")

    def generator():
        for event in iter_task_events(body.task.strip()):
            yield format_sse(event)

    return StreamingResponse(generator(), media_type="text/event-stream")
