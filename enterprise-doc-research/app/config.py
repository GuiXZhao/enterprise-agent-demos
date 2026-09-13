import os
from pathlib import Path

from dotenv import load_dotenv

DEMO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = DEMO_ROOT / "data"
CHROMA_DIR = DATA_DIR / "chroma"
SAMPLE_DOCS_DIR = DEMO_ROOT / "sample_docs"

load_dotenv(DEMO_ROOT / ".env")
load_dotenv(DEMO_ROOT.parent / ".env")  # 作品集根目录 .env

API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv(
    "OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
CHAT_MODEL = os.getenv("OPENAI_MODEL", "qwen-plus")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-v3")
RESEARCH_API_URL = os.getenv("RESEARCH_API_URL", "http://127.0.0.1:8001")

CHUNK_SIZE = 600
CHUNK_OVERLAP = 80
RETRIEVAL_K = 4
HYBRID_POOL_SIZE = 16
RERANK_TOP_N = 6
RRF_K = 60
RERANK_MODEL = os.getenv("RERANK_MODEL", "gte-rerank-v2")
RERANK_API_URL = os.getenv(
    "RERANK_API_URL",
    "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank",
)
USE_HYBRID = os.getenv("USE_HYBRID", "true").lower() in {"1", "true", "yes"}
USE_RERANK = os.getenv("USE_RERANK", "true").lower() in {"1", "true", "yes"}
MAX_RETRIEVAL_ROUNDS = int(os.getenv("MAX_RETRIEVAL_ROUNDS", "2"))
