from fastapi import FastAPI
from routes.sql_generator import router

app = FastAPI(
    title="SQL Generator Backend",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Text Generator Backend Running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=9000
    )
