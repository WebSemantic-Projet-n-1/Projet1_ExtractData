from fastapi import FastAPI
from fastapi.responses import FileResponse
from api import router as api_router

app = FastAPI()

# Root endpoint
@app.get("/")
def read_root():
    # Return the search engine page
    return FileResponse("web_1.0_output/searchEngine.html")

app.include_router(api_router)