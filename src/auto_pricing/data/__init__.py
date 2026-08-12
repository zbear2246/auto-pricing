import json

def load_pricing():
    with open("pricing.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    return data



pricing = load_pricing()


__all__ = ["pricing"]