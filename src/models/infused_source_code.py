from langchain_core.pydantic_v1 import BaseModel, Field

class InfusedSourceCode(BaseModel):
    """
    A Pydantic model representing source code that has been infused with documentation.

    This model is used to encapsulate the source code along with the generated comments,
    typically produced by a language model. The `source_code_with_docs` field contains 
    the source code in string format, now enriched with comments or documentation.
    """

    source_code_with_docs: str = Field(description="Source code with generated comments. If file violates syntax of a programming language supplied - make this empty string.")
    error: bool = Field(
        description="If file violates syntax of a programming language supplied or is not a programming language at all - make this true"
    )
