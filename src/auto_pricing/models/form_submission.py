from auto_pricing.models.submission_field import (
    QuestionTypes,
    SingleField as single, 
    TextField as text, 
    MultiField as multi)
from pydantic import BaseModel, ConfigDict, Field


class Form(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    modular_ack: single = Field(alias=QuestionTypes.modularAck)
    contact_name: text = Field(alias=QuestionTypes.contactName)
    contact_method: single = Field(alias=QuestionTypes.contactMethod)
    contact_phone: text = Field(alias=QuestionTypes.contactPhone)
    contact_email: text = Field(alias=QuestionTypes.contactEmail)
    device_type: single = Field(alias=QuestionTypes.deviceType)
    device_brand: text = Field(alias=QuestionTypes.deviceBrand)
    device_product: text = Field(alias=QuestionTypes.deviceProduct)
    device_model: text = Field(alias=QuestionTypes.deviceModel)
    device_condition: single = Field(alias=QuestionTypes.deviceCondition)
    service_type: multi = Field(alias=QuestionTypes.serviceType)
    cleaning_tier: single = Field(alias=QuestionTypes.cleaningTier)
    deep_clean_type: single = Field(alias=QuestionTypes.deepCleanType)
    repair_phone: multi = Field(alias=QuestionTypes.repairPhone)
    repair_tablet: multi = Field(alias=QuestionTypes.repairTablet)
    repair_laptop: multi = Field(alias=QuestionTypes.repairLaptop)
    repair_home_console: multi = Field(alias=QuestionTypes.repairHomeConsole)
    repair_handheld: multi = Field(alias=QuestionTypes.repairHandheld)
    repair_controller: multi = Field(alias=QuestionTypes.repairController)
    
    
    
    
    
    
    
    
    
    
    
    
    
    