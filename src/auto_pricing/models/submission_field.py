from pydantic import BaseModel, ConfigDict
from typing import Literal, Annotated
from enum import Enum


class QuestionTypes(str, Enum):
    modularAck = "modularAck"
    contactName = "contactName"
    contactMethod = "contactMethod"
    contactPhone = "contactPhone"
    contactEmail = "contactEmail"
    deviceType = "deviceType"
    deviceBrand = "deviceBrand"
    deviceProduct = "deviceProduct"
    deviceModel = "deviceModel"
    deviceCondition = "deviceCondition"
    serviceType = "serviceType"
    cleaningTier = "cleaningTier"
    deepCleanType = "deepCleanType"
    repairPhone = "repairPhone"
    repairTablet = "repairTablet"
    repairLaptop = "repairLaptop"
    repairHomeConsole = "repairHomeConsole"
    repairHandheld = "repairHandheld"
    repairController = "repairController"

class TextField(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    question: str
    type: Literal["text"]
    value: str | None
    required: bool

class SingleField(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    question: str
    type: Literal["single"]
    value: str | None
    required: bool
    
class MultiField(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    question: str
    type: Literal["multi"]
    value: list[str]
    required: bool