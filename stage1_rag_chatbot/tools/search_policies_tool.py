from langchain.tools import tool

from stage1_rag_chatbot.db.vector_store import search


@tool
def search_parking_policies(query: str) -> str:
    """Search SkyPark's policy documents for general info, working hours, pricing,
    locations, booking process, and facility rules/guidelines."""
    docs = search(query, top_k=5)
    if not docs:
        return "No relevant policy information found."
    return "\n\n".join(f"[{d.metadata.get('policy_name', '?')}] {d.page_content}" for d in docs)