from fastapi import FastAPI
from fastapi.responses import FileResponse
from api import router as api_router

app = FastAPI()

# Root endpoint
@app.get("/")
async def read_root():
    return FileResponse("pages/index.html")

# Search Engine Web 1.0
@app.get("/web-1.0/")
async def v1():
    return FileResponse("pages/searchEngine_web-1.0.html")

# Search Engine Web 3.0
@app.get("/web-3.0/")
async def v2():
    return FileResponse("pages/searchEngine_web-3.0.html")

app.include_router(api_router)