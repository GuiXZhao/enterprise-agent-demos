import time
from functools import lru_cache

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_openai.chat_models.base import OpenAIConnectionError

from app.config import API_KEY, BASE_URL, CHAT_MODEL, EMBEDDING_MODEL


@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=API_KEY,
        base_url=BASE_URL,
        check_embedding_ctx_length=False,
    )


@lru_cache
def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=CHAT_MODEL,
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=0.2,
    )


def invoke_llm(messages: list[BaseMessage], *, max_retries: int = 3):
    llm = get_llm()
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            return llm.invoke(messages)
        except OpenAIConnectionError as exc:
            last_error = exc
            if attempt + 1 >= max_retries:
                break
            time.sleep(1.5 * (attempt + 1))
    if last_error is not None:
        raise last_error
    raise RuntimeError("LLM invoke failed")
