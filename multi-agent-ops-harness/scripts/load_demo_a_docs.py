"""加载 Demo A sample_docs 到共享 Chroma（Demo B 检索依赖）。"""

import sys
from pathlib import Path

DEMO_A = Path(__file__).resolve().parent.parent.parent / "enterprise-doc-research"
sys.path.insert(0, str(DEMO_A))

from app.ingest import get_vectorstore, load_sample_docs


def main():
    loaded = load_sample_docs()
    print(f"loaded {len(loaded)} files")
    print("store ok", get_vectorstore() is not None)


if __name__ == "__main__":
    main()
