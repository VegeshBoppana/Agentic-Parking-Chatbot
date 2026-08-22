import uuid

from langchain_core.messages import HumanMessage

from stage1_rag_chatbot.db.sql_store import create_tables, set_orchestrator_thread
from stage4_orchestration.graph import build_graph, get_checkpointer


def main() -> None:
    create_tables()
    thread_id = uuid.uuid4().hex[:8]
    messages = []

    print("SkyPark Parking Assistant (orchestrated) - type 'exit' to leave.\n")

    with get_checkpointer() as checkpointer:
        checkpointer.setup()
        graph = build_graph(checkpointer)

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                break
            if not user_input:
                continue

            messages.append(HumanMessage(content=user_input))
            config = {"configurable": {"thread_id": thread_id}}
            result = graph.invoke({"messages": messages, "reservation": None, "decision": None}, config=config)

            if result.get("reservation"):
                set_orchestrator_thread(result["reservation"]["reservation_id"], thread_id)

            if "__interrupt__" in result:
                print("Bot: Your reservation is pending administrator approval.\n")
                continue

            messages = result["messages"]
            print(f"Bot: {messages[-1].content}\n")


if __name__ == "__main__":
    main()