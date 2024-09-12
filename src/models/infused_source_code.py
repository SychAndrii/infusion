from langchain_core.pydantic_v1 import BaseModel, Field

class InfusedSourceCode(BaseModel):
    source_code_with_docs: str = Field(description="Source code with generated comments")
