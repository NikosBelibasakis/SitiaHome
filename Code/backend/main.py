from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from components.prop_search import search_xe_properties
from components.req_and_valid import (process_and_validate_requirements)
from components.rank_and_rec import select_properties



matching_urls = []
user_requirements = None


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

    global user_requirements
    user_requirements = process_and_validate_requirements(prompt)
    return user_requirements



@app.post("/search-properties")
def search_properties():

    global matching_urls
    matching_urls = search_xe_properties(user_requirements)

    if matching_urls:
        return True 

    return False



@app.post("/select-properties")
async def select_properties_main():

    selected_properties = await select_properties(matching_urls, user_requirements)
    return selected_properties