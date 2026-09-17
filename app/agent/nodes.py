from app.agent.state import AgentState, ToolAgentState



class AgentNodes:

    def __init__(
        self,
        customer_repository,
        interaction_repository,
        intelligence_repository,
        rag_service,
        llm_provider,
    ):
        self.customers = customer_repository
        self.interactions = interaction_repository
        self.intelligence = intelligence_repository
        self.rag = rag_service
        self.llm = llm_provider

    async def load_customer(
        self,
        state: AgentState,
    ) -> dict:

        customer_id = state["customer_id"]

        customer = await self.customers.get_by_id(
            customer_id
        )

        if not customer:
            raise ValueError("Customer not found")

        interactions = (
            await self.interactions.get_by_customer(
                customer_id
            )
        )

        interaction_text = "\n".join(
            (
                f"{item.occurred_at} | "
                f"{item.direction} | "
                f"{item.channel} | "
                f"{item.interaction_type} | "
                f"{item.content}"
            )
            for item in interactions
        )

        context = f"""
Customer ID: {customer.id}
Name: {customer.name}
Company: {customer.company or "Unknown"}
Status: {customer.status}

Interactions:
{interaction_text}
"""

        return {
            "customer_context": context
        }

    async def load_intelligence(
        self,
        state: AgentState,
    ) -> dict:

        intelligence = (
            await self.intelligence.get_by_customer(
                state["customer_id"]
            )
        )

        if not intelligence:
            return {
                "intelligence_context":
                    "Customer intelligence has not been generated."
            }

        context = f"""
Sentiment: {intelligence.sentiment}
Intent: {intelligence.intent}
Churn Risk: {intelligence.churn_risk}
Urgency: {intelligence.urgency}
Primary Issue: {intelligence.primary_issue}
Summary: {intelligence.summary}
Recommended Action: {intelligence.recommended_action}
"""

        return {
            "intelligence_context": context
        }

    async def check_policy_requirement(
        self,
        state: AgentState,
    ) -> dict:

        question = state["question"].lower()

        policy_keywords = [
            "policy",
            "discount",
            "approval",
            "contact",
            "call",
            "follow up",
            "follow-up",
            "support",
            "escalate",
            "escalation",
        ]

        needs_policy = any(
            keyword in question
            for keyword in policy_keywords
        )

        return {
            "needs_policy": needs_policy
        }

    def route_policy(
        self,
        state: AgentState,
    ) -> str:

        if state.get("needs_policy", False):
            return "retrieve_policy"

        return "generate_answer"

    async def retrieve_policy(
        self,
        state: AgentState,
    ) -> dict:

        retriever = self.rag.create_retriever()

        results = await retriever.retrieve(
            query=state["question"],
            top_k=3,
            max_distance=0.75,
        )

        contexts = []

        for chunk, document, distance in results:

            contexts.append(
                f"""
SOURCE: {document.filename}
PAGE: {chunk.page_number}

CONTENT:
{chunk.content}
"""
            )

        return {
            "policy_context": "\n\n".join(
                contexts
            )
        }

    async def generate_answer(
        self,
        state: AgentState,
    ) -> dict:

        policy_context = state.get(
            "policy_context",
            "",
        )

        system_prompt = """
You are a customer intelligence assistant.

Use the supplied customer information,
customer intelligence and company policy.

Rules:
- Do not invent customer information.
- Do not invent company policies.
- If policy context is supplied, follow it.
- If required information is unavailable, say so.
- Keep recommendations practical.
- Company policy overrides an AI-generated
  recommendation if they conflict.
"""

        user_prompt = f"""
USER QUESTION:
{state["question"]}

CUSTOMER:
{state.get("customer_context", "")}

CUSTOMER INTELLIGENCE:
{state.get("intelligence_context", "")}

RETRIEVED COMPANY POLICY:
{policy_context or "No policy retrieval was required."}
"""

        answer = await self.llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        return {
            "answer": answer
        }



    async def call_agent(
        self,
        state: ToolAgentState,
    ) -> dict:

        messages = state.get(
            "messages",
            [],
        )

        if not messages:

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

        response = (
            await self.llm.converse_with_tools(
                messages=messages,
                tool_config=TOOL_CONFIG,
            )
        )

        assistant_message = (
            response["output"]["message"]
        )

        messages.append(
            assistant_message
        )

        tool_calls = []

        for block in assistant_message[
            "content"
        ]:

            if "toolUse" in block:

                tool_calls.append(
                    block["toolUse"]
                )

        final_answer = None

        messages = list(
            state.get(
                "messages",
                [],
            )
        )


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
            state.get("iterations", 0)
            + 1
        ),
        "question_added": True,
    }