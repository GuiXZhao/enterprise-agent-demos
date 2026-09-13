import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import CHROMA_DIR
from app.ingest import get_vectorstore, load_sample_docs
from app.research import run_research


def main():
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)
    loaded = load_sample_docs()
    print("loaded", len(loaded))
    print("store ok", get_vectorstore() is not None)
    r = run_research("采购合同付款周期是多少？")
    print("plan", r["plan"][:80])
    print("queries", r["search_queries"])
    print("answer len", len(r["answer"]))
    steps = [t["step"] for t in r["trace"]]
    print("trace", steps)
    print("rounds", r.get("retrieval_rounds", 0))
    assert "reflect" in steps, "v1.0 graph should include reflect step"


if __name__ == "__main__":
    main()
