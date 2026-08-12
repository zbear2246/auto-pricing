from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Literal



    
class OptionsField(BaseModel):
    answers: dict[str,str] = Field(min_length=2)

class TextField(BaseModel):
    question: str
    type: Literal["text"]
    value: str | None
    required: bool

class SingleField(BaseModel):
    question: str
    type: Literal["single"]
    options: OptionsField
    value: str | None
    required: bool
    
class MultiField(BaseModel):
    question: str
    type: Literal["multi"]
    options: OptionsField
    value: list[str]
    required: bool
    




    