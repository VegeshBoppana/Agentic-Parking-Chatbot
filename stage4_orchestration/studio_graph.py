from langgraph.graph import END, START, StateGraph

from stage4_orchestration.nodes.administrator_approval import administrator_approval_node
from stage4_orchestration.nodes.data_recording import data_recording_node
from stage4_orchestration.nodes.user_interaction import user_interaction_node
from stage4_orchestration.nodes.wait_for_decision import wait_for_decision_node
from stage4_orchestration.state import OrchestratorState


def _route_after_user_interaction(state: OrchestratorState) -> str:
    return "administrator_approval" if state.get("reservation") else END


graph = StateGraph(OrchestratorState)
graph.add_node("user_interaction", user_interaction_node)
graph.add_node("administrator_approval", administrator_approval_node)
graph.add_node("wait_for_decision", wait_for_decision_node)
graph.add_node("data_recording", data_recording_node)

graph.add_edge(START, "user_interaction")
graph.add_conditional_edges(
    "user_interaction", _route_after_user_interaction,
    {"administrator_approval": "administrator_approval", END: END},
)
graph.add_edge("administrator_approval", "wait_for_decision")
graph.add_edge("wait_for_decision", "data_recording")
graph.add_edge("data_recording", END)