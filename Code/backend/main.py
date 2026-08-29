from fastapi import FastAPI
from pydantic import BaseModel

from models.req_and_valid import process_and_validate_requirements


app = FastAPI()


class SearchRequest(BaseModel):
    prompt: str


@app.get("/")
def root():
    return {"message": "SitiaHome API is running"}


@app.post("/search")
def search(request: SearchRequest):
    return process_and_validate_requirements(request.prompt)