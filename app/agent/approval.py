from langgraph.types import interrupt

from app.agent.state import (
    ToolAgentState,
)


async def request_approval(
    state: ToolAgentState,
) -> dict:

    tool_calls = state.get(
        "pending_tool_calls",
        [],
    )

    if not tool_calls:
        return {}

    tool_call = tool_calls[0]

    decision = interrupt(
        {
            "type":
                "human_approval",

            "tool":
                tool_call["name"],

            "arguments":
                tool_call["input"],

            "message":
                "Human approval required "
                "before executing this action.",
        }
    )

    approved = (
        decision.get(
            "approved",
            False,
        )
    )

    return {
        "approval_status": (
            "approved"
            if approved
            else "rejected"
        )
    }