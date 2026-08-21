from functools import lru_cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from shared.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL, OPENAI_EMBEDDING_MODEL, OPENAI_MAX_TOKENS

# we used @lru_cache here becasue we are creating the functions here and reusing everywhere
@lru_cache(maxsize=1)
def get_chat_model() -> ChatOpenAI:
    return ChatOpenAI(
        model=OPENAI_CHAT_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0,
        max_tokens=OPENAI_MAX_TOKENS,
    )


@lru_cache(maxsize=1)
def get_embedding_model() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=OPENAI_EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY,
    )