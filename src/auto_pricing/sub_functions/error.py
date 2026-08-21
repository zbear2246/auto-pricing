from auto_pricing.models import QuestionTypes

class Error:
    def __init__(self):
        self.json: dict
        self.error: dict = {}
    
    def create(self, q_type: QuestionTypes, message:str):
        if self.error.get(q_type.value):
            return
        
        self.error[q_type.value] = message
        
    def purge(self):
        self.error = {}

    def create_json(self):
        self.json = {
            "status": "error" if self.error else "ok",
            "error": self.error
        }
        
        print(self.json)
        
        return self.json