def recall_at_k(retrieved_policies: list[str], expected_policy: str, k: int) -> float:
    """1.0 if expected_policy appears anywhere in the top k retrieved, else 0.0."""
    return 1.0 if expected_policy in retrieved_policies[:k] else 0.0


def precision_at_k(retrieved_policies: list[str], expected_policy: str, k: int) -> float:
    """With exactly one relevant item: 1/k if found in the top k, else 0.0."""
    return (1.0 / k) if expected_policy in retrieved_policies[:k] else 0.0


def reciprocal_rank(retrieved_policies: list[str], expected_policy: str) -> float:
    """1 / rank of the first correct match, or 0.0 if not found at all."""
    for i, policy in enumerate(retrieved_policies, start=1):
        if policy == expected_policy:
            return 1.0 / i
    return 0.0