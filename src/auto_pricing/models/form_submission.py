from auto_pricing.models.submission_field import (
    SingleField as single, 
    TextField as text, 
    MultiField as multi)
from pydantic import BaseModel, ConfigDict, Field


class Form(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    
    modularAck: single
    contactName: text
    contactMethod: single
    contactPhone: text
    contactEmail: text
    deviceType: single
    deviceBrand: text
    deviceProduct: text
    deviceModel: text
    deviceCondition: single
    serviceType: multi
    cleaningTier: single
    deepCleanType: single
    repairPhone: multi
    repairTablet: multi
    repairLaptop: multi
    repairHomeConsole: multi
    repairHandheld: multi
    repairController: multi
    
    
    
    
    
    
    
    
    
    
    
    
    
    