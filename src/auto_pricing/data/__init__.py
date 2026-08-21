import json

def load_pricing() -> dict:
    with open("src/auto_pricing/data/pricing.json", 'r', encoding='utf-8') as f:
        data:dict = json.load(f)
        
    return data

def load_form_schema() -> dict:
    with open("src/auto_pricing/data/form_schema.json", 'r', encoding='utf-8') as f:
        data:dict = json.load(f)
        
    return data

pricing: dict = load_pricing()
form_schema:dict = load_form_schema()

__all__ = ["pricing", 'form_schema']

if __name__ == "__main__":
    form_schema = load_form_schema()
    
    form_id = form_schema['repairLaptop']
    
    form_options = form_id['options']
    
    print(form_options)