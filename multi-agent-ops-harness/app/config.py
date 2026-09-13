import os
from pathlib import Path

from dotenv import load_dotenv

DEMO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = DEMO_ROOT / "data"
DB_PATH = DATA_DIR / "harness.db"

DEMO_A_ROOT = DEMO_ROOT.parent / "enterprise-doc-research"
DEMO_A_CHROMA = DEMO_A_ROOT / "data" / "chroma"
DEMO_A_SAMPLES = DEMO_A_ROOT / "sample_docs"

load_dotenv(DEMO_ROOT / ".env")
load_dotenv(DEMO_A_ROOT / ".env")
load_dotenv(DEMO_ROOT.parent / ".env")  # 作品集根目录 .env

API_KEY = os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv(
    "OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
CHAT_MODEL = os.getenv("OPENAI_MODEL", "qwen-plus")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-v3")

MAX_SUPERVISOR_STEPS = int(os.getenv("MAX_SUPERVISOR_STEPS", "10"))
# Windows 下 MCP 子进程偶发失败；演示稳定可设 false，需要时再切 true
USE_MCP_FOR_RESEARCH = os.getenv("USE_MCP_FOR_RESEARCH", "false").lower() in {
    "1",
    "true",
    "yes",
}
