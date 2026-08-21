from typing import Annotated, TypedDict
from shared.llm import get_chat_model
from stage1_rag_chatbot.db.vector_store import search
from langsmith import Client, evaluate

DATASET_NAME = "skypark-stage1-rag-triad"

def ensure_dataset() -> None:
    client = Client()
    if not client.has_dataset(dataset_name=DATASET_NAME):
        client.create_dataset(DATASET_NAME, description="Stage 1 RAG Triad eval questions")
        client.create_examples(
            dataset_name=DATASET_NAME,
            examples=[{"inputs": {"question": q}} for q in QUESTIONS],
        )


def main() -> None:
    ensure_dataset()
    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[groundedness, answer_relevance, retrieval_relevance],
        experiment_prefix="stage1-rag-triad",
    )
    print(results)

QUESTIONS = [
    "What are the parking rules?",
    "What are the working hours and pricing?",
    "Which zone has EV charging spots?",
    "How do I reserve a parking space?",
    "Is smoking allowed in the parking facility?",
]


def target(inputs: dict) -> dict:
    question = inputs["question"]
    docs = search(question, top_k=5)
    context = "\n\n".join(d.page_content for d in docs)

    answer = get_chat_model().invoke(
        f"Answer the question using ONLY the context below.\n\nContext:\n{context}\n\nQuestion: {question}"
    ).content

    return {"answer": answer, "context": context}


class Grade(TypedDict):
    score: Annotated[bool, ..., "True if the criterion is met, False otherwise"]
    reasoning: Annotated[str, ..., "Brief explanation for the score"]


def _judge(prompt: str) -> Grade:
    return get_chat_model().with_structured_output(Grade).invoke(prompt)


def groundedness(inputs: dict, outputs: dict) -> dict:
    grade = _judge(
        f"Context:\n{outputs['context']}\n\nAnswer:\n{outputs['answer']}\n\n"
        "Is the answer fully supported by the context, with no unsupported claims?"
    )
    return {"key": "groundedness", "score": grade["score"], "comment": grade["reasoning"]}


def answer_relevance(inputs: dict, outputs: dict) -> dict:
    grade = _judge(
        f"Question:\n{inputs['question']}\n\nAnswer:\n{outputs['answer']}\n\n"
        "Does the answer directly and adequately address the question?"
    )
    return {"key": "answer_relevance", "score": grade["score"], "comment": grade["reasoning"]}


def retrieval_relevance(inputs: dict, outputs: dict) -> dict:
    grade = _judge(
        f"Question:\n{inputs['question']}\n\nRetrieved context:\n{outputs['context']}\n\n"
        "Is the retrieved context relevant to answering the question?"
    )
    return {"key": "retrieval_relevance", "score": grade["score"], "comment": grade["reasoning"]}



if __name__ == "__main__":
    main()