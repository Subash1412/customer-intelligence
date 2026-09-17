from typing import TypedDict


class AgentState(
    TypedDict,
    total=False,
):
    customer_id: int

    question: str

    customer_context: str

    intelligence_context: str

    policy_context: str

    needs_policy: bool

    answer: str




class ToolAgentState(
    TypedDict,
    total=False,
):
    customer_id: int
    question: str

    messages: list
    pending_tool_calls: list

    final_answer: str
    tools_used: list[str]

    iterations: int
    question_added: bool

    approval_required: bool
    approval_status: str