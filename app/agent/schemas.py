from pydantic import BaseModel, Field


class AgentRequest(BaseModel):

    customer_id: int

    question: str = Field(
        min_length=3,
        max_length=2000,
    )

    thread_id: str

class AgentResponse(BaseModel):

    customer_id: int

    question: str

    answer: str

    used_policy: bool


class AgentResumeRequest(
    BaseModel
):
    thread_id: str

    approved: bool