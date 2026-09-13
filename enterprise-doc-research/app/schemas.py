from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    filename: str
    chunk_count: int
    char_count: int


class ResearchRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)


class TraceStep(BaseModel):
    step: str
    detail: str
    elapsed_ms: int | None = None
    total_ms: int | None = None


class ResearchResponse(BaseModel):
    question: str
    plan: str
    search_queries: list[str]
    answer: str
    citations: list[str]
    trace: list[TraceStep]
    retrieval_rounds: int = 1
    total_ms: int | None = None
