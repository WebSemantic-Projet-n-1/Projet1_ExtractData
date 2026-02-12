from fastapi import FastAPI
from fastapi.responses import FileResponse
from api.api_web_1 import router as api_web_1_0_router
from api.api_rdfa import router as api_rdfa_router
from api.api_knowledge_graph import router as api_knowledge_graph_router

app = FastAPI()

# Root endpoint
@app.get("/")
async def read_root():
    return FileResponse("pages/index.html")

# Search Engine Web 1.0
@app.get("/web-1.0/")
async def v1():
    return FileResponse("pages/searchEngine_web-1.0.html")

# API Web 1.0
app.include_router(api_web_1_0_router)

# Search Engine RDFa
@app.get("/rdfa/")
async def v2():
    return FileResponse("pages/searchEngine_rdfa.html")

# API RDFa
app.include_router(api_rdfa_router)

# Search Engine Knowledge Graph
@app.get("/knowledge-graph/")
async def v3():
    return FileResponse("pages/searchEngine_knowledge-graph.html")

# API Knowledge Graph
app.include_router(api_knowledge_graph_router)