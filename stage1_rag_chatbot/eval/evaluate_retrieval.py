from langsmith import Client, evaluate

from stage1_rag_chatbot.db.vector_store import search
from stage1_rag_chatbot.eval.eval_dataset import EVAL_DATASET
from stage1_rag_chatbot.eval.ir_metrics import precision_at_k, reciprocal_rank, recall_at_k

DATASET_NAME = "skypark-stage1-ir-metrics"
K = 3


def ensure_dataset() -> None:
    client = Client()
    if not client.has_dataset(dataset_name=DATASET_NAME):
        client.create_dataset(DATASET_NAME, description="Stage 1 retrieval eval - Recall@K, Precision@K, MRR")
        client.create_examples(
            dataset_name=DATASET_NAME,
            examples=[
                {"inputs": {"question": item["question"]}, "outputs": {"expected_policy": item["expected_policy"]}}
                for item in EVAL_DATASET
            ],
        )


def target(inputs: dict) -> dict:
    docs = search(inputs["question"], top_k=K)
    retrieved_policies = [d.metadata.get("policy_name", "") for d in docs]
    return {"retrieved_policies": retrieved_policies}


def recall_evaluator(outputs: dict, reference_outputs: dict) -> dict:
    score = recall_at_k(outputs["retrieved_policies"], reference_outputs["expected_policy"], K)
    return {"key": f"recall_at_{K}", "score": score}


def precision_evaluator(outputs: dict, reference_outputs: dict) -> dict:
    score = precision_at_k(outputs["retrieved_policies"], reference_outputs["expected_policy"], K)
    return {"key": f"precision_at_{K}", "score": score}


def mrr_evaluator(outputs: dict, reference_outputs: dict) -> dict:
    score = reciprocal_rank(outputs["retrieved_policies"], reference_outputs["expected_policy"])
    return {"key": "mrr", "score": score}


def main() -> None:
    ensure_dataset()
    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[recall_evaluator, precision_evaluator, mrr_evaluator],
        experiment_prefix="stage1-ir-metrics",
    )
    print(results)


if __name__ == "__main__":
    main()