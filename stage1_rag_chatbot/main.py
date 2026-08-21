import uuid

from stage1_rag_chatbot.agent import chat
from stage1_rag_chatbot.db.sql_store import create_tables


def main() -> None:
    create_tables()  # cheap, idempotent - safe even if bootstrap.py already ran
    thread_id = uuid.uuid4().hex[:8]
    print("SkyPark Parking Assistant - type 'exit' or 'quit' to leave.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        if not user_input:
            continue

        reply = chat(user_input, thread_id=thread_id)
        print(f"Bot: {reply}\n")


if __name__ == "__main__":
    main()