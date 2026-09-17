TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_customer",
                "description": (
                    "Get basic information about a customer "
                    "using the customer ID."
                ),
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "customer_id"
                        ]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "get_customer_intelligence",
                "description": (
                    "Get AI-generated customer intelligence "
                    "including sentiment, intent, churn risk, "
                    "urgency and recommended action."
                ),
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "integer"
                            }
                        },
                        "required": [
                            "customer_id"
                        ]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "search_company_policy",
                "description": (
                    "Search company policy documents. "
                    "Use this for questions about discounts, "
                    "approvals, customer contact, follow-ups, "
                    "support and escalation rules."
                ),
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "query"
                        ]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "propose_customer_followup",
                "description": (
                    "Propose a customer follow-up action. "
                    "Use this when a concrete human action "
                    "should be taken for the customer."
                ),
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "customer_id": {
                                "type": "integer"
                            },
                            "action": {
                                "type": "string"
                            },
                            "reason": {
                                "type": "string"
                            }
                        },
                        "required": [
                            "customer_id",
                            "action",
                            "reason"
                        ]
                    }
                }
            }
        }
    ]
}


ACTION_TOOLS = {
    "propose_customer_followup",
}


class AgentToolExecutor:

    def __init__(
        self,
        customer_repository,
        intelligence_repository,
        rag_service,
    ):
        self.customers = customer_repository
        self.intelligence = intelligence_repository
        self.rag = rag_service

    async def execute(
        self,
        tool_name: str,
        tool_input: dict,
    ) -> dict:

        if tool_name == "get_customer":
            return await self._get_customer(
                tool_input["customer_id"]
            )

        if tool_name == "get_customer_intelligence":
            return await self._get_intelligence(
                tool_input["customer_id"]
            )

        if tool_name == "search_company_policy":
            return await self._search_policy(
                tool_input["query"]
            )

        if tool_name == "propose_customer_followup":
            return await self._propose_customer_followup(
                customer_id=tool_input["customer_id"],
                action=tool_input["action"],
                reason=tool_input["reason"],
            )

        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

        if tool_name == "propose_customer_followup":

            return await self._propose_followup(
                customer_id=tool_input[
                    "customer_id"
                ],
                action=tool_input[
                    "action"
                ],
                reason=tool_input[
                    "reason"
                ],
            )

    async def _get_customer(
        self,
        customer_id: int,
    ) -> dict:

        customer = await self.customers.get_by_id(
            customer_id
        )

        if not customer:
            return {
                "error": "Customer not found"
            }

        return {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "company": customer.company,
            "status": customer.status,
        }

    async def _get_intelligence(
        self,
        customer_id: int,
    ) -> dict:

        intelligence = await self.intelligence.get_by_customer(
            customer_id
        )

        if not intelligence:
            return {
                "error": "Customer intelligence not found"
            }

        return {
            "sentiment": intelligence.sentiment,
            "intent": intelligence.intent,
            "churn_risk": intelligence.churn_risk,
            "urgency": intelligence.urgency,
            "primary_issue": intelligence.primary_issue,
            "summary": intelligence.summary,
            "recommended_action": intelligence.recommended_action,
        }

    async def _search_policy(
        self,
        query: str,
    ) -> dict:

        retriever = self.rag.create_retriever()

        results = await retriever.retrieve(
            query=query,
            top_k=3,
            max_distance=0.75,
        )

        sources = []

        for chunk, document, distance in results:
            sources.append(
                {
                    "content": chunk.content,
                    "filename": document.filename,
                    "page": chunk.page_number,
                    "distance": float(distance),
                }
            )

        return {
            "results": sources
        }

    async def _propose_customer_followup(
        self,
        customer_id: int,
        action: str,
        reason: str,
    ) -> dict:

        return {
            "customer_id": customer_id,
            "action": action,
            "reason": reason,
            "status": "proposed",
        }

    async def _propose_followup(
    self,
    customer_id: int,
    action: str,
    reason: str,
) -> dict:

        customer = (
            await self.customers.get_by_id(
                customer_id
            )
        )

        if not customer:
            return {
                "error": "Customer not found"
            }

        return {
            "status": "created",
            "customer_id": customer_id,
            "action": action,
            "reason": reason,
        }