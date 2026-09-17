from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from langgraph.types import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.runtime import agent_graphs

from app.agent.graph import build_agent_graph
from app.agent.nodes import AgentNodes

from app.agent.schemas import (
    AgentRequest,
    AgentResponse,
    AgentResumeRequest,
)

from app.agent.tool_graph import (
    build_tool_agent_graph,
)

from app.agent.tool_nodes import (
    ToolAgentNodes,
)

from app.agent.tools import (
    AgentToolExecutor,
)

from app.ai.providers.factory import (
    get_llm_provider,
)

from app.db.database import get_db

from app.modules.customers.repository import (
    CustomerRepository,
)

from app.modules.interactions.repository import (
    InteractionRepository,
)

from app.modules.intelligence.repository import (
    CustomerIntelligenceRepository,
)

from app.modules.rag.repository import (
    RagRepository,
)

from app.modules.rag.service import (
    RagService,
)

from app.rag.embeddings import (
    TitanEmbeddingProvider,
)


router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


# =========================================================
# V1 - DETERMINISTIC LANGGRAPH AGENT
# =========================================================

@router.post(
    "/ask",
    response_model=AgentResponse,
)
async def ask_agent(
    request: AgentRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        embedding_provider = (
            TitanEmbeddingProvider()
        )

        rag_service = RagService(
            repository=RagRepository(db),
            embedding_provider=(
                embedding_provider
            ),
        )

        nodes = AgentNodes(
            customer_repository=(
                CustomerRepository(db)
            ),
            interaction_repository=(
                InteractionRepository(db)
            ),
            intelligence_repository=(
                CustomerIntelligenceRepository(
                    db
                )
            ),
            rag_service=rag_service,
            llm_provider=(
                get_llm_provider()
            ),
        )

        graph = build_agent_graph(
            nodes
        )

        result = await graph.ainvoke(
            {
                "customer_id":
                    request.customer_id,

                "question":
                    request.question,
            }
        )

        return AgentResponse(
            customer_id=(
                request.customer_id
            ),
            question=(
                request.question
            ),
            answer=result["answer"],
            used_policy=result.get(
                "needs_policy",
                False,
            ),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# V2 - NOVA TOOL-CALLING AGENT + LANGGRAPH
# =========================================================

@router.post(
    "/ask-v2",
)
async def ask_tool_agent(
    request: AgentRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        customer_repository = (
            CustomerRepository(db)
        )

        intelligence_repository = (
            CustomerIntelligenceRepository(
                db
            )
        )

        rag_service = RagService(
            repository=RagRepository(db),
            embedding_provider=(
                TitanEmbeddingProvider()
            ),
        )

        tool_executor = (
            AgentToolExecutor(
                customer_repository=(
                    customer_repository
                ),
                intelligence_repository=(
                    intelligence_repository
                ),
                rag_service=rag_service,
            )
        )

        nodes = ToolAgentNodes(
            llm_provider=(
                get_llm_provider()
            ),
            tool_executor=(
                tool_executor
            ),
        )

        graph = (
            build_tool_agent_graph(
                nodes
            )
        )

        # Temporary development registry.
        # Allows /resume to access the
        # interrupted graph.
        agent_graphs[
            request.thread_id
        ] = graph

        config = {
            "configurable": {
                "thread_id":
                    request.thread_id,
            }
        }

        result = await graph.ainvoke(
            {
                "customer_id":
                    request.customer_id,

                "question":
                    request.question,

                "iterations": 0,

                "tools_used": [],

                "question_added":
                    False,
            },
            config=config,
        )

        snapshot = await graph.aget_state(
        config
        )

        interrupts = []

        for task in snapshot.tasks:
            for interrupt in task.interrupts:
                interrupts.append(
                    interrupt.value
                )

        waiting_for_approval = (
            len(interrupts) > 0
        )

        return {
    "customer_id":
        request.customer_id,

    "question":
        request.question,

    "answer":
        result.get(
            "final_answer"
        ),

    "status": (
        "waiting_for_approval"
        if waiting_for_approval
        else "completed"
    ),

    "approval_required":
        waiting_for_approval,

    "approval_request": (
        interrupts[0]
        if interrupts
        else None
    ),

    "tools_used":
        result.get(
            "tools_used",
            []
        ),

    "iterations":
        result.get(
            "iterations",
            0
        ),

    "thread_id":
        request.thread_id,
}

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


# =========================================================
# RESUME INTERRUPTED V2 AGENT
# =========================================================

@router.post(
    "/resume",
)
async def resume_agent(
    request: AgentResumeRequest,
):
    graph = agent_graphs.get(
        request.thread_id
    )

    if graph is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Agent thread not found. "
                "Start the workflow using "
                "/ask-v2 first."
            ),
        )

    config = {
        "configurable": {
            "thread_id":
                request.thread_id,
        }
    }

    try:
        result = await graph.ainvoke(
            Command(
                resume={
                    "approved":
                        request.approved,
                }
            ),
            config=config,
        )

        return {
            "answer":
                result.get(
                    "final_answer"
                ),

            "tools_used":
                result.get(
                    "tools_used",
                    [],
                ),

            "approval_status":
                result.get(
                    "approval_status"
                ),

            "thread_id":
                request.thread_id,

            "iterations":
                result.get(
                    "iterations",
                    0,
                ),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )