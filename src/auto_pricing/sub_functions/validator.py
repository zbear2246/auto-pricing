from auto_pricing.models import Form
from src.auto_pricing.sub_functions import Error
from src.auto_pricing.data import form_schema
from typing import Literal

class Validator:
    def __init__(self, submission: Form, error: Error):
        self.submission: Form = submission
        
        self.error = error
        self.schema_id: dict = {}
        
        self.always_optional = ["deviceModel", "deviceCondition"]
        self.always_required = ["modularAck", "contactName", "contactMethod", "contactPhone", "contactEmail", "deviceType", "deviceBrand", "deviceProduct", "serviceType"]
        
        self.check()
    
    def check(self):
        for field_name in Form.model_fields:
            field = getattr(self.submission, field_name)
            
            field_id = Form.model_fields[field_name].alias
            self.schema_id = form_schema[field_id]
            
            form_type = field.type
            
            match form_type:
                case "multi":
                    self.check_multi(multi=[field, field_id])
                    continue
                case "single":
                    self.check_single(single=[field, field_id])
                    continue
                case "text":
                    self.check_text(text=[field, field_id])
                    continue

                
    def check_always_optional(self, optional: list [Form, str]) -> None:
        field, field_id = optional
        
        value = field.value
        form_type = field.type
        
        if form_type == "text":
            return
        
        
        schema_options = self.schema_id['options']
        
        if not value:
            return
        
        if value not in schema_options:
            self.error.create(field_id, f'{field_id.value} does not contain a valid value')

            
    def check_multi(self, multi: list [Form, str]) -> None:
        field, field_id = multi
        
        value = field.value
        required = field.required
        schema_options = self.schema_id['options']
        
        valid_value = True
        
        for val in value:
            if val not in schema_options:
                valid_value = False 
                        
        if field_id in self.always_optional:
            self.check_always_optional(optional=[field, field_id])
            return
  
        if (field_id in self.always_required) and not (required):
            self.error.create(field_id, f'{field_id.value} are not required when should be')
        
        if required and not value:
            self.error.create(field_id, f"{field_id.value} must be answered")
            
        if not required and value:
            self.error.create(field_id, f"{field_id.value} cannot be ansered")
  
        if not valid_value:
            self.error.create(field_id, f'{field_id.value} does not contain a valid value')
            
        return
    
    def check_single(self, single: list [Form, str]) -> None:
        field, field_id = single
        
        value = field.value
        required = field.required
        schema_options = self.schema_id['options']
        
        if field_id in self.always_optional:
            self.check_always_optional(optional=[field, field_id])
            return
        
        if (field_id in self.always_required) and not (required):
            self.error.create(field_id, f'{field_id.value} is not required when should be')
        
        if required and not value:
            self.error.create(field_id, f"{field_id.value} must be answered")
            
        if not required and value:
            self.error.create(field_id, f"{field_id.value} cannot be ansered")
            
        if value and value not in schema_options:
            self.error.create(field_id, f'{field_id.value} does not contain a valid value')
            
        return

    def check_text(self, text: list [Form, str]) -> None:
        field, field_id = text
        
        value = field.value
        required = field.required
        
        
        if field_id in self.always_optional:
            self.check_always_optional(optional=[field, field_id])
            return
        
        if (field_id in self.always_required) and not (required):
            self.error.create(field_id, f'{field_id.value} is not required when should be')
        
        if required and not value:
            self.error.create(field_id, f"{field_id.value} must be answered")
            
        if not required and value:
            self.error.create(field_id, f"{field_id.value} cannot be ansered")
            
        return