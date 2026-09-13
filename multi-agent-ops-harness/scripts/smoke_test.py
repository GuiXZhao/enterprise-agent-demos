import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import DEMO_A_CHROMA
from app.supervisor.graph import run_task


def main():
    if not DEMO_A_CHROMA.exists():
        print("WARN: Demo A chroma missing. Run scripts/load_demo_a_docs.py first")
    task = "采购合同金额 80 万，供应商延迟 20 天，按制度计算违约金并说明是否触顶 5% 上限。"
    r = run_task(task)
    print("agents", r["agents_used"])
    print("ms", r["total_ms"])
    print("answer preview", r["final_answer"][:200])
    assert len(r["agents_used"]) >= 2, "expected multi-agent"
    assert r["final_answer"], "expected answer"
    print("smoke OK")


if __name__ == "__main__":
    main()
