from src.auto_pricing.data import pricing
from src.auto_pricing.sub_functions.addon_calculator import AddonCalculator
from src.auto_pricing.models import Form

class PricingLookup:
    def __init__(self, submission: Form):
        self.prices = pricing
        self.realevent_data = self.create_list_of_realevant_data(submission)
        
        
    def find_biggest(self):
        pass
    
    def create_list_of_realevant_data(self, submission):
        realevant_data: dict = {}
        for field_name in Form.model_fields:
            field = getattr(submission, field_name)
            field_id: str = Form.model_fields[field_name].alias
            
            
            match field_id:
                case "cleaningTier":
                    realevant_data["cleaningTier"] = field.value if field.value == "cleanBasic" else None
                    continue
                
                case "deepCleanType":
                    realevant_data["deepCleanType"] = field.value
                    continue
                
                case "repairPhone":
                    realevant_data["repairPhone"] = field.value
                    continue
                
                case "repairTablet":
                    realevant_data["repairTablet"] = field.value
                    continue
                
                case "repairLaptop":
                    realevant_data["repairLaptop"] = field.value
                    continue
                
                case "repairHomeConsole":
                    realevant_data["repairHomeConsole"] = field.value
                    continue
                
                case "repairHandheld":
                    realevant_data["repairHandheld"] = field.value
                    continue
                
                case "repairController":
                    realevant_data["repairController"] = field.value
                    continue
                
        print(f"here is some realevant data: {realevant_data}")
                
        return realevant_data
            