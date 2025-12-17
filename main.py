from fastapi import FastAPI
from contextlib import asynccontextmanager
from routes.sql_generator import router
from vector_store import vector_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load Vector Store
    vector_store.load()
    yield

app = FastAPI(
    title="SQL and Text Generator Backend",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "SQL and Text Generator Backend Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=9000
    )   
