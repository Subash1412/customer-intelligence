from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.agent.approval import request_approval
from app.agent.state import ToolAgentState


checkpointer = MemorySaver()


def build_tool_agent_graph(
    nodes,
):
    graph = StateGraph(
        ToolAgentState
    )

    graph.add_node(
        "agent",
        nodes.call_agent,
    )

    graph.add_node(
        "tools",
        nodes.execute_tools,
    )

    graph.add_node(
        "route_tool",
        lambda state: {},
    )

    graph.add_node(
        "approval",
        request_approval,
    )

    graph.add_node(
        "rejected",
        nodes.handle_rejection,
    )

    graph.add_edge(
        START,
        "agent",
    )

    graph.add_conditional_edges(
        "agent",
        nodes.route_agent,
        {
            "tools": "route_tool",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "route_tool",
        nodes.route_tool,
        {
            "tools": "tools",
            "approval": "approval",
        },
    )

    graph.add_conditional_edges(
        "approval",
        nodes.route_approval,
        {
            "tools": "tools",
            "rejected": "rejected",
        },
    )

    graph.add_edge(
        "tools",
        "agent",
    )

    graph.add_edge(
        "rejected",
        "agent",
    )

    return graph.compile(
        checkpointer=checkpointer
    )