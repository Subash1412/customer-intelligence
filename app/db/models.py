from app.db.base import Base

from app.modules.customers.models import Customer
from app.modules.interactions.models import Interaction
from app.modules.intelligence.models import CustomerIntelligence
from app.modules.rag.models import RagDocument,RagChunk
__all__ = [
    "Base",
    "Customer",
    "Interaction",
    "CustomerIntelligence",
    "RagDocument",
    "RagChunk",
]

