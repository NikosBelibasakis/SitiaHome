from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models.req_and_valid import process_and_validate_requirements


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    prompt: str


@app.post("/search")
def search(request: SearchRequest):
    return process_and_validate_requirements(request.prompt)