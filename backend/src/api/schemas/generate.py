from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Prompt describing the blog topic and requirements")


class GenerateResponse(BaseModel):
    title: str = Field(..., description="Suggested blog title")
    content: str = Field(..., description="Generated blog content (markdown)")
