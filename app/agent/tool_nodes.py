from app.agent.state import ToolAgentState
from app.agent.tools import TOOL_CONFIG
from app.agent.tools import (
    ACTION_TOOLS,
)


class ToolAgentNodes:

    def __init__(
        self,
        llm_provider,
        tool_executor,
    ):
        self.llm = llm_provider
        self.tools = tool_executor

    async def call_agent(
    self,
    state: ToolAgentState,
    ) -> dict:

    # Copy existing conversation history
        messages = list(
            state.get(
                "messages",
                [],
            )
        )

    # Add the current question only once.
    # Agent -> Tool -> Agent loops must not
    # add the same question repeatedly.
        if not state.get(
            "question_added",
            False,
        ):
            question = f"""
    Customer ID: {state["customer_id"]}

    User request:
    {state["question"]}
    """

            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "text": question
                        }
                    ],
                }
            )

        # Ask Nova what to do next
        response = (
            await self.llm.converse_with_tools(
                messages=messages,
                tool_config=TOOL_CONFIG,
            )
        )

        assistant_message = (
            response["output"]["message"]
        )

        # Save Nova's response/tool request
        messages.append(
            assistant_message
        )

        tool_calls = []

        # Find tools requested by Nova
        for block in assistant_message[
            "content"
        ]:
            if "toolUse" in block:
                tool_calls.append(
                    block["toolUse"]
                )

        final_answer = None

        # No tool call means Nova has
        # produced the final answer
        if not tool_calls:
            for block in assistant_message[
                "content"
            ]:
                if "text" in block:
                    final_answer = (
                        block["text"]
                    )
                    break

        return {
            "messages": messages,
            "pending_tool_calls": tool_calls,
            "final_answer": final_answer,
            "iterations": (
                state.get(
                    "iterations",
                    0,
                )
                + 1
            ),
            "question_added": True,
        }

    async def execute_tools(
        self,
        state: ToolAgentState,
    ) -> dict:

        tool_calls = state.get(
            "pending_tool_calls",
            [],
        )

        messages = state["messages"]

        tools_used = list(
            state.get(
                "tools_used",
                [],
            )
        )

        tool_results = []

        for tool_call in tool_calls:

            tool_name = tool_call["name"]

            tool_input = tool_call["input"]

            result = (
                await self.tools.execute(
                    tool_name=tool_name,
                    tool_input=tool_input,
                )
            )

            tools_used.append(
                tool_name
            )

            tool_results.append(
                {
                    "toolResult": {
                        "toolUseId":
                            tool_call[
                                "toolUseId"
                            ],

                        "content": [
                            {
                                "json": result
                            }
                        ],

                        "status": "success",
                    }
                }
            )

        # Tool results are sent back to Nova
        messages.append(
            {
                "role": "user",
                "content": tool_results,
            }
        )

        return {
            "messages": messages,
            "pending_tool_calls": [],
            "tools_used": tools_used,
        }

    def route_agent(
        self,
        state: ToolAgentState,
    ) -> str:

        # Prevent infinite agent/tool loops
        if state.get(
            "iterations",
            0,
        ) >= 6:
            return "end"

        # Nova requested one or more tools
        if state.get(
            "pending_tool_calls"
        ):
            return "tools"

        # Nova produced final response
        return "end"

    def route_tool(
        self,
        state: ToolAgentState,
    ) -> str:

        tool_calls = state.get(
            "pending_tool_calls",
            [],
        )

        if not tool_calls:
            return "agent"

        requires_approval = any(
            tool_call["name"]
            in ACTION_TOOLS

            for tool_call
            in tool_calls
        )

        if requires_approval:
            return "approval"

        return "tools"


    async def handle_rejection(
        self,
        state: ToolAgentState,
    ) -> dict:

        messages = list(
            state["messages"]
        )

        tool_results = []

        for tool_call in state.get(
            "pending_tool_calls",
            [],
        ):

            tool_results.append(
                {
                    "toolResult": {
                        "toolUseId":
                            tool_call[
                                "toolUseId"
                            ],

                        "content": [
                            {
                                "json": {
                                    "status":
                                        "rejected",

                                    "reason":
                                        "Human rejected "
                                        "the proposed action."
                                }
                            }
                        ],

                        "status":
                            "success",
                    }
                }
            )

        messages.append(
            {
                "role": "user",
                "content": tool_results,
            }
        )

        return {
            "messages": messages,
            "pending_tool_calls": [],
        }

    def route_approval(
        self,
        state: ToolAgentState,
    ) -> str:

        if (
            state.get(
                "approval_status"
            )
            == "approved"
        ):
            return "tools"

        return "rejected"