from fastapi import FastAPI, File, HTTPException, UploadFile

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse



from app.config import API_KEY

from app.ingest import get_vectorstore, ingest_file, load_sample_docs

from app.research.graph import format_sse, iter_research_events, run_research

from app.schemas import ResearchRequest, ResearchResponse, TraceStep, UploadResponse



app = FastAPI(

    title="Enterprise Doc Research API",

    description="Demo A: 企业文档深度研究 Agent",

    version="1.1.0",

)

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_methods=["*"],

    allow_headers=["*"],

)





@app.get("/health")

def health():

    store = get_vectorstore()

    return {

        "status": "ok",

        "indexed": store is not None,

        "api_key_configured": bool(API_KEY and not API_KEY.startswith("sk-your")),

    }





@app.post("/documents/upload", response_model=UploadResponse)

async def upload_document(file: UploadFile = File(...)):

    if not file.filename:

        raise HTTPException(status_code=400, detail="缺少文件名")

    raw = await file.read()

    try:

        result = ingest_file(file.filename, raw)

    except ValueError as exc:

        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UploadResponse(**result)





@app.post("/documents/load-samples")

def ingest_samples():

    results = load_sample_docs()

    if not results:

        raise HTTPException(status_code=404, detail="sample_docs 目录为空")

    return {"loaded": len(results), "files": results}





def _to_response(result: dict) -> ResearchResponse:

    return ResearchResponse(

        question=result["question"],

        plan=result["plan"],

        search_queries=result["search_queries"],

        answer=result["answer"],

        citations=result["citations"],

        trace=[TraceStep(**item) for item in result["trace"]],

        retrieval_rounds=result.get("retrieval_rounds", 1),

        total_ms=result.get("total_ms"),

    )





@app.post("/research", response_model=ResearchResponse)

def research(body: ResearchRequest):

    if not API_KEY or API_KEY.startswith("sk-your"):

        raise HTTPException(status_code=500, detail="请配置 OPENAI_API_KEY")

    return _to_response(run_research(body.question.strip()))





@app.post("/research/stream")

def research_stream(body: ResearchRequest):

    if not API_KEY or API_KEY.startswith("sk-your"):

        raise HTTPException(status_code=500, detail="请配置 OPENAI_API_KEY")



    def event_generator():

        for event in iter_research_events(body.question.strip()):

            yield format_sse(event)



    return StreamingResponse(event_generator(), media_type="text/event-stream")


