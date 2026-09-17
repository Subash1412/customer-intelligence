from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.interactions.routes import (
    router as interaction_router,
)

from app.core.config import settings
from app.modules.customers.routes import router as customer_router
from app.modules.intelligence.routes import ( router as intelligence_router)

from app.modules.rag.routes import (
    router as rag_router,
)

from app.modules.rag.routes import (
    router as rag_router,
)

from app.modules.agent.routes import (
    router as agent_router,
)


app = FastAPI(
    title=settings.APP_NAME
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    customer_router,
    prefix="/api/v1",
)

app.include_router(
    interaction_router,
    prefix="/api/v1",
)

app.include_router(
    intelligence_router,
    prefix="/api/v1",
)

app.include_router(
    rag_router,
    prefix="/api/v1",
)   


app.include_router(
    agent_router,
    prefix="/api/v1",
)