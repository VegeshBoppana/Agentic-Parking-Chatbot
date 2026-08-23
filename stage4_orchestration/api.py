from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from pydantic import BaseModel

from stage1_rag_chatbot.db.sql_store import create_tables, get_reservation_by_id
from stage4_orchestration.graph import build_graph, get_checkpointer

WEB_UI_PATH = Path(__file__).resolve().parent.parent / "web_ui" / "index.html"

app = FastAPI(title="SkyPark Orchestrator Approval API")

_conversations: dict[str, list] = {}
_checkpointer_cm = None
_graph = None


def _get_graph():
    global _graph, _checkpointer_cm
    if _graph is None:
        create_tables()
        _checkpointer_cm = get_checkpointer()  # keep a reference so it isn't garbage-collected
        checkpointer = _checkpointer_cm.__enter__()
        checkpointer.setup()
        _graph = build_graph(checkpointer)
    return _graph


class ChatRequest(BaseModel):
    thread_id: str
    message: str


@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    graph = _get_graph()
    messages = _conversations.setdefault(req.thread_id, [])
    messages.append(HumanMessage(content=req.message))

    config = {"configurable": {"thread_id": req.thread_id}}
    result = graph.invoke({"messages": messages, "reservation": None, "decision": None}, config=config)

    if "__interrupt__" in result:
        reply = "Your reservation is now pending administrator approval."
    else:
        messages[:] = result["messages"]
        reply = messages[-1].content

    return {"reply": reply}


def _resume(reservation_id: str, decision: str) -> None:
    reservation = get_reservation_by_id(reservation_id)
    thread_id = reservation["orchestrator_thread_id"]
    graph = _get_graph()
    graph.invoke(Command(resume=decision), config={"configurable": {"thread_id": thread_id}})


@app.get("/orchestration/{reservation_id}/approve", response_class=HTMLResponse)
def approve(reservation_id: str):
    try:
        _resume(reservation_id, "approve")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return f"<h3>Reservation {reservation_id} approved.</h3>"


@app.get("/orchestration/{reservation_id}/reject", response_class=HTMLResponse)
def reject(reservation_id: str):
    try:
        _resume(reservation_id, "reject")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return f"<h3>Reservation {reservation_id} rejected.</h3>"


@app.get("/", response_class=HTMLResponse)
def index():
    return WEB_UI_PATH.read_text(encoding="utf-8")