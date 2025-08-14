from pydantic import BaseModel

class AskRequest(BaseModel):
    query: str
    program: str  # "ai" | "ai_product"
    background: str | None = None

class AskResponse(BaseModel):
    answer: str
    sources: list[str]
