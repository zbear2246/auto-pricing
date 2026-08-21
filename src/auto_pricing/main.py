from fastapi import FastAPI, Request
from auto_pricing.models import Form
from src.auto_pricing.sub_functions import (
    AddonCalculator,
    DiscordNotifier,
    EmailComposer,
    EmailSender,
    Error,
    PricingLookup,
    Validator   
)
import json

app = FastAPI()


@app.post("/submit")
def submit(submission: Form):
    error = Error()

    Validator(submission, error=error)
    
    data = error.create_json()
    
    if data["status"] == "error":
        return data
    
    foo = PricingLookup(submission)
    
    return data