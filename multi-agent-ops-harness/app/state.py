import operator
from typing import Annotated, TypedDict


class HarnessState(TypedDict):
    task: str
    plan: str
    current_instruction: str
    next_agent: str
    research_notes: str
    analysis_result: str
    draft_report: str
    final_answer: str
    step_count: int
    agents_used: Annotated[list[str], operator.add]
    trace: Annotated[list[dict], operator.add]
