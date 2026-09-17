from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.agent.state import (
    AgentState,
)


def build_agent_graph(
    nodes,
):

    graph = StateGraph(
        AgentState
    )

    graph.add_node(
        "load_customer",
        nodes.load_customer,
    )

    graph.add_node(
        "load_intelligence",
        nodes.load_intelligence,
    )

    graph.add_node(
        "check_policy",
        nodes.check_policy_requirement,
    )

    graph.add_node(
        "retrieve_policy",
        nodes.retrieve_policy,
    )

    graph.add_node(
        "generate_answer",
        nodes.generate_answer,
    )

    graph.add_edge(
        START,
        "load_customer",
    )

    graph.add_edge(
        "load_customer",
        "load_intelligence",
    )

    graph.add_edge(
        "load_intelligence",
        "check_policy",
    )

    graph.add_conditional_edges(
        "check_policy",

        nodes.route_policy,

        {
            "retrieve_policy":
                "retrieve_policy",

            "generate_answer":
                "generate_answer",
        },
    )

    graph.add_edge(
        "retrieve_policy",
        "generate_answer",
    )

    graph.add_edge(
        "generate_answer",
        END,
    )

    return graph.compile()