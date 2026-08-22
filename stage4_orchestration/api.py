from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from langgraph.types import Command

from stage1_rag_chatbot.db.sql_store import get_reservation_by_id
from stage4_orchestration.graph import build_graph, get_checkpointer

app = FastAPI(title="SkyPark Orchestrator Approval API")


def _resume(reservation_id: str, decision: str) -> None:
    reservation = get_reservation_by_id(reservation_id)
    thread_id = reservation["orchestrator_thread_id"]
    with get_checkpointer() as checkpointer:
        checkpointer.setup()
        graph = build_graph(checkpointer)
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