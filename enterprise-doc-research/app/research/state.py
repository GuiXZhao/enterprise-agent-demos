import operator
from typing import Annotated, TypedDict

from langchain_core.documents import Document


class ResearchState(TypedDict):
    question: str
    plan: str
    search_queries: list[str]
    retrieved_docs: list[Document]
    answer: str
    citations: list[str]
    trace: Annotated[list[dict], operator.add]
    retrieval_round: int
    max_retrieval_rounds: int
    reflect_sufficient: bool
