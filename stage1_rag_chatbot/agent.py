from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from datetime import date

from shared.llm import get_chat_model
from stage1_rag_chatbot.tools.search_policies_tool import search_parking_policies
from stage1_rag_chatbot.tools.availability_tool import check_parking_availability
from stage1_rag_chatbot.tools.reservation_tool import submit_reservation_request
from stage1_rag_chatbot.guardrails.pii_filter import detect_pii, redact_pii
from stage1_rag_chatbot.tools.check_reservation_status_tool import check_reservation_status

SYSTEM_PROMPT = f"""You are the SkyPark parking assistant chatbot.

Today's date is {date.today().isoformat()}. Use this to resolve any relative or
incomplete date/time references the customer gives (e.g. "today", "tomorrow",
"10AM to 11AM" with no date - assume today's date unless the customer says
otherwise). Never guess a date unrelated to today's actual date.

You help customers with three things:
1. Answering questions about parking - general info, working hours, pricing,
   locations, booking process, and rules - using the search_parking_policies tool.
2. Checking live space availability and pricing using the check_parking_availability tool.
3. Collecting a reservation request. To submit one, you MUST have all six details
   from the conversation: name, surname, car/vehicle number, zone, start_time, and
   end_time. If the customer gives a single full name (e.g. "John Doe"), split it
   yourself - first word(s) as name, last word as surname. Do not ask them to
   provide first and last name separately if they already gave a full name. Ask
   only for whatever is genuinely still missing.
4. Checking the status of an existing reservation using check_reservation_status -
   use the customer's car number if they don't remember their reservation ID.

Be concise and friendly. If asked something unrelated to SkyPark parking, politely
redirect the customer back to parking-related topics.
"""

_checkpointer = InMemorySaver()

agent = create_agent(
    model=get_chat_model(),
    tools=[search_parking_policies, check_parking_availability, submit_reservation_request, check_reservation_status],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=_checkpointer,
)


def chat(user_input: str, thread_id: str = "default") -> str:
    """Sends one user message to the agent and returns the reply."""
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
    return result["messages"][-1].content