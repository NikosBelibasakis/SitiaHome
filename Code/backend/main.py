from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from components.prop_search import search_xe_properties
from components.req_and_valid import (process_and_validate_requirements, UserRequirements)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/search")
def search(prompt: str = Body(...)):

    return process_and_validate_requirements(prompt)



@app.post("/search-properties")
def search_properties(requirements: UserRequirements = Body(...)):
    matching_urls = search_xe_properties(requirements)

    if matching_urls:
        return True 

    return False